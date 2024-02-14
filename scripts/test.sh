#!/bin/bash

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'UNIT TESTS'
echo ''

python3 -m pytest

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
export AW_ADMIN='ansible'
export AW_ADMIN_PWD='someSecret!Pwd'
python3 src/ansible-webui/ >/dev/null 2>/dev/null &
echo ''
sleep 5

python3 test/integration/webui/main.py

sleep 1

echo ''
echo 'INTEGRATION TESTS API'
echo ''

echo 'Create API key'
api_key="$(python3 src/ansible-webui/cli.py -f api-key -a create -p "$AW_ADMIN" | grep 'Key=' | cut -d '=' -f2)"
export AW_API_KEY="$api_key"
sleep 1

python3 test/integration/api/main.py

sleep 1
pkill -f 'ansible-webui'
