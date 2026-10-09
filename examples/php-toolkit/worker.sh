#!/usr/bin/env bash
set -euo pipefail
action=${1:?}; kit=${2:?}; lint_kit=${3:?}; work=${4:?}
root=$(cd "$(dirname "$0")" && pwd -P)
php=${PHP_BIN:-php}
composer=${COMPOSER_BIN:-composer}
command -v "$php" >/dev/null || { echo 'PHP 8.4 or newer is required; select IMAGE or install PHP' >&2; exit 69; }
require_composer() { command -v "$composer" >/dev/null || { echo 'Composer 2 is required for native dependency installation' >&2; exit 69; }; }
prepared=${TOOLKIT_PREPARED_ROOT:-/opt/xorder/php-toolkit}
profile=validator
[[ "$action" != fresh ]] || profile=symfony-7.4
has_prepared=0
if [[ -f "$prepared/$profile/vendor/autoload.php" ]]; then
  has_prepared=1
  cmp "$root/$profile/composer.json" "$prepared/$profile/composer.json" || { echo 'Prepared manifest does not match this helper checkout' >&2; exit 65; }
  cmp "$root/$profile/composer.lock" "$prepared/$profile/composer.lock" || { echo 'Prepared dependencies do not match this helper checkout; select its matching php-toolkit image' >&2; exit 65; }
elif [[ ${TOOLKIT_REQUIRE_PREPARED:-0} = 1 ]]; then
  echo 'Prepared Toolkit dependencies are missing. Select an accepted php-toolkit image from the catalog.' >&2
  exit 69
fi
if [[ $(id -u) = 0 ]]; then export COMPOSER_ALLOW_SUPERUSER=1; fi
export COMPOSER=composer.json
if [[ "$action" = fresh ]]; then
  if [[ "$has_prepared" = 1 ]]; then
    # The baked baseline has never installed the consuming kit or warmed application caches.
    [[ ! -e "$prepared/$profile/.env.local" && ! -e "$prepared/$profile/var/cache" ]] || { echo 'Prepared baseline contains previous application state' >&2; exit 65; }
    while IFS= read -r -d '' source; do
      relative=${source#"$root/$profile/"}
      cmp "$source" "$prepared/$profile/$relative" || { echo "Prepared baseline source differs: $relative" >&2; exit 65; }
    done < <(find "$root/$profile" -type f -print0)
    cp -a --no-preserve=ownership "$prepared/$profile/." "$kit/"
  else
    require_composer
  fi
  "$php" -r 'file_put_contents($argv[1], "APP_SECRET=".bin2hex(random_bytes(32)).PHP_EOL);' "$kit/.env.local"
  original_lock=$("$php" -r 'echo hash_file("sha256", $argv[1]);' "$kit/composer.lock")
  if [[ "$has_prepared" != 1 ]]; then
    "$composer" install --working-dir="$kit" --no-interaction --no-progress --prefer-dist --no-scripts
  fi
  [[ $("$php" -r 'echo hash_file("sha256", $argv[1]);' "$kit/composer.lock") = "$original_lock" ]] || { echo 'Fresh app install changed its committed dependency lock' >&2; exit 1; }
  (cd "$kit" && "$php" bin/console cache:warmup --no-interaction && "$php" bin/console about --no-interaction)
  echo "Fresh Symfony 7.4 app ready for ux:install: $kit"
  exit 0
fi
if [[ "$has_prepared" = 1 ]]; then
  validator=$prepared/validator
else
  require_composer
  validator=$work/validator
  mkdir "$validator"
  cp "$root/validator/composer.json" "$root/validator/composer.lock" "$validator/"
  "$composer" install --working-dir="$validator" --no-interaction --no-progress --prefer-dist --no-scripts --no-plugins
fi
# Explicit PHP invocation keeps PHP_BIN authoritative even with Composer's generated bin proxies.
if [[ "$action" = check || "$action" = lint ]]; then
  "$php" "$validator/vendor/bin/ux-toolkit-kit-lint" "$lint_kit" --no-interaction
fi
if [[ "$action" = check || "$action" = debug ]]; then
  "$php" "$validator/vendor/bin/ux-toolkit-kit-debug" "$kit" --no-interaction
fi
