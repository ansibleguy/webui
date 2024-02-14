#!/bin/sh

if ! [ -d '/aw' ]
then
  echo 'YOU HAVE TO MOUNT THE APP SOURCES AT /aw'
  exit 1
fi

echo 'INSTALLING/UPGRADING REQUIREMENTS..'
pip install --upgrade -r /aw/requirements.txt >/dev/null

. /entrypoint_requirements.sh

python3 /aw/src/ansible-webui/
