#!/usr/bin/env bash
set -euo pipefail
profile=$(cd "$(dirname "$0")" && pwd)
if [[ "${1:-}" = --entrypoint ]]; then
  shift
  uid=${PUID:-1000}; gid=${PGID:-1000}
  [[ "$uid" =~ ^[0-9]+$ && "$gid" =~ ^[0-9]+$ ]] || exit 64
  if [[ $(id -u) = 0 ]]; then
    # Only the profile-owned cache volume, never the source or host Composer cache.
    chown -R "$uid:$gid" /app/demo/var
  fi
  cd /app/demo
  exec bash /usr/local/bin/library-entrypoint bash "$profile/startup.sh" --application "$@"
fi
mode=${1:?Supply --prepare or --application}; shift
[[ "$mode" = --prepare || "$mode" = --application ]] || exit 64
cd /app/demo
preference=${COMPOSER_INSTALL_PREFERENCE:-dist}
[[ "$preference" = dist || "$preference" = source ]] || { echo 'COMPOSER_INSTALL_PREFERENCE must be dist or source' >&2; exit 64; }
# A development profile always installs dev requirements and regenerates normal
# autoloads. Do not silently inherit install flags from a production shell.
unset COMPOSER_NO_DEV COMPOSER_NO_SCRIPTS
php /app/tools/sync-demo
composer validate --no-check-publish --no-interaction
mkdir -p var/xorder
marker=var/xorder/composer-ready
fingerprint() {
  php "$profile/verify-composer.php" fingerprint
}
if php "$profile/verify-composer.php" verify; then
  before=$(fingerprint)
  if [[ ! -f "$marker" || $(cat "$marker") != "$before" ]]; then
    composer dump-autoload --no-interaction
    # Imported vendor bytes still need the application's own setup hooks.
    composer run-script --if-defined post-install-cmd --no-interaction
  else
    echo 'Reusing verified Composer dependencies and setup'
  fi
else
  composer install "--prefer-$preference" --no-progress --no-interaction
fi
php "$profile/verify-composer.php" verify
fingerprint > "$marker.tmp"
mv "$marker.tmp" "$marker"
flowbite-prime-tailwind
if [[ "$mode" = --application ]]; then
  # Keep the project's runtime, database wait and docker-php-entrypoint behavior.
  exec sh /app/demo/frankenphp/docker-entrypoint.sh "$@"
fi
