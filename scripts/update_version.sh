#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

last_tag="$(git describe --exact-match --abbrev=0)"
echo "${last_tag}.dev" > "$(dirname "$0")/../VERSION"
