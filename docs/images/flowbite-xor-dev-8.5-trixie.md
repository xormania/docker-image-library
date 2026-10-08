# flowbite-xor-dev/8.5-trixie

FrankenPHP/PHP 8.4 or 8.5 plus Node 22 and a pinned Tailwind CLI for flowbite-xor development and Playwright orchestration.

Available revision: **1.1.0**. Pin:

```text
ghcr.io/xormania/flowbite-xor-dev@sha256:23f4b1755d665c3d0a7fbedebc6fcc6da0edef7ea9a0d71898bee3345ba77df0
```

[Verification evidence](https://github.com/xormania/docker-image-library/actions/runs/37852642503); 2026-10-08T22:23:57.331631Z.

## Measured inventory — linux/amd64

Runtime: 8.5.11; OS: Debian GNU/Linux 13 (trixie).

| Tool | Version |
| --- | --- |
| bash | GNU bash, version 5.2.37(1)-release (x86_64-pc-linux-gnu) |
| composer | Composer version 2.10.3 2026-08-27 13:34:23 |
| curl | curl 8.14.1 (x86_64-pc-linux-gnu) libcurl/8.14.1 OpenSSL/3.5.7 zlib/1.3.1 brotli/1.1.0 zstd/1.5.7 libidn2/2.3.8 libpsl/0.21.2 libssh2/1.11.1 nghttp2/1.64.0 nghttp3/1.8.0 librtmp/2.3 OpenLDAP/2.6.10 |
| frankenphp | FrankenPHP v1.13.0 PHP 8.5.11 Caddy v2.11.7 h1:yj0Y4fYZGPkSvibBJ1sTWE33xC0fxztVyXEW5iIdUT4= |
| gh | gh version 2.46.0 (2025-01-13 Debian 2.46.0-3) |
| git | git version 2.47.3 |
| jq | jq-1.7 |
| node | v22.23.3 |
| npm | 10.9.9 |
| php | PHP 8.5.11 (cli) (built: Oct  6 2026 01:23:29) (ZTS) |
| psql | psql (PostgreSQL) 17.11 (Debian 17.11-0+deb13u1) |
| rg | ripgrep 14.1.1 |
| symfony | Symfony CLI version 5.22.0 (c) 2021-2026 Fabien Potencier (2026-10-06T20:55:04Z - stable) |
| tailwindcss | ≈ tailwindcss v4.3.3 |

Extensions: `apcu`, `bcmath`, `core`, `ctype`, `curl`, `date`, `dom`, `fileinfo`, `filter`, `gd`, `hash`, `iconv`, `intl`, `json`, `lexbor`, `libxml`, `mbstring`, `mysqli`, `mysqlnd`, `openssl`, `pcntl`, `pcre`, `pdo`, `pdo_mysql`, `pdo_pgsql`, `pdo_sqlite`, `pgsql`, `phar`, `posix`, `random`, `readline`, `redis`, `reflection`, `session`, `simplexml`, `sockets`, `sodium`, `spl`, `sqlite3`, `standard`, `tokenizer`, `uri`, `xdebug`, `xml`, `xmlreader`, `xmlwriter`, `zend opcache`, `zip`, `zlib`.

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,198.2 MiB (1,256,357,028 bytes) |
| Build, cache export and image load | 49.45s |
| Public-artifact behavior and inventory verification | 84.54s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37852642503); 2026-10-08T22:23:57.290148Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/flowbite-xor-dev@sha256:a3ad6f61bb56d39060a060c7dbd99c1a65ae32f0ae7d9d7e9df0f6258afca474`; 1,091.6 MiB in the same image store. Change: **+9.8%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:21:51.379666Z.

[Release notes](../releases/flowbite-xor-dev-8.5-trixie-v1.1.0.md).

Capabilities: `composer`, `frankenphp`, `native-build`, `node`, `npm`, `php`, `playwright-client`, `postgresql-client`, `symfony`, `tailwind-cli`, `worker-server`, `xdebug`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- Node and Playwright browsers are supplied by the flowbite-xor profile and its official companion, respectively.
- Playwright and application packages come from project lockfiles; browsers run in the version-matched official Playwright companion.
- Project dependencies and Caddy/worker configuration belong to the consuming repository.
- The cached Tailwind binary is seeded only when its version and platform match the consuming project configuration.
- Use examples/flowbite-xor/run.sh to reuse repository-owned worker, Caddy, PHP and mount configuration without an in-container Docker socket.
- Xdebug is off by default; enable explicitly for debugging or coverage.
