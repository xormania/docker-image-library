# php-browser/8.4-trixie

PHP and Symfony development plus real Chromium and Panther browser tests.

Available revision: **1.2.1**. Pin:

```text
ghcr.io/xormania/php-browser@sha256:730e67ff5d712550b7cce91387e9891e13092af05f70ae719f55f4c12f0a7f05
```

[Verification evidence](https://github.com/xormania/xorder/actions/runs/38002658722); 2026-10-09T23:13:05.960516Z.

## Measured inventory — linux/amd64

Runtime: 8.4.26; OS: Debian GNU/Linux 13 (trixie).

| Tool | Version |
| --- | --- |
| bash | GNU bash, version 5.2.37(1)-release (x86_64-pc-linux-gnu) |
| chromedriver | ChromeDriver 154.0.8037.92 (334b65d254ccc35df4fca82706d1753227b01039-refs/branch-heads/8037@{#1589}) |
| chromium | Chromium 154.0.8037.92 built on Debian GNU/Linux 13 (trixie) |
| composer | Composer version 2.10.3 2026-08-27 13:34:23 |
| curl | curl 8.14.1 (x86_64-pc-linux-gnu) libcurl/8.14.1 OpenSSL/3.5.7 zlib/1.3.1 brotli/1.1.0 zstd/1.5.7 libidn2/2.3.8 libpsl/0.21.2 libssh2/1.11.1 nghttp2/1.64.0 nghttp3/1.8.0 librtmp/2.3 OpenLDAP/2.6.10 |
| gh | gh version 2.46.0 (2025-01-13 Debian 2.46.0-3) |
| git | git version 2.47.3 |
| infection | Infection - PHP Mutation Testing Framework version 0.35.6 |
| jq | jq-1.7 |
| library-php-coverage | xorder PHP coverage runner 1.0.0 |
| library-php-tests | xorder PHP test runner 1.0.0 |
| php | PHP 8.4.26 (cli) (built: Oct  6 2026 01:25:39) (NTS) |
| phpstan-isolated | PHPStan - PHP Static Analysis Tool 2.3.0 |
| psql | psql (PostgreSQL) 17.11 (Debian 17.11-0+deb13u1) |
| rg | ripgrep 14.1.1 |
| symfony | Symfony CLI version 5.22.0 (c) 2021-2026 Fabien Potencier (2026-10-06T20:55:04Z - stable) |

Extensions: `bcmath`, `core`, `ctype`, `curl`, `date`, `dom`, `fileinfo`, `filter`, `gd`, `hash`, `iconv`, `intl`, `json`, `libxml`, `mbstring`, `mysqli`, `mysqlnd`, `openssl`, `pcntl`, `pcov`, `pcre`, `pdo`, `pdo_mysql`, `pdo_pgsql`, `pdo_sqlite`, `pgsql`, `phar`, `posix`, `random`, `readline`, `redis`, `reflection`, `session`, `simplexml`, `sockets`, `sodium`, `spl`, `sqlite3`, `standard`, `tokenizer`, `xdebug`, `xml`, `xmlreader`, `xmlwriter`, `zend opcache`, `zip`, `zlib`.

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,615.5 MiB (1,693,972,416 bytes) |
| Build, cache export and image load | 56.74s |
| Public-artifact behavior and inventory verification | 28.84s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38002658722); 2026-10-09T23:13:05.903283Z.

Plan about **4 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.2.0, `ghcr.io/xormania/php-browser@sha256:f14c53bd6c4c27b54b1415d6913947ec359c28e003d27292ef930d1c9b646464`; 1,834.5 MiB in the same image store. Change: **-11.9%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:46:44.078214Z.

[Release notes](../releases/php-browser-8.4-trixie-v1.2.1.md).

Capabilities: `browser`, `composer`, `mutation-testing`, `native-build`, `panther`, `pcov`, `php`, `php-testing`, `phpstan-isolated`, `postgresql-client`, `symfony`, `xdebug`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- Chromium may need --no-sandbox where the host prohibits sandbox namespaces. Use only for trusted development content.
- No PHP-FPM, web server daemon, or Node toolchain is supplied.
- Node is not included; request a separate capability when the project requires it.
- PCOV is disabled by default. library-php-coverage pcov isolates Xdebug for each CLI process; library-php-tests uses project-locked PHPUnit and PHPStan, not global test packages.
- Project PHP dependencies come from Composer lockfiles.
- Xdebug is off by default; enable with XDEBUG_MODE=coverage or debug.
