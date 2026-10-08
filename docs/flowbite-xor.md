# flowbite-xor development and tests

This optional profile targets the actual
[`xormania/flowbite-xor`](https://github.com/xormania/flowbite-xor) repository.
The acceptance fixture pins commit
[`15e520c`](https://github.com/xormania/flowbite-xor/tree/15e520c8d1bba19f721e92fc15ed3785ac0a130b),
inspected on 8 October 2026: Symfony 8.1, UX 3.5.1, PHP 8.5/FrankenPHP workers,
Node 22 and Playwright 1.58.2. Its kit lint/PHP/fresh-install jobs also test PHP
8.4; this profile does not replace that compatibility coverage.

| Part | Supplied by |
| --- | --- |
| PHP extensions, Composer, Symfony CLI, FrankenPHP/Caddy, APCu | `php-frankenphp/8.5-trixie` |
| Node 22 and npm | `flowbite-xor-dev/8.5-trixie`, derived from the exact FrankenPHP parent |
| Caddy/Mercure, worker mode, PHP ini, app entrypoint and source layout | The current flowbite-xor checkout's `demo/` configuration |
| Application and Playwright packages | `composer.lock` and `package-lock.json` using Composer install and npm ci |
| Browser binaries and fonts matching upstream screenshot baselines | Official `mcr.microsoft.com/playwright:v<locked-version>-noble` companion |

Definitions alone are not pullable releases. Select an available
`flowbite-xor-dev` digest from the [catalog](../catalog.json) after publication,
or build the root and derivative locally for validation:

```sh
python3 scripts/build.py php-frankenphp/8.5-trixie image-library-check:dev --children
```

From a clone of this library, with an existing flowbite-xor checkout:

```sh
export IMAGE='<verified flowbite-xor-dev digest_reference>'
export WORKSPACE='/absolute/path/to/flowbite-xor'
export FLOWBITE_PROJECT='my-flowbite-xor'
bash examples/flowbite-xor/run.sh up
bash examples/flowbite-xor/run.sh test tests/e2e/lab.calendar.spec.ts
bash examples/flowbite-xor/run.sh test --shard=2/3
bash examples/flowbite-xor/run.sh exec bash -c 'cd demo && bin/console tailwind:build'
bash examples/flowbite-xor/run.sh down
```

`up` starts the demo and browser, waits for health, syncs recipes and runs npm ci.
The repository's app entrypoint installs Composer dependencies on the first
start. Playwright's config builds stale Tailwind CSS before tests. There is no
host Node dependency. The host needs Docker/Compose and registry/dependency
access. Default host ports are loopback 8084/8444; override `HTTP_PORT`,
`HTTPS_PORT` and `HTTP3_PORT` when needed. Use a separate `FLOWBITE_PROJECT` for
each checkout. `down` preserves caches; `down --volumes` deliberately removes
this profile's disposable Caddy/home/demo-var volumes.

The browser shares the app container's network namespace. Its localhost port
3000 is reachable by the existing Playwright configuration without publishing
that port on the host. The runner uses `DEMO_URL=https://localhost` and
`PHP_BINARY=php`, so PHP helpers execute directly in the same app container.
`PW_BROWSER_SERVER=/bin/false` tells Playwright to reuse the already healthy
server and fail if it disappears. Neither container has a mounted Docker socket.
The version is read from package-lock.json and checked against package.json;
the official companion and its server package use that same exact version.

The profile overlays the repository's existing Compose files and mounts its
Caddyfile plus `10-app.ini`/`20-app.dev.ini`. That preserves worker execution,
Mercure directives and the current upload limits (2M per file, 8M per request).
It supplies a prebuilt development image instead of rebuilding the demo's PHP
toolchain. Exact CI artifact parity requires using the same selected library
digest in project CI; matching a PHP minor alone is insufficient. Keep the
repository's production image build separate from this development profile.

The app uses your UID/GID by default. `PUID=0 PGID=0` supports a root-owned
sandbox checkout. Only the named home, Caddy and demo-var cache volumes have
their ownership adjusted. The checkout supplies writable vendor/node_modules
directories for the chosen user. Set `CA_CERTIFICATE=/absolute/proxy-ca.pem`
for the shared [CA trust option](usage.md#network-access); the Node browser
companion gets the mounted certificate as an extra trusted CA as well.

The readiness recipe tests persistent workers, the shared PHP/native/TLS/user
contract, then starts the pinned real consuming repository and runs its calendar
and dropzone lab specs. It never updates screenshot baselines. A source update
to `tests/fixtures/flowbite-xor/consumer.json` deliberately updates that consumer
baseline; ordinary users run their current checkout.

References:

- [Inspected demo Dockerfile](https://github.com/xormania/flowbite-xor/blob/15e520c8d1bba19f721e92fc15ed3785ac0a130b/demo/Dockerfile)
- [Inspected CI and PHP version coverage](https://github.com/xormania/flowbite-xor/blob/15e520c8d1bba19f721e92fc15ed3785ac0a130b/.github/workflows/ci.yml)
- [Existing browser server and PHP helpers](https://github.com/xormania/flowbite-xor/blob/15e520c8d1bba19f721e92fc15ed3785ac0a130b/playwright.config.ts)
- [FrankenPHP image and non-root guidance](https://frankenphp.dev/docs/docker/)
- [Playwright version matching](https://playwright.dev/docs/docker#image-tags)
