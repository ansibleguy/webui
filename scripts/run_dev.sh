#!/bin/bash

set -e

export TEST_QUIET=0
if [[ -n "$1" ]] && [[ "$1" == "q" ]]
then
  export TEST_QUIET=1
fi

cd "$(dirname "$0")"
export AW_DEV=1
export AW_ENV='dev'
export AW_SECRET='asdfThisIsSuperSecret!'  # keep sessions on auto-reload
source ./run_shared.sh
