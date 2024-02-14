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

# shellcheck disable=SC2155
export AW_DB="/tmp/$(date +%s).aw.db"
export AW_ADMIN='tester'
export AW_ADMIN_PWD='someSecret!Pwd'
python3 src/ansible-webui/ >/dev/null &
sleep 5

python3 test/integration/webui/main.py

sleep 1

pkill -f 'ansible-webui'
