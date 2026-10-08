#!/usr/bin/env bash
# Verify the downloaded PHAR before executing it. The publisher appends its root.
set -euo pipefail

if [[ $# != 1 ]]; then
    printf 'Usage: %s DIRECTORY_WITH_COMPOSER_PHAR\n' "$0" >&2
    exit 2
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo_dir=$(CDPATH= cd -- "$script_dir/../.." && pwd)
artifact_dir=$(CDPATH= cd -- "$1" && pwd)
phar="$artifact_dir/composer.phar"

command -v php >/dev/null || { printf 'Missing prerequisite: PHP CLI\n' >&2; exit 1; }
php -r 'if (PHP_VERSION_ID < 70205 || !extension_loaded("Phar")) {
    fwrite(STDERR, "Composer requires PHP CLI >= 7.2.5 with PHAR support\n"); exit(1);
}'

# A mismatch must stop here, before running downloaded code.
expected_version=$(python3 - "$repo_dir" "$phar" <<'PY'
import hashlib
import json
import pathlib
import sys

definition = json.loads((pathlib.Path(sys.argv[1]) / "artifacts/binary/composer/definition.json").read_text())
artifact = pathlib.Path(sys.argv[2])
if not artifact.is_file() or artifact.is_symlink():
    raise SystemExit("Missing regular Composer PHAR")
if hashlib.sha256(artifact.read_bytes()).hexdigest() != definition["details"]["sha256"]:
    raise SystemExit("Composer PHAR checksum mismatch")
print(definition["details"]["upstream_version"])
PY
)

actual_version=$(php "$phar" --no-ansi --version)
case "$actual_version" in
    "Composer version $expected_version "*) ;;
    *) printf 'Unexpected Composer version: %s\n' "$actual_version" >&2; exit 1 ;;
esac

# Official PHARs include Composer's upstream license; preserve these bytes.
php -r '
$license = file_get_contents("phar://" . $argv[1] . "/LICENSE");
if ($license === false || strpos($license, "Nils Adermann, Jordi Boggiano") === false
    || strpos($license, "Permission is hereby granted") === false) {
    fwrite(STDERR, "Composer upstream license missing from PHAR\n"); exit(1);
}' "$phar"

scratch_dir=$(mktemp -d)
trap 'rm -rf -- "$scratch_dir"' EXIT
cp "$repo_dir/tests/fixtures/php/composer.json" "$repo_dir/tests/fixtures/php/composer.lock" "$scratch_dir/"
mkdir "$scratch_dir/home"
COMPOSER_DISABLE_NETWORK=1 COMPOSER_HOME="$scratch_dir/home" \
    php "$phar" --no-ansi --no-interaction --no-plugins --no-scripts \
    --working-dir="$scratch_dir" validate --strict --no-check-publish

printf 'Verified %s; locked consumer metadata valid without network\n' "$actual_version"
