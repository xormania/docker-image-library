# syntax=docker/dockerfile:1
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# Install during publication, when dist downloads are available. Consumers copy
# these two independent locked projects; their application vendor is unrelated.
COPY examples/php-toolkit/validator/composer.json examples/php-toolkit/validator/composer.lock /opt/xorder/php-toolkit/validator/
RUN set -eux; \
    export COMPOSER_ALLOW_SUPERUSER=1 COMPOSER_HOME=/tmp/toolkit-composer-home COMPOSER_CACHE_DIR=/tmp/toolkit-composer-cache; \
    cd /opt/xorder/php-toolkit/validator; \
    sha256sum composer.json composer.lock > /tmp/toolkit-validator-inputs.sha256; \
    composer install --no-interaction --no-progress --prefer-dist --no-scripts --no-plugins; \
    sha256sum --check /tmp/toolkit-validator-inputs.sha256; \
    composer check-platform-reqs; \
    test -s vendor/bin/ux-toolkit-kit-lint; \
    test -s vendor/bin/ux-toolkit-kit-debug; \
    rm -rf /tmp/toolkit-composer-home /tmp/toolkit-composer-cache /tmp/toolkit-validator-inputs.sha256

COPY examples/php-toolkit/symfony-7.4/ /opt/xorder/php-toolkit/symfony-7.4/
RUN set -eux; \
    export COMPOSER_ALLOW_SUPERUSER=1 COMPOSER_HOME=/tmp/toolkit-composer-home COMPOSER_CACHE_DIR=/tmp/toolkit-composer-cache; \
    cd /opt/xorder/php-toolkit/symfony-7.4; \
    sha256sum composer.json composer.lock symfony.lock > /tmp/toolkit-baseline-inputs.sha256; \
    composer install --no-interaction --no-progress --prefer-dist --no-scripts; \
    sha256sum --check /tmp/toolkit-baseline-inputs.sha256; \
    composer check-platform-reqs; \
    test -s vendor/autoload_runtime.php; \
    test ! -e .env.local; \
    test ! -d vendor/symfony/ux-toolkit/kits/xorder-consumer; \
    rm -rf var/cache var/log /tmp/toolkit-composer-home /tmp/toolkit-composer-cache /tmp/toolkit-baseline-inputs.sha256

ARG SOURCE_COMMIT
ARG IMAGE_VERSION
LABEL org.opencontainers.image.source="https://github.com/xormania/xorder" \
      org.opencontainers.image.revision="${SOURCE_COMMIT}" \
      org.opencontainers.image.version="${IMAGE_VERSION}"
