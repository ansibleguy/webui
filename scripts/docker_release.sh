#!/usr/bin/env bash

set -e

if [ -z "$1" ]
then
  echo 'YOU NEED TO SUPPLY A VERSION!'
  exit 1
fi

set -u

VERSION="$1"
IMAGE_REPO="ansible0guy/webui"
IMAGE_REPO_UNPRIV="${IMAGE_REPO}-unprivileged"
IMAGE_REPO_AWS="${IMAGE_REPO}-aws"

image="${IMAGE_REPO}:${VERSION}"
image_latest="${IMAGE_REPO}:latest"

image_unpriv="${IMAGE_REPO_UNPRIV}:${VERSION}"
image_unpriv_latest="${IMAGE_REPO_UNPRIV}:latest"

image_aws="${IMAGE_REPO_AWS}:${VERSION}"
image_aws_latest="${IMAGE_REPO_AWS}:latest"

if ! docker image ls | grep "$IMAGE_REPO" | grep -q "$VERSION"
then
  echo "Image not found: ${image}"
  exit 1
fi

echo ''
echo "### RELEASING IMAGES WITH TAG ${VERSION} ###"
docker push "$image"
docker push "$image_unpriv"
docker push "$image_aws"

echo ''
read -r -p "Release version ${VERSION} as latest? [y/N] " -n 1
if [[ "$REPLY" =~ ^[Yy]$ ]]
then
  if ! docker image ls | grep "$IMAGE_REPO" | grep -q 'latest'
  then
    echo "Image not found: ${image_latest}"
    exit 1
  fi

  echo ''
  echo "### RELEASING IMAGES WITH TAG latest ###"
  docker push "$image_latest"
  docker push "$image_unpriv_latest"
  docker push "$image_aws_latest"
fi
