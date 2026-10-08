# syntax=docker/dockerfile:1
ARG COMPOSER_IMAGE
ARG BASE_IMAGE
FROM ${COMPOSER_IMAGE} AS composer
FROM ${BASE_IMAGE}
ARG REDIS_VERSION
ARG XDEBUG_VERSION
ARG SYMFONY_URL
ARG SYMFONY_SHA256
ARG SOURCE_COMMIT
ARG IMAGE_VERSION
LABEL org.opencontainers.image.source="https://github.com/xormania/docker-image-library" \
      org.opencontainers.image.revision="${SOURCE_COMMIT}" \
      org.opencontainers.image.version="${IMAGE_VERSION}"
COPY images/shared/install.sh /tmp/install-common
RUN bash /tmp/install-common && rm /tmp/install-common
RUN apt-get update && apt-get install -y --no-install-recommends \
      libicu-dev libonig-dev libcurl4-openssl-dev libzip-dev libxml2-dev \
      libpng-dev libjpeg62-turbo-dev libfreetype6-dev libsqlite3-dev default-mysql-client \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" intl mbstring curl zip bcmath \
      pdo_pgsql pgsql pdo_mysql mysqli pdo_sqlite gd sockets pcntl \
    && pecl install "redis-${REDIS_VERSION}" "xdebug-${XDEBUG_VERSION}" \
    && docker-php-ext-enable redis xdebug \
    && rm -rf /var/lib/apt/lists/* /tmp/pear
COPY --from=composer /usr/bin/composer /usr/local/bin/composer
RUN curl --fail --location --retry 3 "$SYMFONY_URL" -o /tmp/symfony.tar.gz \
    && printf '%s  %s\n' "$SYMFONY_SHA256" /tmp/symfony.tar.gz | sha256sum -c - \
    && tar -xzf /tmp/symfony.tar.gz -C /usr/local/bin symfony \
    && rm /tmp/symfony.tar.gz
COPY images/php-dev/development.ini /usr/local/etc/php/conf.d/zz-development.ini
COPY images/shared/entrypoint.sh /usr/local/bin/library-entrypoint
ENV HOME=/home/dev COMPOSER_HOME=/home/dev/.composer \
    XDG_CACHE_HOME=/home/dev/.cache XDEBUG_MODE=off
WORKDIR /workspace
ENTRYPOINT ["bash", "/usr/local/bin/library-entrypoint"]
CMD ["bash"]
