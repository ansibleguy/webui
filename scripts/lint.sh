#!/bin/bash

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'LINTING Python'
echo ''

pylint --recursive=y --load-plugins pylint_django --django-settings-module=aw.settings .

echo ''
echo 'LINTING YAML'
echo ''

yamllint .

