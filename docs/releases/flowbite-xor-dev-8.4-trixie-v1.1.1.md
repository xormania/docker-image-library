# flowbite-xor-dev/8.4-trixie v1.1.1

- Retain only the prepared PHPStan Turbo binary matching the image runtime; omit incompatible native binaries in the installation layer while preserving PHPStan and its Symfony/PHPUnit extensions.

Migration: Compatible packaging fix. Select a verified new digest to obtain the smaller image. Prepared PHPStan remains opt-in; project-owned dependencies and analysis configuration are unchanged. Linux PHP 8.4/8.5 ZTS continues to use the upstream fallback when no matching binary is supplied.

Source: `fe9dd2386cafb65936477548b3dbe368ba339a27` (`flowbite-xor-dev/8.4-trixie/v1.1.1`).

Artifact: `ghcr.io/xormania/flowbite-xor-dev@sha256:19a3edd4ddaefcc024106d593121b3d86d6910cae9ea7ae8c555a8d35f5cfa39`.

Base/parent: `ghcr.io/xormania/php-frankenphp@sha256:111d101fb9f59aa1284533505070ebf9534cb7c22c909603074a2fa0046339e5`.

[Verification](https://github.com/xormania/xorder/actions/runs/38002658722).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,200.1 MiB (1,258,448,044 bytes) |
| Build, cache export and image load | 26.11s |
| Public-artifact behavior and inventory verification | 108.55s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38002658722); 2026-10-09T23:15:06.477167Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.1.0, `ghcr.io/xormania/flowbite-xor-dev@sha256:68979e1105bdadb6a3a784a8944f86ffe8f54f0e8d475dc2bbea0c18a00b2cca`; 1,426.1 MiB in the same image store. Change: **-15.8%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:49:05.827746Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
