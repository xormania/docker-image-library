# syntax=docker/dockerfile:1
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
ARG SOURCE_COMMIT
ARG IMAGE_VERSION
LABEL org.opencontainers.image.revision="${SOURCE_COMMIT}" \
      org.opencontainers.image.version="${IMAGE_VERSION}"
RUN apt-get update && apt-get install -y --no-install-recommends \
      chromium chromium-driver fonts-liberation fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*
ENV PANTHER_CHROME_BINARY=/usr/bin/chromium \
    PANTHER_CHROME_DRIVER_BINARY=/usr/bin/chromedriver
