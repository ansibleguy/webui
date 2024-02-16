#!/usr/bin/env bash

set -eu

VERSION="$1"
IMAGE_BASE="ansible0guy/ansible-webui"
image="${IMAGE_BASE}:${VERSION}"

if ! docker image ls | grep "$IMAGE_BASE" | grep -q "$VERSION"
then
  echo "Image not found: ${image}"
  exit 1
fi

docker push "$image"
