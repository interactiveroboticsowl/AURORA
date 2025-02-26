import logging
import os
from typing import Any, Protocol
from datetime import datetime

import yaml
from git import Optional
from jinja2 import Template
from kubernetes import client, config
from kubernetes.client import ApiValueError, OpenApiException
from kubernetes.client.models import (
    V1CustomResourceDefinition,
    V1Deployment,
    V1Ingress,
    V1Service,
)

logging.basicConfig(level=logging.INFO)

if os.getenv("KUBERNETES_PORT"):
    config.load_incluster_config()
else:
    config.load_kube_config()


def get_application_status(application_name: str, namespace: str):
    api_instance = client.CustomObjectsApi()
    try:
        application = api_instance.get_namespaced_custom_object(
            group="example.com",
            version="v1",
            namespace=namespace,
            plural="surveys",
            name=application_name,
        )

        status = application.get("status", {})
        return status.get("state", "Unknown")
    except client.rest.ApiException as e:
        if e.status == 404:
            logging.error(
                f"Application {application_name} not found in namespace {namespace}"
            )
            return "Application not created yet"
        return "Error fetching application status"


def load_yaml_template(filename, template_dir="templates"):
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", template_dir)
    with open(os.path.join(path, filename), "r") as file:
        return file.read()


PARTICIPATION_TEMPLATE = Template(load_yaml_template("participation.yaml"))


class DeleteFnProtocol(Protocol):
    def __call__(self, name: str, namespace: Optional[str] = "default") -> Any: ...


class ListFnProtocol(Protocol):
    def __call__(
        self,
        label_selector: str,
        limit: Optional[int] = None,
        namespace: Optional[str] = "default",
    ) -> Any: ...


def handle_delete_stale_entities(
    list_entities_fn: ListFnProtocol,
    delete_entity_fn: DeleteFnProtocol,
    max_creation_timestamp: int,
    namespace: Optional[str] = "default",
):
    # list_args = {"limit": 50, "label_selector": "type=userdeployment"}
    list_args = {"limit": 50}
    if namespace is not None:
        list_args["namespace"] = namespace
    entities = list_entities_fn(**list_args)
    logging.warning(entities)
    sorted_entities = sorted(
        entities["items"], key=lambda x: -datetime.fromisoformat(x["metadata"]["creationTimestamp"]).timestamp()
    )

    for entity in sorted_entities:
        logging.info(
            f"entity creation timestamp: {datetime.fromisoformat(entity["metadata"]["creationTimestamp"]).timestamp()}"
        )
        if datetime.fromisoformat(entity["metadata"]["creationTimestamp"]).timestamp() > max_creation_timestamp:
            break

        handle_delete_entity(entity, delete_entity_fn, namespace)


def handle_delete_entity(
    entity: V1Deployment | V1Service | V1Ingress | V1CustomResourceDefinition,
    delete_namespaced_fn: DeleteFnProtocol,
    namespace: Optional[str] = "default",
):
    assert entity["metadata"] is not None

    delete_args = {"name": entity["metadata"]["name"]}
    if namespace is not None:
        delete_args["namespace"] = namespace

    try:
        delete_namespaced_fn(**delete_args)
        logging.info(f"Initiated delete of {entity["metadata"]["name"]}")
        return True
    except OpenApiException as e:
        logging.error(f"Exception during delete of {entity["metadata"]["name"]}: {e}")
    return True


async def cleanup_participation(user_id: str, survey_name: str):
    if user_id is None or survey_name is None or user_id == "" or survey_name == "":
        return False  # TODO: handle error case

    api = client.CustomObjectsApi()

    try:
        participation_obj = api.get_cluster_custom_object(
            "example.com", "v1", "participations", f"{user_id}-{survey_name}"
        )
    except OpenApiException as e:
        logging.error(e)
        return False

    if participation_obj is None:
        logging.warning(
            f"participation of user {user_id} for survey {survey_name} not found"
        )
        return False

    try:
        api.delete_cluster_custom_object(
            "example.com", "v1", "participations", f"{user_id}-{survey_name}"
        )
    except OpenApiException as e:
        logging.error(f"error deleting participation customobject: {e}")
        return False

    return True


async def create_user_participation_object(survey_name: str, user_id: str):
    api = client.CustomObjectsApi()

    participation_yaml = PARTICIPATION_TEMPLATE.render(
        surveyName=survey_name, userID=user_id
    )
    logging.info(participation_yaml)
    participation_obj = yaml.safe_load(participation_yaml)
    participation_obj["spec"]["userId"] = str(participation_obj["spec"]["userId"])
    logging.info(participation_obj)
    try:
        api.get_cluster_custom_object(
            group="example.com",
            version="v1",
            plural="participations",
            name=f"{user_id}-{survey_name.lower()}",
        )
        logging.info(f"Survey {survey_name} for user {user_id} already exists")
        return True
    except client.ApiException as e:
        if e.status != 404:
            logging.error(f"Error fetching survey: {e}")
            return False

    try:

        api.create_cluster_custom_object(
            group="example.com",
            version="v1",
            plural="participations",
            body=participation_obj,
        )
    except ApiValueError as e:
        logging.error(
            f"Invalid parameters for call to create_cluster_custom_object: {e}"
        )
        return False

    return True
