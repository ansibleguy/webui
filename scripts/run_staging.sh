#!/bin/bash

set -e

cd "$(dirname "$0")"
export AW_ENV='staging'
source ./run_shared.sh
