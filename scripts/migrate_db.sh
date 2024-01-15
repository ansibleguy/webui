#!/bin/bash

set -e

CLEAN=0
if [ -n "$1" ] && [[ "$1" == "clean" ]]
then
  CLEAN=1
fi

cd "$(dirname "$0")/.."

echo ''
echo 'Removing temporary migrations'
echo ''

if [[ "$CLEAN" == "1" ]]
then
  git ls-files . --exclude-standard --others | grep 'migrations' | xargs --no-run-if-empty rm
fi

cd "$(pwd)/ansible-webui/"

echo ''
echo 'Creating migrations'
echo ''

python3 manage.py makemigrations
python3 manage.py makemigrations aw

echo ''
echo 'Running migrations'
echo ''

python3 manage.py migrate
