#!/usr/bin/env bash
set -euo pipefail
usage() { echo 'Usage: run.sh check|lint|debug KIT_DIRECTORY | fresh NEW_APP_DIRECTORY' >&2; exit 64; }
action=${1:-}; shift || usage
case "$action" in check|lint|debug|fresh) ;; *) usage ;; esac
[[ $# = 1 ]] || usage
root=$(cd "$(dirname "$0")" && pwd -P)
if [[ "$action" = fresh ]]; then
  [[ ! -e "$1" && ! -L "$1" ]] || { echo 'Fresh app destination must not exist; use a new directory for each run' >&2; exit 73; }
  mkdir -p "$(dirname "$1")"
  mkdir "$1"
  kit=$(cd "$1" && pwd -P)
  cp -a "$root/symfony-7.4/." "$kit/"
  cp "$kit/env.example" "$kit/.env"
else
  kit=$(cd "$1" && pwd -P)
  [[ -f "$kit/manifest.json" ]] || { echo 'Kit directory must contain manifest.json' >&2; exit 64; }
fi
cache=${COMPOSER_CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/xorder/composer}
mkdir -p "$cache"
cache=$(cd "$cache" && pwd -P)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
lint_kit=$kit
mode=${KIT_MODE:-auto}
case "$mode" in
  auto)
    if command -v git >/dev/null && [[ $(git -C "$kit" rev-parse --show-toplevel 2>/dev/null || true) = "$kit" ]]; then mode=archive; else mode=directory; fi ;;
  archive|directory) ;;
  *) echo 'KIT_MODE must be auto, archive, or directory' >&2; exit 64 ;;
esac
if [[ "$action" != debug && "$action" != fresh && "$mode" = archive ]]; then
  [[ $(git -C "$kit" rev-parse --show-toplevel) = "$kit" ]] || { echo 'Archive mode requires the kit at the Git repository root' >&2; exit 64; }
  mkdir "$work/kit"
  git -C "$kit" archive HEAD | tar -x -C "$work/kit"
  lint_kit=$work/kit
  echo 'Linting the committed HEAD archive, honoring export-ignore. KIT_MODE=directory checks working files.' >&2
fi
if [[ -n ${IMAGE:-} ]]; then
  [[ "$IMAGE" = *@sha256:* || ${TOOLKIT_LOCAL_IMAGE:-0} = 1 ]] || { echo 'IMAGE must be an accepted catalog digest reference; local build verification requires TOOLKIT_LOCAL_IMAGE=1' >&2; exit 64; }
  trust=()
  if [[ -n ${CA_CERTIFICATE:-} ]]; then
    [[ "$CA_CERTIFICATE" = /* && -r "$CA_CERTIFICATE" ]] || { echo 'CA_CERTIFICATE must be a readable absolute PEM path' >&2; exit 64; }
    trust=(--mount "type=bind,src=$CA_CERTIFICATE,dst=/run/xorder-ca.pem,readonly" -e LIBRARY_CA_FILE=/run/xorder-ca.pem)
  fi
  container_lint=/kit-source
  [[ "$lint_kit" = "$kit" ]] || container_lint=/work/kit
  kit_mount="type=bind,src=$kit,dst=/kit-source,readonly"
  [[ "$action" != fresh ]] || kit_mount="type=bind,src=$kit,dst=/kit-source"
  network=()
  [[ -z ${TOOLKIT_NETWORK:-} ]] || network=(--network "$TOOLKIT_NETWORK")
  python3 "$root/../shared/network.py" docker run --rm --init \
    -e HTTP_PROXY -e HTTPS_PROXY -e http_proxy -e https_proxy -e NO_PROXY -e no_proxy \
    -e PUID="${PUID:-$(id -u)}" -e PGID="${PGID:-$(id -g)}" \
    -e TOOLKIT_REQUIRE_PREPARED=1 "${network[@]}" \
    "${trust[@]}" \
    -e COMPOSER_CACHE_DIR=/composer-cache \
    --mount "type=bind,src=$root,dst=/xorder-toolkit,readonly" \
    --mount "$kit_mount" \
    --mount "type=bind,src=$work,dst=/work" \
    --mount "type=bind,src=$cache,dst=/composer-cache" \
    "$IMAGE" bash /xorder-toolkit/worker.sh "$action" /kit-source "$container_lint" /work
else
  if [[ -n ${CA_CERTIFICATE:-} ]]; then
    [[ "$CA_CERTIFICATE" = /* && -r "$CA_CERTIFICATE" ]] || { echo 'CA_CERTIFICATE must be a readable absolute PEM path' >&2; exit 64; }
    export COMPOSER_CAFILE=$CA_CERTIFICATE
  fi
  COMPOSER_CACHE_DIR=$cache bash "$root/worker.sh" "$action" "$kit" "$lint_kit" "$work"
fi
