#!/usr/bin/env bash
# Verify actual TLS clients and explicit root execution, on every profile.
set -euo pipefail
image=${1:?Supply image}
root=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d)
server=
cleanup() {
  [ -z "$server" ] || kill "$server" 2>/dev/null || true
  if [ -d "$work/workspace" ]; then
    docker run --rm -e PUID=0 -e PGID=0 --mount "type=bind,src=$work/workspace,dst=/workspace" "$image" \
      bash -c 'rm -f /workspace/root-proof; chown "$1:$2" /workspace' -- "$(id -u)" "$(id -g)" >/dev/null 2>&1 || true
  fi
  rm -rf "$work"
}
trap cleanup EXIT
openssl req -x509 -newkey rsa:2048 -nodes -keyout "$work/ca.key" -out "$work/ca.crt" -days 1 \
  -subj /CN=LibraryFixtureCA -addext basicConstraints=critical,CA:TRUE >/dev/null 2>&1
openssl req -newkey rsa:2048 -nodes -keyout "$work/server.key" -out "$work/server.csr" -subj /CN=localhost >/dev/null 2>&1
printf 'subjectAltName=DNS:localhost,IP:127.0.0.1\n' > "$work/server.ext"
openssl x509 -req -in "$work/server.csr" -CA "$work/ca.crt" -CAkey "$work/ca.key" -CAcreateserial \
  -out "$work/server.crt" -days 1 -extfile "$work/server.ext" >/dev/null 2>&1
mkdir "$work/source"
git -C "$work/source" init -q
git -C "$work/source" -c user.name=Fixture -c user.email=fixture@example.test commit --allow-empty -qm Fixture
git clone --bare -q "$work/source" "$work/repo.git"
git -C "$work/repo.git" update-server-info
printf 'trusted\n' > "$work/proof.txt"
python3 "$root/server.py" "$work" > "$work/server.log" 2>&1 & server=$!
for attempt in {1..50}; do [ ! -f "$work/port" ] || break; sleep .1; done
port=$(cat "$work/port")
python3 - "$work" "$port" <<'PY'
import json, sys, zipfile
from pathlib import Path
root=Path(sys.argv[1]); url=f'https://localhost:{sys.argv[2]}'
with zipfile.ZipFile(root/'package.zip', 'w') as archive:
    archive.writestr('proof.txt', 'Composer downloaded this over verified HTTPS.\n')
package={'name':'fixture/proof','version':'1.0.0','type':'library','dist':{'type':'zip','url':url+'/package.zip'}}
(root/'packages.json').write_text(json.dumps({'packages':{'fixture/proof':{'1.0.0':package}}}))
PY
docker run --rm --network host "$image" bash -c '! curl --fail --silent "https://localhost:$1/proof.txt"' -- "$port"
docker run --rm --network host -e LIBRARY_CA_FILE=/run/ca.pem \
  --mount "type=bind,src=$work/ca.crt,dst=/run/ca.pem,readonly" "$image" bash -c '
  test "$(id -u)" = 1000
  curl --fail --silent "https://localhost:$1/proof.txt" | rg "^trusted$"
  git clone -q "https://localhost:$1/repo.git" "$HOME/proof-repo"
  if command -v composer >/dev/null; then
    mkdir "$HOME/composer-tls"; cd "$HOME/composer-tls"
    php -r '\''echo json_encode(["repositories"=>[["type"=>"composer","url"=>$argv[1]],["packagist.org"=>false]],"require"=>["fixture/proof"=>"1.0.0"]]);'\'' "https://localhost:$1" > composer.json
    composer install --no-interaction --no-progress --no-audit
    test -f vendor/fixture/proof/proof.txt
  fi
  if command -v node >/dev/null; then
    node -e '\''require("https").get(process.argv[1],r=>{if(r.statusCode!==200)process.exit(1);r.resume()}).on("error",e=>{console.error(e);process.exit(1)})'\'' "https://localhost:$1/proof.txt"
  fi' -- "$port"
printf 'invalid\n' > "$work/bad.pem"
if docker run --rm -e LIBRARY_CA_FILE=/run/ca.pem --mount "type=bind,src=$work/bad.pem,dst=/run/ca.pem,readonly" "$image" true; then
  echo 'Invalid certificate was accepted' >&2; exit 1
fi
if docker run --rm --user 1000 -e LIBRARY_CA_FILE=/run/ca.pem --mount "type=bind,src=$work/ca.crt,dst=/run/ca.pem,readonly" "$image" true; then
  echo 'A non-root entrypoint silently ignored system trust setup' >&2; exit 1
fi
mkdir "$work/workspace"
docker run --rm -e PUID=0 -e PGID=0 --mount "type=bind,src=$work/workspace,dst=/workspace" "$image" bash -c 'chown 0:0 /workspace; chmod 755 /workspace; touch root-proof; test "$(id -u)" = 0'
test "$(stat -c %u "$work/workspace/root-proof")" = 0
echo 'Proxy CA, TLS clients, validation errors and PUID=0 passed'
