import base64
import logging
import os

from kubernetes import client, config
from sqlalchemy import event
from sqlalchemy.orm import Session, object_session

from .data import models

if os.getenv("KUBERNETES_PORT"):
    config.load_incluster_config()
else:
    config.load_kube_config()

api_client = client.ApiClient()
custom_api = client.CustomObjectsApi(api_client)
v1 = client.CoreV1Api()


# TODO: use survey template
# SURVEY_TEMPLATE = Template(load_yaml_template("survey.yaml"))
# containers = ""
# for container in container_descriptions:
#     containers += f"""
# - name: {container["name"]}
#   dockerfile: {container["dockerfile"]}
#   ports:"""

#     for port, service_port in container["ports"]:
#         containers += f"""
#     - containerPort: {port}"""

#         if service_port is not None:
#             containers += f"""
#       servicePort: {service_port}"""


# survey_yaml = SURVEY_TEMPLATE.render(
#     name=name,
#     buildVersion=1,
#     started="false",
#     repoUrl=repo_url,
#     repoBranch=repo_branch,
#     authSecretName=git_secret_name,
#     rosVersion=ros_version,
#     resbagTopics=rosbag_topics,
#     containers=containers,
# )
# logging.warning(survey_yaml)
# survey_obj = yaml.safe_load(survey_yaml)
# # might automatically cast to int
# survey_obj["spec"]["rosVersion"] = str(survey_obj["spec"]["rosVersion"])
def update_kubernetes_crd(project: models.Project):
    if not project.application.repo or not project.application.containers:
        logging.info(
            f"Skipping CRD creation for project {project.name}: Missing repo or containers"
        )
        return

    crd_data = {
        "apiVersion": "example.com/v1",
        "kind": "Survey",
        "metadata": {"name": f"project-{project.name.lower()}"},
        "spec": {
            "buildVersion": project.application.build_version,
            "gitRepo": {
                "url": project.application.repo.git_url,
                "branch": project.application.repo.git_branch,
                "authSecret": f"repo-{project.application.repo.id}-access-token",
            },
            "containers": [
                {
                    "name": container.name,
                    "dockerfile": container.dockerfile,
                    "ports": [
                        {
                            "containerPort": port_map.internal_port,
                            "servicePort": port_map.external_port,
                        }
                        for port_map in container.ports
                    ],
                }
                for container in project.application.containers
            ],
            "rosVersion": project.application.ros_version,
            "rosbagTopics": [topic.topic for topic in project.application.log_topics],
        },
    }

    try:
        custom_api.patch_cluster_custom_object(
            group="example.com",
            version="v1",
            plural="surveys",
            name=f"project-{project.name.lower()}",
            body=crd_data,
        )
        logging.info(f"Updated CRD for project {project.name}")
    except client.ApiException as e:
        if e.status == 404:
            custom_api.create_cluster_custom_object(
                group="example.com",
                version="v1",
                plural="surveys",
                body=crd_data,
            )
            logging.info(f"Created new CRD for project {project.name}")
        else:
            logging.error(
                f"Error updating/creating CRD for project {project.name}: {str(e)}"
            )
            raise


def update_kubernetes_secret(repo: models.Repo):
    secret_name = f"repo-{repo.id}-access-token"
    namespace = "default"
    secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name=secret_name),
        type="Opaque",
        data={
            "token": base64.b64encode(repo.access_token.encode("utf-8")).decode("utf-8")
        },
    )

    try:
        v1.read_namespaced_secret(name=secret_name, namespace=namespace)
        # Secret exists, update it
        v1.patch_namespaced_secret(name=secret_name, namespace=namespace, body=secret)
        logging.info(f"Updated Secret {secret_name} for repo {repo.id}")
    except client.ApiException as e:
        if e.status == 404:
            # Secret doesn't exist, create it
            v1.create_namespaced_secret(namespace=namespace, body=secret)
            logging.info(f"Created new Secret {secret_name} for repo {repo.id}")
        else:
            logging.error(
                f"Error updating/creating Secret for repo {repo.id}: {str(e)}"
            )
            raise


@event.listens_for(models.Repo.access_token, "set")
def receive_set(target, value, oldvalue, initiator):
    session = object_session(target)
    if session:
        update_kubernetes_secret(target)


@event.listens_for(models.Project, "after_update")
@event.listens_for(models.Application, "after_update")
@event.listens_for(models.Repo, "after_update")
@event.listens_for(models.Container, "after_update")
@event.listens_for(models.PortMap, "after_update")
@event.listens_for(models.LogTopic, "after_update")
def receive_after_update(mapper, connection, target):
    session = Session(bind=connection)
    project = None
    if isinstance(target, models.Project):
        project = target
    elif isinstance(target, models.Application):
        project = target.project
    elif isinstance(target, models.Repo):
        project = target.application.project
    elif isinstance(target, models.Container):
        project = target.application.project
    elif isinstance(target, models.LogTopic):
        project = target.application.project

    if project:
        update_kubernetes_crd(project)
    session.close()


@event.listens_for(models.Application, "after_insert")
@event.listens_for(models.Repo, "after_insert")
@event.listens_for(models.Container, "after_insert")
@event.listens_for(models.PortMap, "after_insert")
@event.listens_for(models.LogTopic, "after_insert")
def receive_after_insert(mapper, connection, target):
    if isinstance(target, models.Repo):
        update_kubernetes_secret(target)
    receive_after_update(mapper, connection, target)


@event.listens_for(models.Project, "after_delete")
@event.listens_for(models.Application, "after_delete")
@event.listens_for(models.Repo, "after_delete")
@event.listens_for(models.Container, "after_delete")
@event.listens_for(models.PortMap, "after_delete")
@event.listens_for(models.LogTopic, "after_delete")
def receive_after_delete(mapper, connection, target):
    receive_after_update(mapper, connection, target)
