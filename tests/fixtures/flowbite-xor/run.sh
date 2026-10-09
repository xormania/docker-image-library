#!/usr/bin/env bash
set -euo pipefail
image=${1:?Supply flowbite-xor-dev image}
root=$(cd "$(dirname "$0")/../../.." && pwd)
docker run --rm --mount "type=bind,src=$root,dst=/xorder,readonly" "$image" \
  bash /xorder/tests/fixtures/flowbite-xor/verify-composer-reuse.sh
work=$(mktemp -d)
export IMAGE="$image" WORKSPACE="$work/repo" FLOWBITE_PROJECT="flowbite-check-${RANDOM}-${RANDOM}"
export HTTP_PORT=18084 HTTPS_PORT=18444 HTTP3_PORT=18444
export WORKTREE_GIT=1
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
git init "$work/main"
git -C "$work/main" remote add origin "${consumer[0]}"
git -C "$work/main" fetch --depth 1 origin "${consumer[1]}"
git -C "$work/main" worktree add --detach "$WORKSPACE" FETCH_HEAD
# The upstream test observes history before Turbo's promoted visit completes.
# Keep this verification-only overlay tied to its reviewed source; changing the
# consumer pin requires removing or reviewing the overlay, not applying it blindly.
if [[ "${consumer[1]}" != c8878af66897d8c10af694050a7a588166942117 ]]; then
  printf 'Review the frame-navigation completion overlay for the new consumer pin\n' >&2
  exit 1
fi
fixture_patch="$root/tests/fixtures/flowbite-xor/frame-navigation-completion.patch"
printf 'Applying xorder-owned test synchronization overlay to pinned flowbite-xor %s\n' "${consumer[1]}"
git -C "$WORKSPACE" apply --check "$fixture_patch"
git -C "$WORKSPACE" apply --whitespace=error "$fixture_patch"
bash "$root/examples/flowbite-xor/run.sh" up
bash "$root/examples/flowbite-xor/run.sh" status
bash "$root/examples/flowbite-xor/run.sh" exec test -s demo/var/tailwind/app.built.css
before_setup=$(bash "$root/examples/flowbite-xor/run.sh" exec bash -c 'cat demo/var/xorder/composer-ready demo/var/xorder/node-ready')
bash "$root/examples/flowbite-xor/run.sh" up
bash "$root/examples/flowbite-xor/run.sh" status
# Matching setup avoids package reinstalls; the recorded content stays stable.
after_setup=$(bash "$root/examples/flowbite-xor/run.sh" exec bash -c 'cat demo/var/xorder/composer-ready demo/var/xorder/node-ready')
test "$before_setup" = "$after_setup"
test "$(bash "$root/examples/flowbite-xor/run.sh" exec git rev-parse HEAD)" = "${consumer[1]}"
bash "$root/examples/flowbite-xor/run.sh" exec git status --porcelain
bash "$root/examples/flowbite-xor/run.sh" exec bash -c 'cd demo && composer check-platform-reqs'
bash "$root/examples/flowbite-xor/run.sh" exec bash -c \
  'cd demo && cmp /opt/tailwind/tailwindcss-linux-x64 "var/tailwind/$(cat /opt/tailwind/version)/tailwindcss-linux-x64" && php bin/console tailwind:build'
bash "$root/examples/flowbite-xor/run.sh" php-tests all
bash "$root/examples/flowbite-xor/run.sh" exec php -r \
  '$report=simplexml_load_file("demo/var/phpunit-coverage.xml"); if (!$report || (int)$report->project->metrics["coveredstatements"] < 1) { throw new RuntimeException("PHPUnit must record executed statements"); }'
bash "$root/examples/flowbite-xor/run.sh" test "${consumer[@]:2}"
# Composer, Node and the app must write the host mount as the requested user.
test "$(stat -c %u "$WORKSPACE/node_modules")" = "$(id -u)"
test "$(stat -c %u "$WORKSPACE/demo/vendor")" = "$(id -u)"
