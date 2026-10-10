# php-frankenphp/8.5-trixie v1.1.0

- Add checksum-pinned Infection 0.35.6 with per-process Xdebug and project-owned PHPUnit/configuration.
- Add opt-in PCOV coverage and reusable lock-owned PHPUnit/PHPStan tasks while retaining Xdebug coverage and default-disabled coverage hooks.
- Prepare an explicitly selected isolated PHPStan 2.3.0 with Symfony/PHPUnit extensions from a separate Composer lock.
- Accept a mounted multi-certificate PEM CA bundle; validate all certificates before replacing managed trust and retain single-certificate and root/user behavior.

Migration: Compatible additive update. Select a verified new digest before using library-php-tests; PHPUnit/PHPStan versions and configuration continue to come from the consuming project. Set COVERAGE_DRIVER=xdebug for Xdebug coverage. LIBRARY_CA_FILE accepts either a single certificate or a complete validated PEM bundle.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`php-frankenphp/8.5-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/php-frankenphp@sha256:c60aee9639a4e9b377c1f48e26dd5d351edc7f39673344debe1afb677c8b0572`.

Base/parent: `docker.io/dunglas/frankenphp:1-php8.5-trixie@sha256:06e3a490ff76db5bfd1c3c410677fc22bdbcb2c735c240cfa4111727d7641f38`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,219.2 MiB (1,278,378,978 bytes) |
| Build, cache export and image load | 208.84s |
| Public-artifact behavior and inventory verification | 31.33s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:45:01.446171Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/php-frankenphp@sha256:3ac6ca8f9ba8d4155eb7a83c5a512a344673a3d1f62073fd0b53730030aa457d`; 961.6 MiB in the same image store. Change: **+26.8%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:18:54.406682Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
