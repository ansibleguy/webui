#!/usr/bin/env bash

set -e

if [ -z "$1" ]
then
  echo 'YOU NEED TO SUPPLY A VERSION!'
  exit 1
fi

set -u

VERSION="$1"

cd "$(dirname "$0")/../docker"

IMAGE_BASE="ansible0guy/ansible-webui"
image="${IMAGE_BASE}:${VERSION}"
image_latest="${IMAGE_BASE}:latest"
container="ansible-webui-${VERSION}"

read -r -p "Build version ${VERSION} as latest? [y/N] " -n 1

echo ''
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

if [[ "$REPLY" =~ ^[Yy]$ ]]
then
  if docker image ls | grep "$IMAGE_BASE" | grep -q 'latest'
  then
    docker image rm "$image_latest"
  fi
fi

echo ''
echo "### BUILDING IMAGE ${image} ###"
docker build -f Dockerfile_production -t "$image" --build-arg "AW_VERSION=${VERSION}" --no-cache .
if [[ "$REPLY" =~ ^[Yy]$ ]]
then
  docker build -f Dockerfile_production -t "$image_latest" --build-arg "AW_VERSION=${VERSION}" .
fi

echo ''
echo "### STARTING IMAGE ${image} FOR TEST ###"
docker run -it --name "$container" --publish 127.0.0.1:8000:8000 "$image"
