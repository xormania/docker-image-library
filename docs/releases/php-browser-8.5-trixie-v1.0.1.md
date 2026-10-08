# php-browser/8.5-trixie v1.0.1

- Reuse build layers across source-label changes; explicitly refresh Debian packages for each image revision.

Migration: Compatible patch update; advertised development capabilities and invocation remain unchanged. Verify project dependencies before changing an existing digest pin.

Source: `f83e29f70357a1e0a58bb0e8dbf9824e63cf05e5` (`php-browser/8.5-trixie/v1.0.1`).

Artifact: `ghcr.io/xormania/php-browser@sha256:ccd4837bf67803cfd4de7e0450bceb9025cff4238d679f993aaa36f701713f1f`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:659f0c3ea9c1d84bf7c19b3ebaaef4bd16dec21dbb700ff637428186ecce5b2a`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37750479509).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,606.7 MiB (1,684,720,862 bytes) |
| Build, cache export and image load | 58.66s |
| Public-artifact behavior and inventory verification | 9.79s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37750479509); 2026-10-08T08:39:23.697732Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
