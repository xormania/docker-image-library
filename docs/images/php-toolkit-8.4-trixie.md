# php-toolkit/8.4-trixie

Isolated Symfony UX Toolkit kit validation and clean locked Symfony 7.4 recipe-install applications, prepared for restricted consumer networks.

**Not available:** no verified public release. The following capabilities describe the intended profile.

Capabilities: `composer`, `native-build`, `pcov`, `php`, `php-testing`, `phpstan-isolated`, `postgresql-client`, `prepared-composer-dependencies`, `symfony`, `symfony-toolkit-baseline`, `ux-toolkit-validation`, `xdebug`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Toolkit validation and fresh-app recipe](../php-toolkit.md) · [Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- No PHP-FPM, web server daemon, or Node toolchain is supplied.
- PCOV is disabled by default. library-php-coverage pcov isolates Xdebug for each CLI process; library-php-tests uses project-locked PHPUnit and PHPStan, not global test packages.
- Prepared projects do not select PHPUnit or PHPStan versions for the consuming project. Fresh baselines contain no generated kit recipes or application cache.
- Prepared validator and baseline dependencies belong to their committed xorder lockfiles, not the consuming application's lockfile.
- Project PHP dependencies come from Composer lockfiles.
- The clean baseline is Symfony 7.4 with Symfony UX Toolkit 3.5.1; a different baseline requires an explicitly updated lock and image revision.
- Xdebug is off by default; enable with XDEBUG_MODE=coverage or debug.
