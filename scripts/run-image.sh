#!/usr/bin/env bash
# Public invocation recipe, also used by behavioral checks.
set -euo pipefail
image=${1:?Usage: run-image.sh IMAGE [COMMAND...]}
shift
workspace=${WORKSPACE:-$PWD}
cache=${CACHE_VOLUME:-image-library-cache}
if [ "$#" = 0 ]; then set -- bash; fi
docker run --rm --init \
  --mount "type=bind,src=$workspace,dst=/workspace" \
  --mount "type=volume,src=$cache,dst=/home/dev" \
  -e PUID="$(id -u)" -e PGID="$(id -g)" \
  -e HTTP_PROXY -e HTTPS_PROXY -e NO_PROXY \
  "$image" "$@"
