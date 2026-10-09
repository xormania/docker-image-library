# php-frankenphp/8.4-trixie v1.1.1

- Retain only the prepared PHPStan Turbo binary matching the image runtime; omit incompatible native binaries in the installation layer while preserving PHPStan and its Symfony/PHPUnit extensions.

Migration: Compatible packaging fix. Select a verified new digest to obtain the smaller image. Prepared PHPStan remains opt-in; project-owned dependencies and analysis configuration are unchanged. Linux PHP 8.4/8.5 ZTS continues to use the upstream fallback when no matching binary is supplied.

Source: `fe9dd2386cafb65936477548b3dbe368ba339a27` (`php-frankenphp/8.4-trixie/v1.1.1`).

Artifact: `ghcr.io/xormania/php-frankenphp@sha256:111d101fb9f59aa1284533505070ebf9534cb7c22c909603074a2fa0046339e5`.

Base/parent: `docker.io/dunglas/frankenphp:1-php8.4-trixie@sha256:2fd4a848c05bf4902a3d9ff1a4991c2f4d4665df0567aee21be4eee120ded038`.

[Verification](https://github.com/xormania/xorder/actions/runs/38002658722).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 963.5 MiB (1,010,350,164 bytes) |
| Build, cache export and image load | 169.72s |
| Public-artifact behavior and inventory verification | 28.73s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38002658722); 2026-10-09T23:10:25.600617Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.1.0, `ghcr.io/xormania/php-frankenphp@sha256:6c5edb921d745e5dbc8fdff454c557360c5a789d5a82aa7b351b6419176050e8`; 1,189.4 MiB in the same image store. Change: **-19.0%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:44:22.594975Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
