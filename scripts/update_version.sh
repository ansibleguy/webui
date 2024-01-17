#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

#last_tag="$(git describe --exact-match --abbrev=0)"
last_tag="0.0.1"
echo "${last_tag}.dev" > "$(dirname "$0")/../VERSION"
