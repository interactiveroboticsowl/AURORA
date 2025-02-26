#!/bin/bash
set -e

build_and_push() {
    (cd $1 && docker build -f $2 -t $3 .)
    docker push $3
}

echo "Building and pushing backend docker images"

build_and_push ./backend Dockerfile localhost:5000/survey-platform-backend:latest
build_and_push ./backend Dockerfile.cleanup localhost:5000/cleanup-job:latest

echo "Building and pushing frontend docker images"

build_and_push ./frontend Dockerfile localhost:5000/survey-platform-frontend:latest

echo "Building and pushing operator docker images"

build_and_push ./survey-operator survey.Dockerfile localhost:5000/survey-controller:latest
build_and_push ./survey-operator simulation.Dockerfile localhost:5000/simulation-orchestrator:latest