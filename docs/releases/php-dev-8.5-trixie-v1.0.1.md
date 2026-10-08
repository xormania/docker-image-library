# php-dev/8.5-trixie v1.0.1

- Reuse build layers across source-label changes; explicitly refresh Debian packages for each image revision.

Migration: Compatible patch update; advertised development capabilities and invocation remain unchanged. Verify project dependencies before changing an existing digest pin.

Source: `f83e29f70357a1e0a58bb0e8dbf9824e63cf05e5` (`php-dev/8.5-trixie/v1.0.1`).

Artifact: `ghcr.io/xormania/php-dev@sha256:659f0c3ea9c1d84bf7c19b3ebaaef4bd16dec21dbb700ff637428186ecce5b2a`.

Base/parent: `docker.io/library/php:8.5-cli-trixie@sha256:01a109229f4465bc9ef042d9198f09a4d9da7775a825dbd8572dcdbd8756c4d3`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37750479509).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 903.5 MiB (947,429,837 bytes) |
| Build, cache export and image load | 240.39s |
| Public-artifact behavior and inventory verification | 9.06s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37750479509); 2026-10-08T08:37:22.375659Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
