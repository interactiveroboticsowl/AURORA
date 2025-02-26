import asyncio
import base64
import logging
import os
from datetime import datetime, timezone
from urllib.parse import urlparse

import kopf
from kubernetes import client, config

logging.basicConfig(level=logging.DEBUG)


@kopf.on.create("example.com", "v1", "surveys")
@kopf.on.update("example.com", "v1", "surveys")
async def reconcile_survey(spec, status, name, logger, **kwargs):
    observed_version = status.get("observedVersion", 0)
    build_version = spec["buildVersion"]
    started = spec.get("started", False)
    core_v1 = client.CoreV1Api()
    try:
        core_v1.read_namespace(name)
    except client.rest.ApiException as e:
        if e.status == 404:
            logger.info(f"Creating namespace for survey {name}")
            core_v1.create_namespace(
                client.V1Namespace(metadata=client.V1ObjectMeta(name=name))
            )
            # we do not need role bindings as our simulation-orchestrator role is clusterwide
            # create_role_binding("simulation-orchestrator", name)

    if started:
        if status.get("state") != "Started":
            await update_status(name, {"state": "Started"})
        return

    if build_version > observed_version:
        logger.info(f"New build version detected for survey {name}: {build_version}")

        await update_status(
            name, {"state": "Building", "observedVersion": build_version}
        )

        success = await build_survey(name, spec, name, logger)

        if success:
            await update_status(
                name,
                {
                    "state": "Ready",
                    "lastSuccessfulBuild": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                },
            )
        else:
            await update_status(name, {"state": "Failed"})


def create_kaniko_job(name, spec, namespace):
    logging.info(f"NAMESPACE: {namespace}")
    logging.info(f"Creating Kaniko job for survey: {name}")
    batch_v1 = client.BatchV1Api()

    git_repo = spec["gitRepo"]
    containers = spec["containers"]

    env = []

    git_url = git_repo["url"]
    parsed_url = urlparse(git_url)
    git_url = f"{parsed_url.netloc}{parsed_url.path}"

    if "authSecret" in git_repo:
        core_v1 = client.CoreV1Api()
        git_secret = core_v1.read_namespaced_secret(
            git_repo["authSecret"], namespace="default"
        )

        if (
            "token" in git_secret.data
            and git_secret.data["token"] is not None
            and git_secret.data["token"].strip() != ""
        ):
            token = base64.b64decode(git_secret.data["token"]).decode("utf-8")
            git_url = f"oauth2:{token}@{git_url}"

    kaniko_containers = []

    logging.error(f"GIT URL: {git_url}")
    logging.error(f"git://{git_url}#refs/heads/{git_repo['branch']}")
    head_refs = (
        f"#refs/heads/{git_repo['branch']}"
        if git_repo["branch"] is not None and git_repo["branch"] != ""
        else ""
    )

    for container in containers:
        kaniko_cmd = [
            f"--context=git://{git_url}{head_refs}",
            f"--destination=registry:5000/{name}-{container['name']}:latest",
            f"--dockerfile={container['dockerfile']}",
            "--insecure",
            "--skip-tls-verify",
        ]

        kaniko_containers.append(
            client.V1Container(
                name=f"kaniko-{container['name'].lower()}",
                image="gcr.io/kaniko-project/executor:latest",
                args=kaniko_cmd,
                env=env,
            )
        )

    job_name = f"build-{name.lower()}-{int(datetime.now().timestamp())}"

    job = client.V1Job(
        metadata=client.V1ObjectMeta(name=job_name, labels={"project-name": name}),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    containers=kaniko_containers,
                    restart_policy="Never",
                )
            ),
            ttl_seconds_after_finished=300,
        ),
    )

    return batch_v1.create_namespaced_job(namespace, job)


async def build_survey(name, spec, namespace, logger):
    batch_v1 = client.BatchV1Api()
    logger.info(f"Starting build process for survey {name}")

    build_job = create_kaniko_job(name, spec, namespace)

    while True:
        job = batch_v1.read_namespaced_job(build_job.metadata.name, namespace)
        if job.status.succeeded is not None and job.status.succeeded > 0:
            logger.info(f"Build job {job.metadata.name} succeeded")
            return True
        elif job.status.failed is not None and job.status.failed > 0:
            logger.error(f"Build job {job.metadata.name} failed")
            return False

        logger.info(f"Waiting for build job {job.metadata.name} to complete")
        await asyncio.sleep(10)


async def update_status(name, patch):
    api = client.CustomObjectsApi()
    api.patch_cluster_custom_object(
        group="example.com",
        version="v1",
        plural="surveys",
        name=name,
        body={"status": patch},
    )


if __name__ == "__main__":
    if os.getenv("KUBERNETES_PORT"):
        config.load_incluster_config()
    else:
        config.load_kube_config()
    kopf.run()
