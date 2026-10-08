# syntax=docker/dockerfile:1
ARG COMPOSER_IMAGE
ARG BASE_IMAGE
FROM ${COMPOSER_IMAGE} AS composer
FROM ${BASE_IMAGE}
ARG APT_REFRESH
COPY images/shared/install.sh /tmp/install-common
RUN test -n "$APT_REFRESH" && bash /tmp/install-common && rm /tmp/install-common
ARG REDIS_VERSION
ARG XDEBUG_VERSION
ARG APCU_VERSION
COPY images/shared/install-php.sh /tmp/install-php
RUN bash /tmp/install-php && rm /tmp/install-php
COPY --from=composer /usr/bin/composer /usr/local/bin/composer
ARG SYMFONY_URL
ARG SYMFONY_SHA256
COPY images/shared/install-symfony.sh /tmp/install-symfony
RUN bash /tmp/install-symfony && rm /tmp/install-symfony
RUN mkdir -p /data /config && chown -R dev:dev /data /config
COPY images/shared/development.ini /usr/local/etc/php/conf.d/zz-development.ini
COPY images/shared/entrypoint.sh /usr/local/bin/library-entrypoint
ENV HOME=/home/dev COMPOSER_HOME=/home/dev/.composer \
    XDG_CACHE_HOME=/home/dev/.cache XDEBUG_MODE=off
WORKDIR /workspace
ENTRYPOINT ["bash", "/usr/local/bin/library-entrypoint"]
CMD ["bash"]
ARG SOURCE_COMMIT
ARG IMAGE_VERSION
LABEL org.opencontainers.image.source="https://github.com/xormania/docker-image-library" \
      org.opencontainers.image.revision="${SOURCE_COMMIT}" \
      org.opencontainers.image.version="${IMAGE_VERSION}"
