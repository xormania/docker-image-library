# php-frankenphp/8.4-trixie v1.1.0

- Add checksum-pinned Infection 0.35.6 with per-process Xdebug and project-owned PHPUnit/configuration.
- Add opt-in PCOV coverage and reusable lock-owned PHPUnit/PHPStan tasks while retaining Xdebug coverage and default-disabled coverage hooks.
- Prepare an explicitly selected isolated PHPStan 2.3.0 with Symfony/PHPUnit extensions from a separate Composer lock.
- Accept a mounted multi-certificate PEM CA bundle; validate all certificates before replacing managed trust and retain single-certificate and root/user behavior.

Migration: Compatible additive update. Select a verified new digest before using library-php-tests; PHPUnit/PHPStan versions and configuration continue to come from the consuming project. Set COVERAGE_DRIVER=xdebug for Xdebug coverage. LIBRARY_CA_FILE accepts either a single certificate or a complete validated PEM bundle.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`php-frankenphp/8.4-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/php-frankenphp@sha256:6c5edb921d745e5dbc8fdff454c557360c5a789d5a82aa7b351b6419176050e8`.

Base/parent: `docker.io/dunglas/frankenphp:1-php8.4-trixie@sha256:2fd4a848c05bf4902a3d9ff1a4991c2f4d4665df0567aee21be4eee120ded038`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,189.4 MiB (1,247,227,779 bytes) |
| Build, cache export and image load | 178.72s |
| Public-artifact behavior and inventory verification | 28.29s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:44:22.594975Z.

Plan about **3 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/php-frankenphp@sha256:9cd194f21ef4600fbba343fa5a471528fff3f6db6a1889ea280fb58d68cf30d2`; 931.8 MiB in the same image store. Change: **+27.6%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37852642503); 2026-10-08T22:22:56.838890Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
