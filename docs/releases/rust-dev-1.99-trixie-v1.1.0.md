# rust-dev/1.99-trixie v1.1.0

- Add opt-in trust for a mounted proxy CA before dropping privileges; preserve workspace ownership.

Migration: Compatible additive update. Mount one PEM certificate read-only and set LIBRARY_CA_FILE to its container path when needed. Root-owned workspaces can use PUID=0 and PGID=0 without bypassing the entrypoint.

Source: `b37b38aeb332765ee2beb889fdaf1030dfed4589` (`rust-dev/1.99-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/rust-dev@sha256:3bd310edbdd171c59bde5818d7fae4ff05e1b1f63f9a5c3ff5e3da8b5311e809`.

Base/parent: `docker.io/library/rust:1.99-slim-trixie@sha256:24e632c09342c20abf8312cf4f61430a911c01ed3a5e4c02b87292b1c39c5273`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37762155280).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,274.9 MiB (1,336,841,082 bytes) |
| Build, cache export and image load | 55.26s |
| Public-artifact behavior and inventory verification | 3.51s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:16:28.971289Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/rust-dev@sha256:f7a732022c49f33478b4237d9a8dcd78c8925ee14a6df5fec16ad08729dd0e04`; 1,784.0 MiB in the same image store. Change: **-28.5%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:16:52.317985Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
