# php-browser/8.5-trixie v1.2.0

- Add opt-in PCOV coverage and reusable lock-owned PHPUnit/PHPStan tasks while retaining Xdebug coverage and default-disabled coverage hooks.
- Accept a mounted multi-certificate PEM CA bundle; validate all certificates before replacing managed trust and retain single-certificate and root/user behavior.

Migration: Compatible additive update. Select a verified new digest before using library-php-tests; PHPUnit/PHPStan versions and configuration continue to come from the consuming project. Set COVERAGE_DRIVER=xdebug for Xdebug coverage. LIBRARY_CA_FILE accepts either a single certificate or a complete validated PEM bundle.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`php-browser/8.5-trixie/v1.2.0`).

Artifact: `ghcr.io/xormania/php-browser@sha256:28dcd4508de2caeefbab9db7319bd9edd84b2be51f380c418fab07fec2f18590`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:766e2d2ffe1b043160a0fb9d67825982a87948a4b4e13b41a84298014b34f49d`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,864.3 MiB (1,954,830,702 bytes) |
| Build, cache export and image load | 59.52s |
| Public-artifact behavior and inventory verification | 30.28s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:47:29.043585Z.

Plan about **4 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

Size baseline: v1.1.0, `ghcr.io/xormania/php-browser@sha256:fd4f250816cd15db0e111ea9cb71c40df1def9174633ce1b7e9bdba587cd6882`; 1,606.7 MiB in the same image store. Change: **+16.0%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:20:37.139406Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
