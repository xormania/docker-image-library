#!/usr/bin/env bash
# Runs the public readiness recipe on a disposable real consuming project.
set -euo pipefail
line=${1:?Usage: verify-image.sh LINE_ID IMAGE}
image=${2:?Supply image reference}
root=$(cd "$(dirname "$0")/.." && pwd)
family=${line%%/*}
kind=${family%-dev}
[[ "$family" != php-browser ]] || kind=php
work=$(mktemp -d)
project="image-check-${RANDOM}-${RANDOM}"
cp -a "$root/tests/fixtures/$kind/." "$work/"
cp "$root/tests/fixtures/native-check.c" "$work/"
export IMAGE="$image" WORKSPACE="$work" PUID PGID
PUID=$(id -u); PGID=$(id -g)
compose=(docker compose -p "$project" -f "$root/examples/php/compose.yaml")
cleanup() { "${compose[@]}" down --volumes --remove-orphans >/dev/null 2>&1 || true; docker volume rm "$project-cache" >/dev/null 2>&1 || true; rm -rf "$work"; }
trap cleanup EXIT
start=$SECONDS
if [[ "$kind" = php || "$kind" = python ]]; then
  "${compose[@]}" run --rm dev bash run.sh
  if [[ "$kind" = php ]]; then
    "${compose[@]}" run --rm -e XDEBUG_MODE=coverage dev php -r 'if (!in_array("coverage", xdebug_info("mode"), true)) {exit(1);} echo "Xdebug coverage can be enabled\n";'
  fi
  test "$(stat -c %u "$work/workspace-proof.txt")" = "$PUID"
  # Cache persists between invocations, independently of service process lifetime.
  "${compose[@]}" run --rm dev bash -c 'test -d "$HOME/.cache"; touch "$HOME/.cache/reuse-proof"'
  if [[ "$kind" = php ]]; then
    "${compose[@]}" run --rm dev bash -c 'test -f "$HOME/.cache/cache-proof"; test -f "$HOME/.cache/reuse-proof"'
  fi
else
  WORKSPACE="$work" CACHE_VOLUME="$project-cache" bash "$root/scripts/run-image.sh" "$image" bash run.sh
  test "$(stat -c %u "$work/workspace-proof.txt")" = "$PUID"
fi
WORKSPACE="$work" CACHE_VOLUME="$project-cache" bash "$root/scripts/run-image.sh" "$image" bash -c 'cc native-check.c -o native-proof && ./native-proof'
printf 'Behavioral recipe completed in %ss for %s\n' "$((SECONDS-start))" "$line"
