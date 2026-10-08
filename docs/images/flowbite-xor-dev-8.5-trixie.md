# flowbite-xor-dev/8.5-trixie

FrankenPHP/PHP 8.5 plus Node 22 for flowbite-xor development and Playwright test orchestration.

**Not available:** no verified public release. The following capabilities describe the intended profile.

Capabilities: `composer`, `frankenphp`, `native-build`, `node`, `npm`, `php`, `playwright-client`, `postgresql-client`, `symfony`, `worker-server`, `xdebug`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- Node and Playwright browsers are supplied by the flowbite-xor profile and its official companion, respectively.
- Playwright and application packages come from project lockfiles; browsers run in the version-matched official Playwright companion.
- Project dependencies and Caddy/worker configuration belong to the consuming repository.
- Use examples/flowbite-xor/run.sh to reuse repository-owned worker, Caddy, PHP and mount configuration without an in-container Docker socket.
- Xdebug is off by default; enable explicitly for debugging or coverage.
