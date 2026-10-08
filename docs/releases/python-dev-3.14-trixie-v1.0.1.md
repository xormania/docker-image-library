# python-dev/3.14-trixie v1.0.1

- Reuse build layers across source-label changes; explicitly refresh Debian packages for each image revision.
- Use the official slim Trixie base with explicitly installed native build tools and PostgreSQL clients.
- Reuse the upstream Python interpreter instead of installing a second system Python.

Migration: Compatible patch update; advertised development capabilities and invocation remain unchanged. Verify project dependencies before changing an existing digest pin.

Source: `f83e29f70357a1e0a58bb0e8dbf9824e63cf05e5` (`python-dev/3.14-trixie/v1.0.1`).

Artifact: `ghcr.io/xormania/python-dev@sha256:b8fce60b87734551462a90cee2e1c6fbf224082430e09971834d27a6de45e154`.

Base/parent: `docker.io/library/python:3.14-slim-trixie@sha256:f85c5697265c178cc6887276c55fe16cf3d14ca35c3df6a5eab3b360534a55d2`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37750479509).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 593.9 MiB (622,720,013 bytes) |
| Build, cache export and image load | 40.56s |
| Public-artifact behavior and inventory verification | 11.17s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37750479509); 2026-10-08T08:34:08.387897Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
