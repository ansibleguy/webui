#!/bin/bash

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'TESTING Python'
echo ''

python3 -m pytest
