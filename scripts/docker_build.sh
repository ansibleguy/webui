#!/usr/bin/env bash

set -eu

VERSION="$1"

cd "$(dirname "$0")/../docker"

IMAGE_BASE="ansible0guy/ansible-webui"
image="${IMAGE_BASE}:${VERSION}"
container="ansible-webui-${VERSION}"

echo "### CLEANUP ###"
if docker ps -a | grep -q "$container"
then
  docker stop "$container"
  docker rm "$container"
fi

if docker image ls | grep "$IMAGE_BASE" | grep -q "$VERSION"
then
  docker image rm "$image"
fi

echo "### BUILDING IMAGE ${image} ###"
docker build -f Dockerfile_production -t "$image" --build-arg "AW_VERSION=${VERSION}" --no-cache .

echo "### STARTING IMAGE ${image} FOR TEST ###"
docker run -it --name "$container" --publish 127.0.0.1:8000:8000 "$image"
