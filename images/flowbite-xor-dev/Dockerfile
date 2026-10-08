# syntax=docker/dockerfile:1
ARG NODE_IMAGE
ARG BASE_IMAGE
FROM ${NODE_IMAGE} AS node
FROM ${BASE_IMAGE}
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
COPY images/flowbite-xor-dev/entrypoint.sh /usr/local/bin/flowbite-entrypoint
ARG SOURCE_COMMIT
ARG IMAGE_VERSION
LABEL org.opencontainers.image.revision="${SOURCE_COMMIT}" \
      org.opencontainers.image.version="${IMAGE_VERSION}"
