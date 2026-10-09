#!/usr/bin/env bash
set -euo pipefail
uid=${PUID:-1000}
gid=${PGID:-1000}
[[ "$uid" =~ ^[0-9]+$ && "$gid" =~ ^[0-9]+$ ]] || { echo 'PUID and PGID must be numeric' >&2; exit 64; }
if [ -n "${LIBRARY_CA_FILE:-}" ]; then
  [ "$(id -u)" = 0 ] || { echo 'LIBRARY_CA_FILE needs the root entrypoint; use a pre-trusted image or tool CA options with --user' >&2; exit 64; }
  [[ "$LIBRARY_CA_FILE" = /* && -f "$LIBRARY_CA_FILE" && -r "$LIBRARY_CA_FILE" ]] || { echo 'LIBRARY_CA_FILE must name a readable absolute PEM file' >&2; exit 64; }
  # Debian's trust updater needs one certificate per .crt file. Validate the
  # entire bundle before replacing any xorder-owned trust, including on restart.
  (
    umask 077
    ca_stage=$(mktemp -d "${TMPDIR:-/tmp}/library-ca.XXXXXXXX")
    trap 'rm -rf -- "$ca_stage"' EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    ca_error() { echo 'LIBRARY_CA_FILE must contain one or more valid PEM certificates; only whitespace and comments may appear between certificates' >&2; exit 64; }
    ca_count=0
    ca_open=0
    while IFS= read -r ca_line || [ -n "$ca_line" ]; do
      ca_line=${ca_line%$'\r'}
      case "$ca_line" in
        '-----BEGIN CERTIFICATE-----')
          [ "$ca_open" = 0 ] || ca_error
          ca_count=$((ca_count + 1))
          printf -v ca_pem '%s/library-proxy-%06d.pem' "$ca_stage" "$ca_count"
          ca_open=1
          printf '%s\n' "$ca_line" > "$ca_pem"
          ;;
        '-----END CERTIFICATE-----')
          [ "$ca_open" = 1 ] || ca_error
          printf '%s\n' "$ca_line" >> "$ca_pem"
          ca_open=0
          ;;
        *)
          if [ "$ca_open" = 1 ]; then
            printf '%s\n' "$ca_line" >> "$ca_pem"
          else
            [[ "$ca_line" =~ ^[[:space:]]*(#.*)?$ ]] || ca_error
          fi
          ;;
      esac
    done < "$LIBRARY_CA_FILE"
    [ "$ca_open" = 0 ] && [ "$ca_count" -gt 0 ] || ca_error
    for ca_pem in "$ca_stage"/*.pem; do
      openssl x509 -in "$ca_pem" -outform PEM -out "${ca_pem%.pem}.crt" || ca_error
    done
    ca_directory=/usr/local/share/ca-certificates/library-proxy
    install -d -m 0755 "$ca_directory"
    # Remove only the previous single-file layout and this option's own files.
    rm -f -- /usr/local/share/ca-certificates/library-proxy.crt "$ca_directory"/*.crt
    install -m 0644 "$ca_stage"/*.crt "$ca_directory/"
    # Content can change while its managed filename stays the same. Force a
    # rehash so clients using CApath see the replacement's subject lookup.
    update-ca-certificates --fresh >&2
  )
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
