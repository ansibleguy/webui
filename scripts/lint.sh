#!/bin/bash

set -e

cd "$(dirname "$0")/.."

export AW_INIT=1

echo ''
echo 'LINTING Python'
echo ''

export DJANGO_SETTINGS_MODULE='aw.settings'
pylint --recursive=y --load-plugins pylint_django --django-settings-module=aw.settings .

echo ''
echo 'LINTING YAML'
echo ''

yamllint .

