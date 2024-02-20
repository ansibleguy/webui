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

echo '### CLEANUP ###'
if [ -f /var/local/ansible-webui/aw.db ]
then
  BAK_DIR="/var/local/ansible-webui/$(date +%s)"
  mkdir "$BAK_DIR"
  mv /var/local/ansible-webui/aw.db "${BAK_DIR}/aw.db"
  cp -r /var/local/ansible-webui/migrations "${BAK_DIR}/"
fi

cp /var/local/ansible-webui/aw.db.bak /var/local/ansible-webui/aw.db

rm -f /var/local/ansible-webui/log/*

echo '### BUILDING LATEST ###'
cd /tmp
rm -rf /tmp/ansible-webui
git clone https://github.com/ansibleguy/ansible-webui.git
cd /tmp/ansible-webui/docker
docker build -f Dockerfile_production -t ansible-webui:latest --build-arg "AW_VERSION=latest" --no-cache .

echo '### STARTING ###'
docker run -d --restart unless-stopped --name ansible-webui --publish 8000:8000 --volume /var/local/ansible-webui/:/data --volume /var/local/ansible-webui/play/:/play --volume /var/local/ansible-webui/migrations/:/usr/local/lib/python3.10/site-packages/ansible-webui/aw/migrations --env AW_ADMIN_PWD="$AW_ADMIN_PWD" --env AW_ADMIN="$AW_ADMIN" --env AW_HOSTNAMES=demo.webui.ansibleguy.net --env AW_PROXY=1 ansible-webui:latest