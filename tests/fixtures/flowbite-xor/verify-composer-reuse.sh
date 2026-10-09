#!/usr/bin/env bash
# Real offline Composer installs, with deliberately different source/dist refs.
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
export COMPOSER_HOME="$work/home" COMPOSER_ALLOW_SUPERUSER=1 COMPOSER_DISABLE_NETWORK=1
mkdir -p "$work/source/src" "$work/project"
printf '%s\n' '<?php namespace XorderFixture; final class Probe {}' > "$work/source/src/Probe.php"
printf '%s\n' '{"name":"xorder/reuse-fixture","autoload":{"psr-4":{"XorderFixture\\":"src/"}}}' > "$work/source/composer.json"
git -C "$work/source" init -q
git -C "$work/source" add .
git -C "$work/source" -c user.name=Fixture -c user.email=fixture@example.test commit -qm fixture
reference=$(git -C "$work/source" rev-parse HEAD)
php -r '$zip=new ZipArchive(); $zip->open($argv[2],ZipArchive::CREATE); foreach (["composer.json","src/Probe.php"] as $file) {$zip->addFile($argv[1]."/".$file,"package/".$file);} $zip->close();' "$work/source" "$work/package.zip"
php -r '$package=["name"=>"xorder/reuse-fixture","version"=>"1.0.0","autoload"=>["psr-4"=>["XorderFixture\\"=>"src/"]],"source"=>["type"=>"git","url"=>$argv[1],"reference"=>$argv[2]],"dist"=>["type"=>"zip","url"=>"file://".$argv[3],"reference"=>"dist-reference"]]; file_put_contents($argv[4],json_encode(["name"=>"xorder/fixture-consumer","require"=>["xorder/reuse-fixture"=>"1.0.0"],"repositories"=>[["type"=>"package","package"=>$package],["packagist.org"=>false]]]));' "$work/source" "$reference" "$work/package.zip" "$work/project/composer.json"
cd "$work/project"
composer update --prefer-dist --no-interaction --no-progress --no-scripts --no-plugins --no-audit
php "$root/examples/flowbite-xor/verify-composer.php" verify
php "$root/examples/flowbite-xor/verify-composer.php" fingerprint
# Composer labels even local Git transport as network; this sole source is a
# local absolute path, with Packagist disabled and no external repositories.
COMPOSER_DISABLE_NETWORK=0 composer reinstall xorder/reuse-fixture --prefer-source --no-interaction --no-progress --no-scripts --no-plugins
php "$root/examples/flowbite-xor/verify-composer.php" verify
# A stale installed record cannot be accepted just because vendor exists.
php -r '$path="vendor/composer/installed.json"; $data=json_decode(file_get_contents($path),true); $data["packages"][0]["version"]="0.0.0"; file_put_contents($path,json_encode($data));'
if php "$root/examples/flowbite-xor/verify-composer.php" verify; then
  echo 'A stale vendor package was incorrectly accepted' >&2
  exit 1
fi
