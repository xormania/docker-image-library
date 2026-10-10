#!/usr/bin/env bash
# Compare the candidate with committed consumer baselines; never generate new ones.
set -euo pipefail
browser=${1:?Supply browser image}
line=${2:?Supply browser line}
root=$(cd "$(dirname "$0")/../../.." && pwd)
work=$(mktemp -d)
export BROWSER_IMAGE="$browser" WORKSPACE="$work/repo" FLOWBITE_PROJECT="browser-parity-${RANDOM}-${RANDOM}"
export HTTP_PORT=18085 HTTPS_PORT=18445 HTTP3_PORT=18445
export IMAGE
IMAGE=$(python3 - "$root/catalog-v2.json" <<'PY'
import json, sys
entries = [item for item in json.load(open(sys.argv[1]))['resources']
           if item['id'] == 'image/flowbite-xor-dev/8.5-trixie'
           and item['lifecycle'] == 'available' and item['verification']['status'] == 'passed'
           and 'linux/amd64' in item['targets']]
if not entries:
    raise SystemExit('No accepted PHP application image for browser parity')
print(max(entries, key=lambda item: tuple(map(int, item['version'].split('.'))))['identity'])
PY
)
evidence="$root/out/playwright/${line//\//-}"
mkdir -p "$evidence"
cleanup() {
  result=$?
  if [ "$result" != 0 ]; then
    bash "$root/examples/flowbite-xor/run.sh" logs --tail 100 > "$evidence/stack.log" 2>&1 || true
  fi
  for directory in playwright-results playwright-report test-results; do
    if [ -d "$WORKSPACE/$directory" ]; then cp -a "$WORKSPACE/$directory" "$evidence/"; fi
  done
  bash "$root/examples/flowbite-xor/run.sh" down --volumes --remove-orphans >/dev/null 2>&1 || true
  rm -rf "$work"
}
trap cleanup EXIT
mapfile -t consumer < <(python3 - "$root/tests/fixtures/playwright/consumer.json" <<'PY'
import json, sys
item = json.load(open(sys.argv[1]))
print(item['repository']); print(item['commit']); print(item['playwright_version'])
PY
)
git init "$WORKSPACE"
git -C "$WORKSPACE" remote add origin "${consumer[0]}"
git -C "$WORKSPACE" fetch --depth 1 origin "${consumer[1]}"
git -C "$WORKSPACE" checkout --detach FETCH_HEAD
python3 - "$WORKSPACE" "${consumer[2]}" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
package = json.loads((root / 'package.json').read_text())
lock = json.loads((root / 'package-lock.json').read_text())
assert package['devDependencies']['@playwright/test'] == sys.argv[2]
assert lock['packages']['node_modules/@playwright/test']['version'] == sys.argv[2]
PY
docker pull "$IMAGE"
bash "$root/examples/flowbite-xor/run.sh" up
bash "$root/examples/flowbite-xor/run.sh" sync
bash "$root/examples/flowbite-xor/run.sh" exec env CI=1 npx playwright test \
  --project=examples --retries=0 --workers=4 --update-snapshots=none
# Enforce preservation of every committed baseline even if the consumer changes defaults.
git -C "$WORKSPACE" diff --exit-code -- '*.png'
python3 - "$evidence/consumer.json" "${consumer[1]}" "$browser" <<'PY'
import json, pathlib, sys
pathlib.Path(sys.argv[1]).write_text(json.dumps({'consumer_commit': sys.argv[2], 'browser': sys.argv[3],
    'project': 'examples', 'baseline_updates': False, 'status': 'passed'}, indent=2) + '\n')
PY
