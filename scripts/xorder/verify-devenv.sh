#!/usr/bin/env bash
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
mode=verify
if [[ ${1:-} == --generate-lock ]]; then
  mode=generate
  shift
fi
resource=$(realpath "${1:?Pass the extracted environment root}")
command -v nix >/dev/null
command -v devenv >/dev/null

if [[ $mode == generate ]]; then
  work=$(mktemp -d "${TMPDIR:-/tmp}/xorder-devenv-lock.XXXXXXXX")
  trap 'rm -rf "$work"' EXIT
  cp "$resource"/devenv.{nix,yaml} "$work/"
  (cd "$work" && devenv update)
  test -s "$work/devenv.lock"
  cp "$work/devenv.lock" "$resource/devenv.lock"
  exit
fi

for file in devenv.nix devenv.yaml devenv.lock; do
  test -s "$resource/$file"
done
work=$(mktemp -d "${TMPDIR:-/tmp}/xorder-devenv.XXXXXXXX")
trap 'rm -rf "$work"' EXIT
mkdir "$work/environment"
cp "$resource"/devenv.{nix,yaml,lock} "$work/environment/"
cp "$resource/devenv.lock" "$work/devenv.lock"
cp "$repo"/tests/fixtures/artifacts/environment/* "$work/"
# Reuse the locked real Symfony dependency fixture. Do not generate a second lock.
cp "$repo"/tests/fixtures/php/composer.{json,lock} "$work/"
cp -R "$repo/tests/fixtures/php/public" "$work/"
export XORDER_TEST_PORT
XORDER_TEST_PORT=$(python3 - <<'PY'
import socket
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    print(sock.getsockname()[1])
PY
)
(cd "$work" && devenv test)
cmp "$resource/devenv.lock" "$work/devenv.lock"
cmp "$resource/devenv.lock" "$work/environment/devenv.lock"
cmp "$repo/tests/fixtures/php/composer.lock" "$work/composer.lock"
test -s "$work/workspace-proof.txt"
python3 - <<'PY'
import os
import socket
with socket.socket() as sock:
    sock.settimeout(2)
    if sock.connect_ex(('127.0.0.1', int(os.environ['XORDER_TEST_PORT']))) == 0:
        raise SystemExit('devenv left the consumer HTTP service listening after test')
print('Native composition, unchanged locks, writable workspace and service shutdown passed')
PY
