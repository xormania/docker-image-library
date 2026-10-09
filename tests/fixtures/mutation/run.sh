#!/usr/bin/env bash
set -euo pipefail
composer install --no-interaction --no-progress --prefer-dist --no-scripts --no-plugins
composer check-platform-reqs
sha256sum composer.lock > /tmp/mutation-lock.sha256
infection --configuration=infection.json --threads=1 --no-progress --no-interaction --min-msi=100 --min-covered-msi=100
cp var/mutation-summary.json var/strong-summary.json
if WEAK_ASSERTIONS=1 infection --configuration=infection.json --threads=1 --no-progress --no-interaction --min-msi=100 --min-covered-msi=100; then
  echo 'Weak assertions unexpectedly killed every mutant' >&2
  exit 1
fi
python3 - <<'PY'
import json
from pathlib import Path
strong = json.loads(Path('var/strong-summary.json').read_text())
weak = json.loads(Path('var/mutation-summary.json').read_text())
assert strong['stats']['killedCount'] > 0, strong
assert strong['stats']['escapedCount'] == 0, strong
assert weak['stats']['escapedCount'] > 0, weak
print('Mutation check: boundary assertion kills the mutant; type-only assertion lets it escape')
PY
sha256sum --check /tmp/mutation-lock.sha256
php -r 'if (!extension_loaded("xdebug") || ini_get("pcov.enabled")) {exit(1);}'
