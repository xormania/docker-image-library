# php-dev/8.5-trixie v1.2.0

- Add checksum-pinned Infection 0.35.6 with per-process Xdebug and project-owned PHPUnit/configuration.
- Add opt-in PCOV coverage and reusable lock-owned PHPUnit/PHPStan tasks while retaining Xdebug coverage and default-disabled coverage hooks.
- Prepare an explicitly selected isolated PHPStan 2.3.0 with Symfony/PHPUnit extensions from a separate Composer lock.
- Accept a mounted multi-certificate PEM CA bundle; validate all certificates before replacing managed trust and retain single-certificate and root/user behavior.

Migration: Compatible additive update. Select a verified new digest before using library-php-tests; PHPUnit/PHPStan versions and configuration continue to come from the consuming project. Set COVERAGE_DRIVER=xdebug for Xdebug coverage. LIBRARY_CA_FILE accepts either a single certificate or a complete validated PEM bundle.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`php-dev/8.5-trixie/v1.2.0`).

Artifact: `ghcr.io/xormania/php-dev@sha256:766e2d2ffe1b043160a0fb9d67825982a87948a4b4e13b41a84298014b34f49d`.

Base/parent: `docker.io/library/php:8.5-cli-trixie@sha256:01a109229f4465bc9ef042d9198f09a4d9da7775a825dbd8572dcdbd8756c4d3`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,161.1 MiB (1,217,539,725 bytes) |
| Build, cache export and image load | 200.90s |
| Public-artifact behavior and inventory verification | 29.35s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:44:48.585089Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

Size baseline: v1.1.0, `ghcr.io/xormania/php-dev@sha256:53a1728c55ad8059184ef2ccc0bfb5c62e1b97c3cda87f14ae0897e46cf1317d`; 903.5 MiB in the same image store. Change: **+28.5%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:18:34.043560Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
