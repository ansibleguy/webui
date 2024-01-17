#!/bin/bash

set -e

cd "$(dirname "$0")/.."
rm -rf dist/*

python3 -m pip install -r ./requirements_build.txt >/dev/null
python3 -m build
# python3 -m twine upload --repository pypi dist/*
