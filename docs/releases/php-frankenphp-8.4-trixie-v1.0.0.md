# php-frankenphp/8.4-trixie v1.0.0

- Add the PHP 8.4 FrankenPHP line for minimum-version project compatibility checks.

Migration: New optional PHP 8.4 line. Select its verified digest and validate project lockfiles and worker behavior.

Source: `d70d6147534972c34dded90977551f25d98bc61e` (`php-frankenphp/8.4-trixie/v1.0.0`).

Artifact: `ghcr.io/xormania/php-frankenphp@sha256:9cd194f21ef4600fbba343fa5a471528fff3f6db6a1889ea280fb58d68cf30d2`.

Base/parent: `docker.io/dunglas/frankenphp:1-php8.4-trixie@sha256:2fd4a848c05bf4902a3d9ff1a4991c2f4d4665df0567aee21be4eee120ded038`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37852642503).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 931.8 MiB (977,108,437 bytes) |
| Build, cache export and image load | 169.56s |
| Public-artifact behavior and inventory verification | 12.69s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37852642503); 2026-10-08T22:22:56.838890Z.

Plan about **2 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
