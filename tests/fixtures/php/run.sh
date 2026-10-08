#!/usr/bin/env bash
set -euo pipefail
composer install --no-interaction --prefer-dist
composer check-platform-reqs
php check.php
symfony version
php -S 127.0.0.1:8080 -t public >/tmp/library-php-server.log 2>&1 &
server=$!
trap 'kill "$server" 2>/dev/null || true' EXIT
for attempt in {1..30}; do
  curl --fail --silent http://127.0.0.1:8080/ >/tmp/library-page && break
  sleep 1
done
rg 'Ready' /tmp/library-page
if command -v chromium >/dev/null; then
  chromium --version
  chromedriver --version
  php browser.php
  test -s browser-proof.png
fi
