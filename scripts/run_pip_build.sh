#!/bin/bash

set -e

cd "$(dirname "$0")/.."
path_repo="$(pwd)"
tmp_venv="/tmp/ansible-webui-venv/$(date +%s)"

echo ''
echo 'Installing requirements'
echo ''

python3 -m pip install -r ./requirements_build.txt >/dev/null

echo ''
echo "Creating virtualenv ${tmp_venv}"
echo ''

python3 -m virtualenv "$tmp_venv" >/dev/null
source "${tmp_venv}/bin/activate"

echo ''
echo 'Building & Installing Module using PIP'
echo ''

python3 -m pip install -e "$path_repo" >/dev/null

echo ''
echo 'Starting app'
echo ''

python3 -m ansible-webui

echo ''
echo "Removing virtualenv ${tmp_venv}"
echo ''

deactivate
rm -rf "$tmp_venv"
