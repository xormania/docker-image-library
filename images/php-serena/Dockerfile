# syntax=docker/dockerfile:1
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# Keep the proven Agentscient v2 REPL/PHPactor pair. The PHP/Trixie parent
# supplies Python and mbstring; consume its exact verified artifact unchanged.
COPY --from=ghcr.io/astral-sh/uv:0.12.19@sha256:04d046b13e60d6bcec73cbc5e1cad25d680dea90c8573340950a0ac2d1aef424 /uv /usr/local/bin/uv
COPY images/php-serena/requirements-build.txt /opt/xorder/serena/requirements-build.txt
RUN git init /opt/serena-source \
    && git -C /opt/serena-source remote add origin https://github.com/oraios/serena.git \
    && git -C /opt/serena-source fetch --depth=1 origin b79e2a55f9d4072084977dd35bd07d31146d88b9 \
    && git -C /opt/serena-source checkout --detach FETCH_HEAD \
    && test "$(git -C /opt/serena-source rev-parse HEAD)" = b79e2a55f9d4072084977dd35bd07d31146d88b9 \
    && uv --no-cache venv --python /usr/bin/python3 /opt/serena-env \
    && uv --no-cache pip install --python /opt/serena-env/bin/python \
        --require-hashes --only-binary :all: -r /opt/xorder/serena/requirements-build.txt \
    && UV_PROJECT_ENVIRONMENT=/opt/serena-env UV_PYTHON_DOWNLOADS=never \
        uv --no-cache sync --project /opt/serena-source --python /usr/bin/python3 \
        --locked --no-dev --no-editable --no-build-isolation \
    && uv pip check --python /opt/serena-env/bin/python \
    && git -C /opt/serena-source diff --exit-code -- pyproject.toml uv.lock
RUN curl --fail --location --silent --show-error \
        https://github.com/phpactor/phpactor/releases/download/2025.12.21.1/phpactor.phar \
        --output /opt/xorder/serena/phpactor.phar \
    && echo '53bbe9625cd9b5e9b394bc2f595fbad13dbbe6dfc96950c56dea3b5d9a246cc3  /opt/xorder/serena/phpactor.phar' | sha256sum --check
COPY --chmod=755 images/php-serena/launch.py /usr/local/bin/library-serena
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["library-serena"]

ARG SOURCE_COMMIT
ARG IMAGE_VERSION
LABEL org.opencontainers.image.source="https://github.com/xormania/xorder" \
      org.opencontainers.image.revision="${SOURCE_COMMIT}" \
      org.opencontainers.image.version="${IMAGE_VERSION}" \
      io.xorder.serena.revision="b79e2a55f9d4072084977dd35bd07d31146d88b9"
