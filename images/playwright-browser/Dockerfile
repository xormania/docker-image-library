# syntax=docker/dockerfile:1
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
ARG APT_REFRESH
ENV DEBIAN_FRONTEND=noninteractive PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers HOME=/home/dev
COPY images/playwright-browser/package*.json /opt/playwright/
RUN npm ci --prefix /opt/playwright --ignore-scripts --no-audit --no-fund \
    && /opt/playwright/node_modules/.bin/playwright install --with-deps chromium firefox webkit \
    && mv /etc/fonts/conf.d/10-sub-pixel-none.conf /etc/fonts/10-sub-pixel-none.conf.disabled \
    && ln -s /usr/share/fontconfig/conf.avail/10-sub-pixel-rgb.conf /etc/fonts/conf.d/10-sub-pixel-rgb.conf \
    && apt-get update \
    && apt-get install -y --no-install-recommends python3 gosu ca-certificates \
    && rm -rf /var/lib/apt/lists/* /root/.npm /usr/local/lib/node_modules/npm \
    && rm -f /usr/local/bin/npm /usr/local/bin/npx \
    && ln -s /opt/playwright/node_modules/playwright/cli.js /usr/local/bin/playwright \
    && useradd --create-home --uid 1000 --non-unique --shell /bin/bash dev \
    && mkdir -p /workspace /home/dev/.cache \
    && chmod -R a+rX /opt/playwright-browsers
COPY --chmod=755 images/shared/entrypoint.sh /usr/local/bin/library-entrypoint
WORKDIR /workspace
ENTRYPOINT ["library-entrypoint"]
CMD ["playwright", "run-server", "--host", "0.0.0.0", "--port", "3000"]
ARG SOURCE_COMMIT
ARG IMAGE_VERSION
LABEL org.opencontainers.image.source="https://github.com/xormania/xorder" \
      org.opencontainers.image.revision="${SOURCE_COMMIT}" \
      org.opencontainers.image.version="${IMAGE_VERSION}"
