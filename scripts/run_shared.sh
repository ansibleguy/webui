#!/bin/bash

set -e

function log() {
  echo ''
  echo "### $1 ###"
  echo ''
}

cd "$(pwd)/../ansible-webui"
TEST_DB="$(pwd)/aw.${AW_ENV}.db"
TEST_MIGRATE=''

if [ -f "$TEST_DB" ]
then
  # shellcheck disable=SC2162
  read -p "Delete existing ${AW_ENV} DB? (yes/NO) " del_dev_db

  if [[ "$del_dev_db" == 'y' ]] || [[ "$del_dev_db" == 'yes' ]]
  then
    echo "Removing ${AW_ENV} DB.."
    rm "$TEST_DB"
    TEST_MIGRATE='clean'
  fi
else
  echo "Creating DB ${TEST_DB}"
fi

export DJANGO_SUPERUSER_USERNAME='ansible'
export DJANGO_SUPERUSER_PASSWORD='automateMe'
export DJANGO_SUPERUSER_EMAIL='ansible@localhost'

log 'INSTALLING REQUIREMENTS'
python3 -m pip install --upgrade -r ../requirements.txt >/dev/null

log 'INITIALIZING DATABASE SCHEMA'
bash ../scripts/migrate_db.sh "$TEST_MIGRATE"

log 'CREATING USERS'
python3 manage.py createsuperuser --noinput || true

log 'STARTING APP'
python3 __init__.py
