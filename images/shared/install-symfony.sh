#!/usr/bin/env bash
set -euo pipefail
curl --fail --location --retry 3 "$SYMFONY_URL" -o /tmp/symfony.tar.gz \
    && printf '%s  %s\n' "$SYMFONY_SHA256" /tmp/symfony.tar.gz | sha256sum -c - \
    && tar -xzf /tmp/symfony.tar.gz -C /usr/local/bin symfony \
    && rm /tmp/symfony.tar.gz
