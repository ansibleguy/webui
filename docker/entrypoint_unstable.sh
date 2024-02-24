#!/bin/sh

. /entrypoint_requirements.sh

echo 'INSTALLING/UPGRADING latest..'
pip install --no-warn-script-location --upgrade --no-cache-dir "git+https://github.com/ansibleguy/webui.git@latest" >/dev/null

python3 -m ansible-webui
