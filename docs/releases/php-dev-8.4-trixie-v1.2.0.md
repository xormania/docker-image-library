# php-dev/8.4-trixie v1.2.0

- Add checksum-pinned Infection 0.35.6 with per-process Xdebug and project-owned PHPUnit/configuration.
- Add opt-in PCOV coverage and reusable lock-owned PHPUnit/PHPStan tasks while retaining Xdebug coverage and default-disabled coverage hooks.
- Prepare an explicitly selected isolated PHPStan 2.3.0 with Symfony/PHPUnit extensions from a separate Composer lock.
- Accept a mounted multi-certificate PEM CA bundle; validate all certificates before replacing managed trust and retain single-certificate and root/user behavior.

Migration: Compatible additive update. Select a verified new digest before using library-php-tests; PHPUnit/PHPStan versions and configuration continue to come from the consuming project. Set COVERAGE_DRIVER=xdebug for Xdebug coverage. LIBRARY_CA_FILE accepts either a single certificate or a complete validated PEM bundle.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`php-dev/8.4-trixie/v1.2.0`).

Artifact: `ghcr.io/xormania/php-dev@sha256:bed7ada0f7a6d3d9ff119125afc87c6d3fd96ac29fd1210e6f52f516692c6510`.

Base/parent: `docker.io/library/php:8.4-cli-trixie@sha256:1d2cf2b7d715b5b3aa959f0150ccbcc7b71e0181b637e443abf40a7fb56bf79a`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,131.3 MiB (1,186,278,310 bytes) |
| Build, cache export and image load | 167.39s |
| Public-artifact behavior and inventory verification | 27.99s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:44:08.357134Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

Size baseline: v1.1.0, `ghcr.io/xormania/php-dev@sha256:d3f9483df7c3f30837dab772acaa53f55ab1af5b7bdb21af8d320d80f4bd9029`; 873.7 MiB in the same image store. Change: **+29.5%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:18:18.047279Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
