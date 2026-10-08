# php-dev/8.5-trixie

Loaded PHP and Symfony development, CLI tasks, unit and PostgreSQL integration tests.

Available revision: **1.0.1**. Pin:

```text
ghcr.io/xormania/php-dev@sha256:659f0c3ea9c1d84bf7c19b3ebaaef4bd16dec21dbb700ff637428186ecce5b2a
```

[Verification evidence](https://github.com/xormania/docker-image-library/actions/runs/37750479509); 2026-10-08T08:37:22.430540Z.

## Measured inventory — linux/amd64

Runtime: 8.5.11; OS: Debian GNU/Linux 13 (trixie).

| Tool | Version |
| --- | --- |
| bash | GNU bash, version 5.2.37(1)-release (x86_64-pc-linux-gnu) |
| composer | Composer version 2.10.3 2026-08-27 13:34:23 |
| curl | curl 8.14.1 (x86_64-pc-linux-gnu) libcurl/8.14.1 OpenSSL/3.5.7 zlib/1.3.1 brotli/1.1.0 zstd/1.5.7 libidn2/2.3.8 libpsl/0.21.2 libssh2/1.11.1 nghttp2/1.64.0 nghttp3/1.8.0 librtmp/2.3 OpenLDAP/2.6.10 |
| gh | gh version 2.46.0 (2025-01-13 Debian 2.46.0-3) |
| git | git version 2.47.3 |
| jq | jq-1.7 |
| php | PHP 8.5.11 (cli) (built: Oct  6 2026 01:22:31) (NTS) |
| psql | psql (PostgreSQL) 17.11 (Debian 17.11-0+deb13u1) |
| rg | ripgrep 14.1.1 |
| symfony | Symfony CLI version 5.22.0 (c) 2021-2026 Fabien Potencier (2026-10-06T20:55:04Z - stable) |

Extensions: `bcmath`, `core`, `ctype`, `curl`, `date`, `dom`, `fileinfo`, `filter`, `gd`, `hash`, `iconv`, `intl`, `json`, `lexbor`, `libxml`, `mbstring`, `mysqli`, `mysqlnd`, `openssl`, `pcntl`, `pcre`, `pdo`, `pdo_mysql`, `pdo_pgsql`, `pdo_sqlite`, `pgsql`, `phar`, `posix`, `random`, `readline`, `redis`, `reflection`, `session`, `simplexml`, `sockets`, `sodium`, `spl`, `sqlite3`, `standard`, `tokenizer`, `uri`, `xdebug`, `xml`, `xmlreader`, `xmlwriter`, `zend opcache`, `zip`, `zlib`.

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 903.5 MiB (947,429,837 bytes) |
| Build, cache export and image load | 240.39s |
| Public-artifact behavior and inventory verification | 9.06s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37750479509); 2026-10-08T08:37:22.375659Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

[Release notes](../releases/php-dev-8.5-trixie-v1.0.1.md).

Capabilities: `php`, `composer`, `symfony`, `postgresql-client`, `native-build`, `xdebug`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- Project PHP dependencies come from Composer lockfiles.
- Xdebug is off by default; enable with XDEBUG_MODE=coverage or debug.
- No PHP-FPM, web server daemon, or Node toolchain is supplied.
