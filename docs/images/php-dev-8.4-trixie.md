# php-dev/8.4-trixie

Loaded PHP and Symfony development, CLI tasks, unit and PostgreSQL integration tests.

**Not available:** no verified public release. The following capabilities describe the intended profile.

Capabilities: `php`, `composer`, `symfony`, `postgresql-client`, `native-build`, `xdebug`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- Project PHP dependencies come from Composer lockfiles.
- Xdebug is off by default; enable with XDEBUG_MODE=coverage or debug.
- No PHP-FPM, web server daemon, or Node toolchain is supplied.
