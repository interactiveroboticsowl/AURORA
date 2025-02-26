#!/bin/bash
set -e

check_executable() {
    if ! command -v $1 &> /dev/null
    then
        echo "required program '$1' could not be found"
        exit 1
    fi
}

check_executable k3d
check_executable docker
check_executable helm

echo "Creating Cluster.."

set +e
mkdir $HOME/.survey-platform-db

k3d cluster create -c ./config/k3d/k3d-config.yaml
set -e

sh ./build.sh

echo "Install minio"

helm repo add minio-operator https://operator.min.io
helm install --namespace minio-operator --create-namespace operator minio-operator/operator
helm install --namespace minio-tenant --create-namespace --values ./config/minio/minio-values.yaml minio minio-operator/tenant
