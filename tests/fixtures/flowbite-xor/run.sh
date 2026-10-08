#!/usr/bin/env bash
set -euo pipefail
image=${1:?Supply flowbite-xor-dev image}
root=$(cd "$(dirname "$0")/../../.." && pwd)
work=$(mktemp -d)
export IMAGE="$image" WORKSPACE="$work/repo" FLOWBITE_PROJECT="flowbite-check-${RANDOM}-${RANDOM}"
export HTTP_PORT=18084 HTTPS_PORT=18444 HTTP3_PORT=18444
cleanup() {
  status=$?
  if [ "$status" != 0 ]; then
    bash "$root/examples/flowbite-xor/run.sh" logs --tail 100 >/dev/stderr 2>&1 || true
  fi
  bash "$root/examples/flowbite-xor/run.sh" down --volumes --remove-orphans >/dev/null 2>&1 || true
  # Only this disposable cloned fixture, even if a failing command wrote as root.
  if [ -d "$WORKSPACE" ]; then
    docker run --rm -e PUID=0 -e PGID=0 --mount "type=bind,src=$WORKSPACE,dst=/workspace" \
      "$image" find /workspace -mindepth 1 -delete >/dev/null 2>&1 || true
  fi
  rm -rf "$work"
}
trap cleanup EXIT
mapfile -t consumer < <(python3 -c 'import json,sys; c=json.load(open(sys.argv[1])); print(c["repository"]); print(c["commit"]); print("\n".join(c["tests"]))' "$root/tests/fixtures/flowbite-xor/consumer.json")
git init "$WORKSPACE"
git -C "$WORKSPACE" remote add origin "${consumer[0]}"
git -C "$WORKSPACE" fetch --depth 1 origin "${consumer[1]}"
git -C "$WORKSPACE" checkout --detach FETCH_HEAD
bash "$root/examples/flowbite-xor/run.sh" up
bash "$root/examples/flowbite-xor/run.sh" exec bash -c 'cd demo && composer check-platform-reqs'
bash "$root/examples/flowbite-xor/run.sh" test "${consumer[@]:2}"
# Composer, Node and the app must write the host mount as the requested user.
test "$(stat -c %u "$WORKSPACE/node_modules")" = "$(id -u)"
test "$(stat -c %u "$WORKSPACE/demo/vendor")" = "$(id -u)"
