# php-serena/8.5-trixie

Prepared Serena v2 REPL and PHPactor for PHP/Symfony source work over stdio MCP, verified against flowbite-xor.

Available revision: **1.0.0**. Pin:

```text
ghcr.io/xormania/php-serena@sha256:9efe7bb1989723578a3eed03a2ee5802145af1efaba4a1297dd994d5abe62718
```

[Verification evidence](https://github.com/xormania/xorder/actions/runs/38030147899); 2026-10-10T06:17:43.699213Z.

## Measured inventory — linux/amd64

Runtime: 8.5.11; OS: Debian GNU/Linux 13 (trixie).

| Tool | Version |
| --- | --- |
| bash | GNU bash, version 5.2.37(1)-release (x86_64-pc-linux-gnu) |
| composer | Composer version 2.10.3 2026-08-27 13:34:23 |
| curl | curl 8.14.1 (x86_64-pc-linux-gnu) libcurl/8.14.1 OpenSSL/3.5.7 zlib/1.3.1 brotli/1.1.0 zstd/1.5.7 libidn2/2.3.8 libpsl/0.21.2 libssh2/1.11.1 nghttp2/1.64.0 nghttp3/1.8.0 librtmp/2.3 OpenLDAP/2.6.10 |
| gh | gh version 2.46.0 (2025-01-13 Debian 2.46.0-3) |
| git | git version 2.47.3 |
| infection | Infection - PHP Mutation Testing Framework version 0.35.6 |
| jq | jq-1.7 |
| library-php-coverage | xorder PHP coverage runner 1.0.0 |
| library-php-tests | xorder PHP test runner 1.0.0 |
| library-serena | Serena 2.0.0.dev0 (b79e2a55, PHPactor 2025.12.21.1) |
| php | PHP 8.5.11 (cli) (built: Oct  6 2026 01:22:31) (NTS) |
| phpactor | Phpactor 2025.12.21.1 |
| phpstan-isolated | PHPStan - PHP Static Analysis Tool 2.3.0 |
| psql | psql (PostgreSQL) 17.11 (Debian 17.11-0+deb13u1) |
| rg | ripgrep 14.1.1 |
| symfony | Symfony CLI version 5.22.0 (c) 2021-2026 Fabien Potencier (2026-10-06T20:55:04Z - stable) |
| uv | uv 0.12.19 (x86_64-unknown-linux-musl) |

Extensions: `bcmath`, `core`, `ctype`, `curl`, `date`, `dom`, `fileinfo`, `filter`, `gd`, `hash`, `iconv`, `intl`, `json`, `lexbor`, `libxml`, `mbstring`, `mysqli`, `mysqlnd`, `openssl`, `pcntl`, `pcov`, `pcre`, `pdo`, `pdo_mysql`, `pdo_pgsql`, `pdo_sqlite`, `pgsql`, `phar`, `posix`, `random`, `readline`, `redis`, `reflection`, `session`, `simplexml`, `sockets`, `sodium`, `spl`, `sqlite3`, `standard`, `tokenizer`, `uri`, `xdebug`, `xml`, `xmlreader`, `xmlwriter`, `zend opcache`, `zip`, `zlib`.

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,087.2 MiB (1,139,965,670 bytes) |
| Build, cache export and image load | 36.85s |
| Public-artifact behavior and inventory verification | 91.02s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38030147899); 2026-10-10T06:17:43.640904Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

[Release notes](../releases/php-serena-8.5-trixie-v1.0.0.md).

Capabilities: `composer`, `mutation-testing`, `native-build`, `offline-php-semantic-tools`, `pcov`, `php`, `php-testing`, `phpactor`, `phpstan-isolated`, `postgresql-client`, `serena-v2-repl`, `symfony`, `xdebug`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Serena MCP and Symfony recipe](../serena.md) · [Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- No PHP-FPM, web server daemon, or Node toolchain is supplied.
- PCOV is disabled by default. library-php-coverage pcov isolates Xdebug for each CLI process; library-php-tests uses project-locked PHPUnit and PHPStan, not global test packages.
- PHP semantic operations are backed by PHPactor; Twig and Symfony container/service semantics are not established by PHP symbol tests.
- Project PHP dependencies come from Composer lockfiles.
- Serena is pinned to the tested v2 beta revision b79e2a55f9d4072084977dd35bd07d31146d88b9.
- The REPL can execute Python with container permissions. The standalone runner does not implement Agentscient role permissions or coordination.
- The consuming project owns its Composer dependencies. Prepared language-server startup needs no runtime downloads.
- The public runner mounts source read-only by default; pass --write explicitly for trusted editing sessions.
- The runner uses temporary session state. REPL variables, indexes and new memories do not survive process restart.
- Xdebug is off by default; enable with XDEBUG_MODE=coverage or debug.
