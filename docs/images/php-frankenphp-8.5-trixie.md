# php-frankenphp/8.5-trixie

Loaded PHP/Symfony development with FrankenPHP, Caddy and worker-mode HTTP execution.

**Not available:** no verified public release. The following capabilities describe the intended profile.

Capabilities: `php`, `composer`, `symfony`, `postgresql-client`, `native-build`, `xdebug`, `frankenphp`, `worker-server`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- Project dependencies and Caddy/worker configuration belong to the consuming repository.
- Xdebug is off by default; enable explicitly for debugging or coverage.
- Node and Playwright browsers are supplied by the flowbite-xor profile and its official companion, respectively.
