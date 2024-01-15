#!/bin/bash

set -e

cd "$(dirname "$0")"
export AW_DEV=1
export AW_ENV='dev'
export AW_SECRET='asdfThisIsSuperSecret!'  # keep sessions on auto-reload
source ./run_shared.sh
