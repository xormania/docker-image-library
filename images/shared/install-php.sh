#!/usr/bin/env bash
set -euo pipefail
apt-get update && apt-get install -y --no-install-recommends \
      libicu-dev libonig-dev libcurl4-openssl-dev libzip-dev libxml2-dev \
      libpng-dev libjpeg62-turbo-dev libfreetype6-dev libsqlite3-dev default-mysql-client \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" intl mbstring curl zip bcmath \
      pdo_pgsql pgsql pdo_mysql mysqli pdo_sqlite gd sockets pcntl \
    && pecl install "redis-${REDIS_VERSION}" "xdebug-${XDEBUG_VERSION}" "pcov-${PCOV_VERSION}" \
    && docker-php-ext-enable redis xdebug pcov \
    && rm -rf /var/lib/apt/lists/* /tmp/pear

if [ -n "${APCU_VERSION:-}" ]; then
  pecl install "apcu-${APCU_VERSION}"
  docker-php-ext-enable apcu
  rm -rf /tmp/pear
fi
