import asyncio
import logging
import os
from typing import Dict, Tuple

import kopf
import yaml
from jinja2 import Template
from kubernetes import client, config

logging.basicConfig(level=logging.INFO)


def load_yaml_template(filename, template_dir="templates"):
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), template_dir)
    with open(os.path.join(path, filename), "r") as file:
        return file.read()


DEPLOYMENT_TEMPLATE = Template(load_yaml_template("deployment-template.k8s.yaml"))
SERVICE_TEMPLATE = Template(load_yaml_template("service-template.k8s.yaml"))
INGRESS_TEMPLATE = Template(load_yaml_template("ingress-template.k8s.yaml"))


DOAMIN = os.getenv("DOMAIN")
SSL_ENABLED = os.getenv("SSL_ENABLED") == "true"
SSL_ISSUER = os.getenv("SSL_ISSUER")
MINIO_USER = os.getenv("MINIO_USER")
MINIO_PASSWORD = os.getenv("MINIO_PASSWORD")


def get_survey(name):
    api = client.CustomObjectsApi()
    return api.get_cluster_custom_object(
        group="example.com", version="v1", plural="surveys", name=f"project-{name}"
    )


def get_rosbag_config(ros_version, topics):
    # TODO: Implement the logic to get the ros image from the uploaded container
    if ros_version == "1":
        image = "ros:noetic"
        cmd = (
            f"source /opt/ros/noetic/setup.bash && "
            f"rosbag record -O /data/simulation.bag {' '.join(topics) if topics else '-a'} __name:=rosbag_recorder"
        )
        stop_cmd = "source /opt/ros/noetic/setup.bash && rosnode kill /rosbag_recorder"
    elif ros_version == "2":
        image = "ros:humble"
        # ros2 does not compress bags to one file..
        cmd = (
            f"source /opt/ros/humble/setup.bash && "
            f"ros2 bag record -o /data/simulation.bag {' '.join(topics) if topics else '-a'}"
        )
        stop_cmd = ""
    else:
        raise ValueError(f"Unsupported ROS version: {ros_version}")
    return image, cmd, stop_cmd


@kopf.on.create("example.com", "v1", "participations")
def create_participation(spec, name, patch, **kwargs):
    logging.info(f"Creating participation {name} with spec: {spec}")
    api = client.CoreV1Api()
    apps_api = client.AppsV1Api()
    networking_v1_api = client.NetworkingV1Api()

    survey = get_survey(spec["surveyName"])

    user_ns = f"user-{spec["userId"]}"
    try:
        api.create_namespace(
            client.V1Namespace(metadata=client.V1ObjectMeta(name=user_ns))
        )
    except client.rest.ApiException as e:
        if e.status != 409:
            raise

    containers = ""
    container_service_ports: Dict[str, Tuple[int, int]] = {}

    # TODO: configurable resource requests/limits
    for container_spec in survey["spec"]["containers"]:
        containers += f"""
        - name: {container_spec["name"]}
          image: registry:5000/{survey['metadata']['name']}-{container_spec['name']}:latest
          resources:
            limits:
              cpu: 2.0
              memory: 2048Mi
            requests:
              cpu: 1.5
              memory: 1536Mi
          env:
            - name: USER_ID
              value: \"{spec['userId']}\"
          ports:"""
        for port in container_spec.get("ports", []):
            containers += f"""
            - containerPort: {port['containerPort']}"""

            container_service_ports[container_spec["name"]] = (
                port["servicePort"],
                port["containerPort"],
            )

    pvc = client.V1PersistentVolumeClaim(
        metadata=client.V1ObjectMeta(name=f"{name}-data", namespace=user_ns),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteOnce"],
            resources=client.V1ResourceRequirements(requests={"storage": "5Gi"}),
        ),
    )
    try:
        api.create_namespaced_persistent_volume_claim(namespace=user_ns, body=pvc)
    except client.ApiException as e:
        if e.status != 409:
            raise e

        logging.warning(
            f"Volume {name}-data already exists in namespace {user_ns}, reusing!"
        )

    ros_version = survey["spec"]["rosVersion"]
    rosbag_topics = survey["spec"].get("rosbagTopics", [])
    rosbag_image, rosbag_cmd, rosbag_stop_cmd = get_rosbag_config(
        ros_version, rosbag_topics
    )

    deployment_yaml = DEPLOYMENT_TEMPLATE.render(
        name=name,
        namespace=user_ns,
        containers=containers,
        rosbag_image=rosbag_image,
        rosbag_cmd=rosbag_cmd,
        stop_command=rosbag_stop_cmd,
    )
    deployment = yaml.safe_load(deployment_yaml)
    apps_api.create_namespaced_deployment(namespace=user_ns, body=deployment)

    for container_name, (port, target_port) in container_service_ports.items():
        # skip containers without service ports
        if port is None:
            continue

        service_ports = f"""
    - protocol: TCP
      port: {port}
      targetPort: {target_port}"""

        service_name = f"service-{name}-{container_name}"  # name must start with alphabetic character
        service_yaml = SERVICE_TEMPLATE.render(
            name=service_name,
            deployment_name=name,
            namespace=user_ns,
            ports=service_ports,
        )
        service = yaml.safe_load(service_yaml)
        api.create_namespaced_service(namespace=user_ns, body=service)
        host = f"{spec['userId']}{container_name}{target_port}.{DOAMIN}"
        tls = f"""  tls:
    - secretName: tls-secret
      hosts:
        - {host}
"""
        redirect = "    traefik.ingress.kubernetes.io/router.middlewares: default-redirect-https@kubernetescrd"

        ingress_yaml = INGRESS_TEMPLATE.render(
            name=f"ingress-{name}-{container_name}-{target_port}",
            namespace=user_ns,
            host=host,
            serviceName=service_name,
            servicePort=port,
            tls=tls if SSL_ENABLED else "",
            annotations=redirect if SSL_ENABLED else "",
        )
        ingress = yaml.safe_load(ingress_yaml)
        networking_v1_api.create_namespaced_ingress(namespace=user_ns, body=ingress)

    patch["status"] = {"phase": "Running", "rosbagFile": "simulation.bag"}


def create_minio_upload_job(name, namespace, survey_name, rosbag_file):
    batch_v1 = client.BatchV1Api()

    job = client.V1Job(
        metadata=client.V1ObjectMeta(name=f"{name}-minio-upload", namespace=namespace),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="minio-upload",
                            image="minio/mc:latest",
                            command=["/bin/sh", "-c"],                            
                            args=[
                                f"mc alias set myminio https://myminio-hl.minio-tenant.svc.cluster.local:9000 {MINIO_USER} {MINIO_PASSWORD} && "
                                f"mc mirror /data/{rosbag_file} myminio/rosbags/{survey_name}/{namespace}/{rosbag_file}"
                            ],
                            env=[],
                            volume_mounts=[
                                client.V1VolumeMount(name="data", mount_path="/data")
                            ],
                        )
                    ],
                    restart_policy="Never",
                    volumes=[
                        client.V1Volume(
                            name="data",
                            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                claim_name=f"{name}-data"
                            ),
                        )
                    ],
                )
            )
        ),
    )

    return batch_v1.create_namespaced_job(namespace=namespace, body=job)


@kopf.on.delete("example.com", "v1", "participations")
async def cleanup_simulation(spec, name, namespace, logger, status, **kwargs):
    user_ns = f"user-{spec["userId"]}"
    api = client.CoreV1Api()
    apps_api = client.AppsV1Api()
    batch_v1 = client.BatchV1Api()
    networking_v1_api = client.NetworkingV1Api()

    if status is None:
        logging.warning("no status on deleted object, abort cleanup")
        return

    rosbag_file = status["rosbagFile"]
    apps_api.delete_namespaced_deployment(namespace=user_ns, name=name)

    job = create_minio_upload_job(name, user_ns, spec["surveyName"], rosbag_file)

    while True:
        job = batch_v1.read_namespaced_job(job.metadata.name, namespace)
        if job.status.succeeded is not None and job.status.succeeded > 0:
            logger.info(f"Copy rosbag job {job.metadata.name} succeeded")
            break
        elif job.status.failed is not None and job.status.failed > 0:
            logger.error(f"Copy rosbag job {job.metadata.name} failed")
            return False

        logger.info(f"Waiting for copy rosbag job {job.metadata.name} to complete")
        await asyncio.sleep(10)    

    def check_delete_resource(entity, namespace, delete_fn):
        if hasattr(entity, "metadata") and hasattr(entity.metadata, "name"):
            if name in entity.metadata.name:
                delete_fn(name=entity.metadata.name, namespace=namespace)

    services = api.list_namespaced_service(namespace=user_ns)
    for service in services.items:
        check_delete_resource(service, user_ns, api.delete_namespaced_service)

    ingress_rules = networking_v1_api.list_namespaced_ingress(namespace=user_ns)
    for ingress in ingress_rules.items:
        check_delete_resource(
            ingress, user_ns, networking_v1_api.delete_namespaced_ingress
        )

    api.delete_namespaced_persistent_volume_claim(
        name=f"{name}-data", namespace=user_ns
    )
    api.delete_namespace(name=user_ns)


if __name__ == "__main__":
    if os.getenv("KUBERNETES_PORT"):
        config.load_incluster_config()
    else:
        config.load_kube_config()
    logging.info("Starting simulation orchestrator")
    kopf.run()
