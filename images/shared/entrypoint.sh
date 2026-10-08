#!/usr/bin/env bash
set -euo pipefail
uid=${PUID:-1000}
gid=${PGID:-1000}
[[ "$uid" =~ ^[0-9]+$ && "$gid" =~ ^[0-9]+$ ]] || { echo 'PUID and PGID must be numeric' >&2; exit 64; }
# Explicit --user bypasses privilege changes, but keeps the writable HOME convention.
if [ "$(id -u)" = 0 ]; then
  if [ "$uid" != 0 ]; then
    groupmod --non-unique --gid "$gid" dev
    usermod --non-unique --uid "$uid" --gid "$gid" dev
  fi
  # Never recursively change the consuming project's bind mount.
  chown -R "$uid:$gid" /home/dev
  exec gosu "$uid:$gid" "$@"
fi
exec "$@"
