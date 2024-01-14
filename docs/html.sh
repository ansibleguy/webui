#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"

rm -rf build
mkdir build

sphinx-build -b html source/ build/
