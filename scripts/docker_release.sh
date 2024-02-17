#!/usr/bin/env bash

set -e

if [ -z "$1" ]
then
  echo 'YOU NEED TO SUPPLY A VERSION!'
  exit 1
fi

set -u

VERSION="$1"
IMAGE_BASE="ansible0guy/ansible-webui"
image="${IMAGE_BASE}:${VERSION}"
image_latest="${IMAGE_BASE}:latest"

if ! docker image ls | grep "$IMAGE_BASE" | grep -q "$VERSION"
then
  echo "Image not found: ${image}"
  exit 1
fi

echo ''
echo "### RELEASING IMAGE ${image} ###"
docker push "$image"

echo ''
read -r -p "Release version ${VERSION} as latest? [y/N] " -n 1
if [[ "$REPLY" =~ ^[Yy]$ ]]
then
  if ! docker image ls | grep "$IMAGE_BASE" | grep -q 'latest'
  then
    echo "Image not found: ${image_latest}"
    exit 1
  fi

  echo ''
  echo "### RELEASING IMAGE ${image_latest} ###"
  docker push "$image_latest"
fi
