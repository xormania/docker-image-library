# php-browser/8.4-trixie v1.2.0

- Add opt-in PCOV coverage and reusable lock-owned PHPUnit/PHPStan tasks while retaining Xdebug coverage and default-disabled coverage hooks.
- Accept a mounted multi-certificate PEM CA bundle; validate all certificates before replacing managed trust and retain single-certificate and root/user behavior.

Migration: Compatible additive update. Select a verified new digest before using library-php-tests; PHPUnit/PHPStan versions and configuration continue to come from the consuming project. Set COVERAGE_DRIVER=xdebug for Xdebug coverage. LIBRARY_CA_FILE accepts either a single certificate or a complete validated PEM bundle.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`php-browser/8.4-trixie/v1.2.0`).

Artifact: `ghcr.io/xormania/php-browser@sha256:f14c53bd6c4c27b54b1415d6913947ec359c28e003d27292ef930d1c9b646464`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:bed7ada0f7a6d3d9ff119125afc87c6d3fd96ac29fd1210e6f52f516692c6510`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,834.5 MiB (1,923,569,287 bytes) |
| Build, cache export and image load | 58.51s |
| Public-artifact behavior and inventory verification | 29.13s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:46:44.078214Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

Size baseline: v1.1.0, `ghcr.io/xormania/php-browser@sha256:ba7a438a054450fe0e8387e233dee829d0c8ed883be5aa76568175ed1607ae82`; 1,576.9 MiB in the same image store. Change: **+16.3%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:20:29.592528Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
