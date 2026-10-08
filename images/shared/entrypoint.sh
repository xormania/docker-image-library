#!/usr/bin/env bash
set -euo pipefail
uid=${PUID:-1000}
gid=${PGID:-1000}
[[ "$uid" =~ ^[0-9]+$ && "$gid" =~ ^[0-9]+$ ]] || { echo 'PUID and PGID must be numeric' >&2; exit 64; }
if [ -n "${LIBRARY_CA_FILE:-}" ]; then
  [ "$(id -u)" = 0 ] || { echo 'LIBRARY_CA_FILE needs the root entrypoint; use a pre-trusted image or tool CA options with --user' >&2; exit 64; }
  [[ "$LIBRARY_CA_FILE" = /* && -r "$LIBRARY_CA_FILE" ]] || { echo 'LIBRARY_CA_FILE must name a readable absolute PEM path' >&2; exit 64; }
  [ "$(grep -c -- '-----BEGIN CERTIFICATE-----' "$LIBRARY_CA_FILE")" = 1 ] && \
    openssl x509 -in "$LIBRARY_CA_FILE" -noout >/dev/null || { echo 'LIBRARY_CA_FILE must contain one PEM certificate' >&2; exit 64; }
  install -m 0644 "$LIBRARY_CA_FILE" /usr/local/share/ca-certificates/library-proxy.crt
  update-ca-certificates >&2
  export COMPOSER_CAFILE="${COMPOSER_CAFILE:-/etc/ssl/certs/ca-certificates.crt}"
  export NODE_EXTRA_CA_CERTS="${NODE_EXTRA_CA_CERTS:-/etc/ssl/certs/ca-certificates.crt}"
fi
# Explicit --user bypasses privilege changes, but keeps the writable HOME convention.
if [ "$(id -u)" = 0 ]; then
  if [ "$uid" != 0 ]; then
    if [ "$(id -g dev)" != "$gid" ]; then groupmod --non-unique --gid "$gid" dev >&2; fi
    if [ "$(id -u dev)" != "$uid" ] || [ "$(id -g dev)" != "$gid" ]; then
      usermod --non-unique --uid "$uid" --gid "$gid" dev >&2
    fi
  fi
  # Never recursively change the consuming project's bind mount.
  chown -R "$uid:$gid" /home/dev
  # These image-owned directories hold Caddy state, never application sources.
  if command -v frankenphp >/dev/null; then
    chown -R "$uid:$gid" /data /config
  fi
  exec gosu "$uid:$gid" "$@"
fi
exec "$@"
