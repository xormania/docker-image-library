#!/usr/bin/env bash
set -euo pipefail

php --version
composer --version
symfony version
composer install --no-interaction --prefer-dist --no-progress
composer check-platform-reqs
php check.php

url="http://127.0.0.1:${XORDER_TEST_PORT:?Missing fixture port}"
for attempt in {1..30}; do
  if curl --fail --silent "$url/" >page.html; then
    break
  fi
  sleep 1
done
test -s page.html
grep -q '<h1>Ready</h1>' page.html
test "$(curl --silent --output missing.html --write-out '%{http_code}' "$url/missing")" = 404
grep -q 'Missing route' missing.html
echo 'Locked Symfony application served its success and missing routes'
