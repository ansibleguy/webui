#!/bin/bash

set -e

AW_ADMIN='USER'
AW_ADMIN_PWD='PWD'

echo '### REMOVING EXISTING ###'
if docker ps -a | grep -q ansible-webui
then
  docker stop ansible-webui
  docker rm ansible-webui
fi
if docker image ls | grep -q ansible-webui
then
  docker image rm ansible-webui:latest
fi

echo '### BUILDING LATEST ###'
cd /tmp
rm -rf /tmp/ansible-webui
git clone https://github.com/ansibleguy/ansible-webui.git
cd /tmp/ansible-webui/docker
docker build -f Dockerfile_production -t ansible-webui:latest --build-arg "AW_VERSION=latest" .

echo '### STARTING ###'
docker run -d --restart unless-stopped --name ansible-webui --publish 8000:8000 --volume /var/local/ansible-webui/:/data --volume /var/local/ansible-webui/play/:/play --env AW_ADMIN_PWD="$AW_ADMIN_PWD" --env AW_ADMIN="$AW_ADMIN" ansible-webui
