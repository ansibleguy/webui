#!/bin/sh

if ! [ -d '/aw' ]
then
  echo 'YOU HAVE TO MOUNT THE APP SOURCES AT /aw'
  exit 1
fi

echo 'INSTALLING/UPGRADING REQUIREMENTS..'
pip install --upgrade -r /aw/requirements.txt --root-user-action=ignore --no-warn-script-location >/dev/null

. /entrypoint_requirements.sh

python3 /aw/src/ansibleguy-webui/
