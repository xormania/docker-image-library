# rust-dev/1.99-trixie v1.0.1

- Reuse build layers across source-label changes; explicitly refresh Debian packages for each image revision.
- Use the official slim Trixie base with explicitly installed native build tools and PostgreSQL clients.

Migration: Compatible patch update; advertised development capabilities and invocation remain unchanged. Verify project dependencies before changing an existing digest pin.

Source: `f83e29f70357a1e0a58bb0e8dbf9824e63cf05e5` (`rust-dev/1.99-trixie/v1.0.1`).

Artifact: `ghcr.io/xormania/rust-dev@sha256:3d01dc8505b9861f947b2b8567f0cba520f56dac06bafec19680ff0483cad43b`.

Base/parent: `docker.io/library/rust:1.99-slim-trixie@sha256:24e632c09342c20abf8312cf4f61430a911c01ed3a5e4c02b87292b1c39c5273`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37750479509).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,274.9 MiB (1,336,840,122 bytes) |
| Build, cache export and image load | 52.08s |
| Public-artifact behavior and inventory verification | 1.35s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37750479509); 2026-10-08T08:34:01.464104Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
