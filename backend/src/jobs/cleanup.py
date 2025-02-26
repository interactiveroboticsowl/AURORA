import os
from time import time

from dotenv import load_dotenv

from kubernetes import client, config

from ..utils.kubernetes import handle_delete_stale_entities

if not os.getenv("KUBERNETES_PORT"):
    load_dotenv(".env.dev")


MAX_CONTAINER_AGE = int(os.getenv("MAX_CONTAINER_AGE") or 0)
assert isinstance(MAX_CONTAINER_AGE, int) and MAX_CONTAINER_AGE > 0

# TODO: search for expired participation custom objects
def cleanup_stale_deployments():
    max_creation_timestamp = time() - MAX_CONTAINER_AGE

    config.load_incluster_config()
    api = client.CustomObjectsApi()

    def list_fn(**kwargs):
        return api.list_cluster_custom_object("example.com", "v1", "participations", **kwargs)
    def del_fn(**kwargs):
        return api.delete_cluster_custom_object("example.com", "v1", "participations", **kwargs)

    handle_delete_stale_entities(
        list_fn,
        del_fn,
        max_creation_timestamp,
        namespace=None
    )    


def cleanup():
    cleanup_stale_deployments()


if __name__ == "__main__":
    cleanup()
