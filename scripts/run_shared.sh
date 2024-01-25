#!/bin/bash

set -e

function log() {
  echo ''
  echo "### $1 ###"
  echo ''
}

cd "$(pwd)/.."
TEST_DB="$(pwd)/src/ansible-webui/aw.${AW_ENV}.db"
TEST_MIGRATE=''

if [ -f "$TEST_DB" ] && [[ "$TEST_QUIET" != "1" ]]
then
  # shellcheck disable=SC2162
  read -p "Delete existing ${AW_ENV} DB? (yes/NO) " del_dev_db

  if [[ "$del_dev_db" == 'y' ]] || [[ "$del_dev_db" == 'yes' ]]
  then
    echo "Removing ${AW_ENV} DB.."
    rm "$TEST_DB"
    TEST_MIGRATE='clean'
  fi
elif ! [ -f "$TEST_DB" ]
then
  echo "Creating DB ${TEST_DB}"
fi

export AW_DB="$TEST_DB"
export DJANGO_SUPERUSER_USERNAME='ansible'
export DJANGO_SUPERUSER_PASSWORD='automateMe'
export DJANGO_SUPERUSER_EMAIL='ansible@localhost'

log 'SETTING VERSION'
bash ./scripts/update_version.sh
version="$(cat './VERSION')"
export AW_VERSION="$version"
path_play="$(pwd)/test"
export AW_PATH_PLAY="$path_play"

if [[ "$TEST_QUIET" != "1" ]]
then
  log 'INSTALLING REQUIREMENTS'
  python3 -m pip install --upgrade -r ./requirements.txt >/dev/null

  log 'INITIALIZING DATABASE SCHEMA'
  bash ./scripts/migrate_db.sh "$TEST_MIGRATE"

  log 'CREATING USERS'
  python3 ./src/ansible-webui/manage.py createsuperuser --noinput || true
fi

log 'STARTING APP'
python3 ./src/ansible-webui
