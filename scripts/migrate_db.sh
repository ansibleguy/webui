#!/bin/bash

set -e

cd "$(dirname "$0")/../ansible-webui/"

echo ''
echo 'Creating migrations'
echo ''

python3 manage.py makemigrations

echo ''
echo 'Running migrations'
echo ''

python3 manage.py migrate
