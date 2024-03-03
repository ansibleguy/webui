#!/bin/bash

set -e

AW_ADMIN='USER'
AW_ADMIN_PWD='PWD'
DIR_DATA='/var/local/ansible-webui/'
DIR_PLAY="${DIR_DATA}play/"
DIR_LOG="${DIR_DATA}log/"
AW_USER='ansible-webui'
IMAGE='ansible0guy/webui-unprivileged:latest'

# useradd $AW_USER --shell /usr/sbin/nologin --uid 8785 --user-group

echo '### REMOVING EXISTING ###'
if docker ps -a | grep -q ansible-webui
then
  docker stop ansible-webui
  docker rm ansible-webui
fi

echo '### CLEANUP ###'
if [ -f /var/local/ansible-webui/aw.db ]
then
  BAK_DIR="/var/local/ansible-webui/$(date +%s)"
  mkdir "$BAK_DIR"
  mv /var/local/ansible-webui/aw.db "${BAK_DIR}/aw.db"
fi

cp "${DIR_DATA}/aw.db.bak" "${DIR_DATA}/aw.db"
chown "$AW_USER" "$DIR_DATA" "${DIR_DATA}/aw.db"
chown -R "$AW_USER" "$DIR_LOG"
chown -R root:"$AW_USER" "$DIR_PLAY"

# rm -f /var/local/ansible-webui/log/*

echo '### UPDATING ###'
docker pull "$IMAGE"

echo '### STARTING ###'
docker run -d --restart unless-stopped --name ansible-webui --publish 8000:8000 --volume "$DIR_DATA":/data --volume "$DIR_PLAY":/play --env AW_ADMIN_PWD="$AW_ADMIN_PWD" --env AW_ADMIN="$AW_ADMIN" --env AW_HOSTNAMES=demo.webui.ansibleguy.net --env AW_PROXY=1 "$IMAGE"
