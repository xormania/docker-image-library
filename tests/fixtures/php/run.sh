#!/usr/bin/env bash
set -euo pipefail
composer install --no-interaction --prefer-dist
composer check-platform-reqs
php check.php
symfony version
if command -v frankenphp >/dev/null; then
  frankenphp version
  frankenphp list-modules | rg '^http.handlers.mercure$'
  php -r 'if (!extension_loaded("apcu") || !extension_loaded("Zend OPcache")) {exit(1);}'
  frankenphp run --config /workspace/Caddyfile >/tmp/library-php-server.log 2>&1 &
else
  php -S 127.0.0.1:8080 -t public >/tmp/library-php-server.log 2>&1 &
fi
server=$!
trap 'kill "$server" 2>/dev/null || true' EXIT
for attempt in {1..30}; do
  curl --fail --silent http://127.0.0.1:8080/ >/tmp/library-page && break
  sleep 1
done
rg 'Ready' /tmp/library-page
if command -v frankenphp >/dev/null; then
  first=$(curl --fail --silent -D - http://127.0.0.1:8080/ | tr -d '\r' | awk 'tolower($1)=="x-worker-requests:" {print $2}')
  second=$(curl --fail --silent -D - http://127.0.0.1:8080/ | tr -d '\r' | awk 'tolower($1)=="x-worker-requests:" {print $2}')
  test "$second" -eq "$((first+1))"
  echo 'Persistent FrankenPHP worker handled consecutive Symfony requests'
fi
if command -v chromium >/dev/null; then
  chromium --version
  chromedriver --version
  php browser.php
  test -s browser-proof.png
fi
