# php-dev/8.4-trixie v1.2.1

- Retain only the prepared PHPStan Turbo binary matching the image runtime; omit incompatible native binaries in the installation layer while preserving PHPStan and its Symfony/PHPUnit extensions.

Migration: Compatible packaging fix. Select a verified new digest to obtain the smaller image. Prepared PHPStan remains opt-in; project-owned dependencies and analysis configuration are unchanged. Linux PHP 8.4/8.5 ZTS continues to use the upstream fallback when no matching binary is supplied.

Source: `fe9dd2386cafb65936477548b3dbe368ba339a27` (`php-dev/8.4-trixie/v1.2.1`).

Artifact: `ghcr.io/xormania/php-dev@sha256:e00b85cb224a1f9ded14529d4c640c69bf5758237ec4720e67b9016282704a8f`.

Base/parent: `docker.io/library/php:8.4-cli-trixie@sha256:1d2cf2b7d715b5b3aa959f0150ccbcc7b71e0181b637e443abf40a7fb56bf79a`.

[Verification](https://github.com/xormania/xorder/actions/runs/38002658722).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 912.4 MiB (956,681,439 bytes) |
| Build, cache export and image load | 163.56s |
| Public-artifact behavior and inventory verification | 27.67s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38002658722); 2026-10-09T23:10:30.194990Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.2.0, `ghcr.io/xormania/php-dev@sha256:bed7ada0f7a6d3d9ff119125afc87c6d3fd96ac29fd1210e6f52f516692c6510`; 1,131.3 MiB in the same image store. Change: **-19.4%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:44:08.357134Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
