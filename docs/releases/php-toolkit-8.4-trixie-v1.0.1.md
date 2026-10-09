# php-toolkit/8.4-trixie v1.0.1

- Retain only the prepared PHPStan Turbo binary matching the image runtime; omit incompatible native binaries in the installation layer while preserving PHPStan and its Symfony/PHPUnit extensions.

Migration: Compatible packaging fix. Select a verified new digest to obtain the smaller image. Prepared PHPStan remains opt-in; project-owned dependencies and analysis configuration are unchanged. Linux PHP 8.4/8.5 ZTS continues to use the upstream fallback when no matching binary is supplied.

Source: `fe9dd2386cafb65936477548b3dbe368ba339a27` (`php-toolkit/8.4-trixie/v1.0.1`).

Artifact: `ghcr.io/xormania/php-toolkit@sha256:85f60474582b2d43a8a121e8c7ebc7c2d6e619245973db3dab2404f0f61b4a23`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:e00b85cb224a1f9ded14529d4c640c69bf5758237ec4720e67b9016282704a8f`.

[Verification](https://github.com/xormania/xorder/actions/runs/38002658722).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 936.8 MiB (982,284,711 bytes) |
| Build, cache export and image load | 12.97s |
| Public-artifact behavior and inventory verification | 33.35s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38002658722); 2026-10-09T23:14:41.034687Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/php-toolkit@sha256:ecd476253546a991dbab18753b3f60eee192e51240b33890542c9d387dce50f5`; 1,155.7 MiB in the same image store. Change: **-18.9%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:48:17.746506Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
