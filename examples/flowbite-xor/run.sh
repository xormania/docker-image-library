#!/usr/bin/env bash
set -euo pipefail
action=${1:?Usage: run.sh up|test|phpunit|exec|logs|down [arguments]}; shift
root=$(cd "$(dirname "$0")" && pwd)
export WORKSPACE=${WORKSPACE:?Set WORKSPACE to your flowbite-xor checkout}
WORKSPACE=$(cd "$WORKSPACE" && pwd)
export IMAGE=${IMAGE:?Select the verified flowbite-xor-dev digest from the catalog}
export PUID=${PUID:-$(id -u)} PGID=${PGID:-$(id -g)}
export HTTP_PORT=${HTTP_PORT:-8084} HTTPS_PORT=${HTTPS_PORT:-8444} HTTP3_PORT=${HTTP3_PORT:-8444}
export CONTAINER_CA_FILE=
if [ -n "${CA_CERTIFICATE:-}" ]; then
  [[ "$CA_CERTIFICATE" = /* && -r "$CA_CERTIFICATE" ]] || { echo 'CA_CERTIFICATE must be a readable absolute PEM path' >&2; exit 64; }
  export CONTAINER_CA_FILE=/run/library-proxy.pem
fi
# Read the installed/test version from the lock without requiring host Node.
export PLAYWRIGHT_VERSION
PLAYWRIGHT_VERSION=$(docker run --rm --init -e PUID="$PUID" -e PGID="$PGID" \
  --mount "type=bind,src=$WORKSPACE,dst=/workspace,readonly" "$IMAGE" node -e '
  const lock=require("/workspace/package-lock.json"), pkg=require("/workspace/package.json");
  const version=lock.packages["node_modules/@playwright/test"].version;
  if (!/^\d+\.\d+\.\d+$/.test(version) || pkg.devDependencies["@playwright/test"] !== version) {
    throw Error("Pin @playwright/test to the same exact version in package.json and package-lock.json");
  }
  process.stdout.write(version);')
compose=(docker compose --project-directory "$WORKSPACE/demo" -p "${FLOWBITE_PROJECT:-flowbite-xor-library}"
  -f "$WORKSPACE/demo/compose.yaml" -f "$WORKSPACE/demo/compose.override.yaml" -f "$root/compose.yaml")
# Git needs the common objects/refs and the private linked-worktree metadata.
# Keep the replacement pointer durable so container restarts can rebind it.
if [[ "${WORKTREE_GIT:-0}" = 1 && -f "$WORKSPACE/.git" ]]; then
  common=$(git -C "$WORKSPACE" rev-parse --path-format=absolute --git-common-dir)
  private=$(git -C "$WORKSPACE" rev-parse --absolute-git-dir)
  key=$(printf '%s' "$WORKSPACE" | git hash-object --stdin)
  cache="${XDG_CACHE_HOME:-$HOME/.cache}/docker-image-library/worktrees/$key"
  mkdir -p "$cache"
  printf 'gitdir: %s\n' "$private" > "$cache/git-pointer"
  chmod 644 "$cache/git-pointer"
  json_string() {
    local value=$1
    value=${value//\\/\\\\}; value=${value//\"/\\\"}
    value=${value//$'\n'/\\n}; value=${value//$'\r'/\\r}; value=${value//$'\t'/\\t}
    printf '"%s"' "$value"
  }
  overlay=$(mktemp)
  trap 'rm -f "$overlay"' EXIT
  printf '{"services":{"php":{"environment":{"GIT_OPTIONAL_LOCKS":"0"},"volumes":[{"type":"bind","source":%s,"target":%s,"read_only":true,"bind":{"create_host_path":false}},{"type":"bind","source":%s,"target":"/app/.git","read_only":true,"bind":{"create_host_path":false}}]}}}\n' \
    "$(json_string "$common")" "$(json_string "$common")" "$(json_string "$cache/git-pointer")" > "$overlay"
  compose+=(-f "$overlay")
fi
case "$action" in
  up)
    "${compose[@]}" up --wait --wait-timeout 600 --no-build
    "${compose[@]}" exec -T --user "$PUID:$PGID" -w /app php php tools/sync-demo
    "${compose[@]}" exec -T --user "$PUID:$PGID" -w /app/demo php flowbite-prime-tailwind
    "${compose[@]}" exec -T --user "$PUID:$PGID" -w /app php npm ci
    ;;
  test) "${compose[@]}" exec -T --user "$PUID:$PGID" -w /app php npx playwright test "$@" ;;
  phpunit) "${compose[@]}" exec -T --user "$PUID:$PGID" -w /app/demo \
    -e "XDEBUG_MODE=${PHPUNIT_XDEBUG_MODE:-off}" -e APP_ENV=test -e APP_DEBUG=1 \
    -e CREATE_SNAPSHOTS=false php php bin/phpunit "$@" ;;
  exec) "${compose[@]}" exec -T --user "$PUID:$PGID" -w /app php "$@" ;;
  logs) "${compose[@]}" logs "$@" ;;
  down) "${compose[@]}" down "$@" ;;
  *) echo "Unknown action: $action" >&2; exit 64 ;;
esac
