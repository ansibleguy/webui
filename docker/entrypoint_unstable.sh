#!/bin/sh

. /entrypoint_requirements.sh

echo 'INSTALLING/UPGRADING latest..'
pip install --upgrade --no-cache-dir "git+https://github.com/ansibleguy/ansible-webui.git@latest" >/dev/null

python3 -m ansible-webui
