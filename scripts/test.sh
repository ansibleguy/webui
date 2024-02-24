#!/bin/bash

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'UNIT TESTS'
echo ''

python3 -m pytest

function failure() {
  echo ''
  echo '### FAILED ###'
  echo ''
  pkill -f ansible-webui
  exit 1
}

echo ''
echo 'INTEGRATION TESTS WEB-UI'
echo ''

if pgrep -f 'ansible-webui'
then
  echo 'An instance of Ansible-WebUI is already running! Stop it first (pkill -f ansible-webui)'
  exit 1
fi


echo 'Starting Ansible-WebUI..'
export AW_ENV='dev'
# shellcheck disable=SC2155
export AW_DB="/tmp/$(date +%s).aw.db"
# shellcheck disable=SC2155
export AW_PATH_PLAY="$(pwd)/test"
export AW_ADMIN='tester'
export AW_ADMIN_PWD='someSecret!Pwd'
python3 src/ansibleguy-webui/ >/dev/null 2>/dev/null &
echo ''
sleep 5

set +e
if ! python3 test/integration/webui/main.py
then
  failure
fi

sleep 1

echo ''
echo 'INTEGRATION TESTS API'
echo ''

echo 'Create API key'
api_key="$(python3 src/ansibleguy-webui/cli.py -f api-key -a create -p "$AW_ADMIN" | grep 'Key=' | cut -d '=' -f2)"
export AW_API_KEY="$api_key"
sleep 1

if ! python3 test/integration/api/main.py
then
  failure
fi

sleep 1
pkill -f 'ansible-webui'

echo ''
echo 'TESTING TO INITIALIZE AW-DB'
echo ''

# shellcheck disable=SC2155
TMP_DIR="/tmp/aw_$(date +%s)"
mkdir -p "$TMP_DIR"
cp -r ./* "$TMP_DIR"
cd "$TMP_DIR"
rm -rf ./src/ansibleguy-webui/aw/migrations/*
export AW_DB="${TMP_DIR}/aw.db"
timeout 10 python3 src/ansibleguy-webui
ec="$?"
if [[ "$ec" != "124" ]]
then
  exit 1
fi

echo ''
echo '### FINISHED ###'
echo ''
