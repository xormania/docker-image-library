# php-frankenphp/8.5-trixie v1.0.0

- Introduce a loaded FrankenPHP/PHP 8.5 development environment with APCu, worker-mode validation and the shared workspace/CA contract.

Migration: New optional line. Reuse the project Caddyfile and PHP configuration, and validate its worker and upload behavior before switching an existing pin.

Source: `b37b38aeb332765ee2beb889fdaf1030dfed4589` (`php-frankenphp/8.5-trixie/v1.0.0`).

Artifact: `ghcr.io/xormania/php-frankenphp@sha256:3ac6ca8f9ba8d4155eb7a83c5a512a344673a3d1f62073fd0b53730030aa457d`.

Base/parent: `docker.io/dunglas/frankenphp:1-php8.5-trixie@sha256:06e3a490ff76db5bfd1c3c410677fc22bdbcb2c735c240cfa4111727d7641f38`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37762155280).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 961.6 MiB (1,008,259,148 bytes) |
| Build, cache export and image load | 171.93s |
| Public-artifact behavior and inventory verification | 14.53s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:18:54.406682Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
