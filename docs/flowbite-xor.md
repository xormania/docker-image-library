# flowbite-xor development and tests

This optional profile targets the actual
[`xormania/flowbite-xor`](https://github.com/xormania/flowbite-xor) repository.
The acceptance fixture pins commit
[`c8878af`](https://github.com/xormania/flowbite-xor/tree/c8878af66897d8c10af694050a7a588166942117),
inspected on 8 October 2026: Symfony 8.1, UX 3.5.1, PHP 8.5/FrankenPHP workers,
Node 22, Playwright 1.58.2 and Tailwind v4.3.3. Both PHP 8.4 and 8.5 profiles
exercise this baseline, including the PHPUnit suite. Choose 8.4 for the
minimum-version checks and 8.5 for the browser CI runtime.

| Part | Supplied by |
| --- | --- |
| PHP extensions, Composer, Symfony CLI, FrankenPHP/Caddy, APCu | `php-frankenphp/8.4-trixie` or `8.5-trixie` |
| Node 22, npm and checksum-verified Tailwind v4.3.3 CLI | `flowbite-xor-dev/8.4-trixie` or `8.5-trixie`, derived from the exact FrankenPHP parent |
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
bash examples/flowbite-xor/run.sh phpunit
PHPUNIT_XDEBUG_MODE=coverage bash examples/flowbite-xor/run.sh phpunit --coverage-clover var/coverage.xml
bash examples/flowbite-xor/run.sh exec bash -c 'cd demo && bin/console tailwind:build'
bash examples/flowbite-xor/run.sh down
```

`up` starts the demo and browser, waits for health, syncs recipes, seeds the
matching cached Tailwind binary and runs npm ci.
The repository's app entrypoint installs Composer dependencies on the first
start. Playwright's config builds stale Tailwind CSS before tests. There is no
host Node dependency. The host needs Docker/Compose and registry/dependency
access. Default host ports are loopback 8084/8444; override `HTTP_PORT`,
`HTTPS_PORT` and `HTTP3_PORT` when needed. Use a separate `FLOWBITE_PROJECT` for
each checkout. `down` preserves caches; `down --volumes` deliberately removes
this profile's disposable Caddy/home/demo-var volumes.

Xdebug is installed and stays off for the server and ordinary PHPUnit runs.
`PHPUNIT_XDEBUG_MODE=coverage` enables it only in the PHPUnit exec process,
including when the containers were started with Xdebug off. Reports live under
`demo/var` in the named cache volume; retrieve one with
`run.sh exec cat demo/var/coverage.xml`. PHPUnit comes from the demo lockfile.
The runner sets `CREATE_SNAPSHOTS=false`, matching CI.

The image stores a checksum-verified Tailwind v4.3.3 binary at `/opt/tailwind`.
After Composer is ready, `up` reads the demo's resolved tailwind-bundle config
and copies the binary to `demo/var/tailwind/v4.3.3/tailwindcss-linux-x64`.
Fresh worktrees and cache volumes reuse those image bytes. A different pinned
version, explicit binary path or platform keeps the bundle's normal behavior.
The project configuration remains authoritative. Use the new 8.4 image or the
8.5 v1.1.0 image with this runner; the older 8.5 v1.0.0 image has no cache helper.

For a linked Git worktree, export `WORKTREE_GIT=1` before all runner commands:

```sh
export WORKSPACE='/absolute/path/to/flowbite-worktree'
export WORKTREE_GIT=1
export FLOWBITE_PROJECT='my-flowbite-worktree'
bash examples/flowbite-xor/run.sh up
bash examples/flowbite-xor/run.sh exec git status
```

This option requires host Git and mounts the common repository metadata,
including the selected worktree's private metadata, read-only at its host path.
It overlays `/app/.git` with an absolute pointer stored in the host user's
`$XDG_CACHE_HOME/docker-image-library/worktrees` (default `$HOME/.cache`).
The checkout's `.git` file is unchanged, including relative pointers. The
cached pointer survives container restarts. Git reads work inside the container;
run Git writes such as add/commit on the host. Ordinary checkouts need no option.

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

The readiness recipe tests persistent workers and executed-line Xdebug coverage
plus the shared PHP/native/TLS/user contract. It then starts the pinned real
consuming repository as a linked Git worktree, checks Git access, builds Tailwind
from the seeded binary, runs PHPUnit with a nonempty Clover coverage report,
and runs calendar, dropzone, both data-table and both editor lab specs. It never updates screenshot baselines. A source update
to `tests/fixtures/flowbite-xor/consumer.json` deliberately updates that consumer
baseline; ordinary users run their current checkout.

References:

- [Inspected demo Dockerfile](https://github.com/xormania/flowbite-xor/blob/c8878af66897d8c10af694050a7a588166942117/demo/Dockerfile)
- [Inspected CI and PHP version coverage](https://github.com/xormania/flowbite-xor/blob/c8878af66897d8c10af694050a7a588166942117/.github/workflows/ci.yml)
- [Existing browser server and PHP helpers](https://github.com/xormania/flowbite-xor/blob/c8878af66897d8c10af694050a7a588166942117/playwright.config.ts)
- [FrankenPHP image and non-root guidance](https://frankenphp.dev/docs/docker/)
- [Playwright version matching](https://playwright.dev/docs/docker#image-tags)
