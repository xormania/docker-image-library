#!/usr/bin/env bash
set -euo pipefail
mkdir -p /opt/xorder/infection
curl --fail --location --retry 3 "$INFECTION_URL" -o /opt/xorder/infection/infection.phar
printf '%s  %s\n' "$INFECTION_SHA256" /opt/xorder/infection/infection.phar | sha256sum --check --strict
php /opt/xorder/infection/infection.phar --version
