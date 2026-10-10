# flowbite-xor-dev/8.5-trixie v1.2.0

- Add opt-in PCOV coverage and reusable lock-owned PHPUnit/PHPStan tasks while retaining Xdebug coverage and default-disabled coverage hooks.
- Accept a mounted multi-certificate PEM CA bundle; validate all certificates before replacing managed trust and retain single-certificate and root/user behavior.

Migration: Compatible additive update. Select a verified new digest before using library-php-tests; PHPUnit/PHPStan versions and configuration continue to come from the consuming project. Set COVERAGE_DRIVER=xdebug for Xdebug coverage. LIBRARY_CA_FILE accepts either a single certificate or a complete validated PEM bundle.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`flowbite-xor-dev/8.5-trixie/v1.2.0`).

Artifact: `ghcr.io/xormania/flowbite-xor-dev@sha256:71fe8c343367fe83c9b0d39623f9843e627b99763270cddf00b29bae446f3e38`.

Base/parent: `ghcr.io/xormania/php-frankenphp@sha256:c60aee9639a4e9b377c1f48e26dd5d351edc7f39673344debe1afb677c8b0572`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,455.8 MiB (1,526,476,858 bytes) |
| Build, cache export and image load | 29.31s |
| Public-artifact behavior and inventory verification | 115.62s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:50:08.345141Z.

Plan about **3 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

Size baseline: v1.1.0, `ghcr.io/xormania/flowbite-xor-dev@sha256:23f4b1755d665c3d0a7fbedebc6fcc6da0edef7ea9a0d71898bee3345ba77df0`; 1,198.2 MiB in the same image store. Change: **+21.5%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37852642503); 2026-10-08T22:23:57.290148Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
