# php-browser/8.4-trixie v1.2.1

- Retain only the prepared PHPStan Turbo binary matching the image runtime; omit incompatible native binaries in the installation layer while preserving PHPStan and its Symfony/PHPUnit extensions.

Migration: Compatible packaging fix. Select a verified new digest to obtain the smaller image. Prepared PHPStan remains opt-in; project-owned dependencies and analysis configuration are unchanged. Linux PHP 8.4/8.5 ZTS continues to use the upstream fallback when no matching binary is supplied.

Source: `fe9dd2386cafb65936477548b3dbe368ba339a27` (`php-browser/8.4-trixie/v1.2.1`).

Artifact: `ghcr.io/xormania/php-browser@sha256:730e67ff5d712550b7cce91387e9891e13092af05f70ae719f55f4c12f0a7f05`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:e00b85cb224a1f9ded14529d4c640c69bf5758237ec4720e67b9016282704a8f`.

[Verification](https://github.com/xormania/xorder/actions/runs/38002658722).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,615.5 MiB (1,693,972,416 bytes) |
| Build, cache export and image load | 56.74s |
| Public-artifact behavior and inventory verification | 28.84s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38002658722); 2026-10-09T23:13:05.903283Z.

Plan about **4 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.2.0, `ghcr.io/xormania/php-browser@sha256:f14c53bd6c4c27b54b1415d6913947ec359c28e003d27292ef930d1c9b646464`; 1,834.5 MiB in the same image store. Change: **-11.9%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:46:44.078214Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
