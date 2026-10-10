# python-dev/3.14-trixie v1.1.0

- Add opt-in trust for a mounted proxy CA before dropping privileges; preserve workspace ownership.

Migration: Compatible additive update. Mount one PEM certificate read-only and set LIBRARY_CA_FILE to its container path when needed. Root-owned workspaces can use PUID=0 and PGID=0 without bypassing the entrypoint.

Source: `b37b38aeb332765ee2beb889fdaf1030dfed4589` (`python-dev/3.14-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/python-dev@sha256:2868a42d29b7c340a1c592b8135bf40dd78bc028a2fddb50fb80eb3970d1f97d`.

Base/parent: `docker.io/library/python:3.14-slim-trixie@sha256:f85c5697265c178cc6887276c55fe16cf3d14ca35c3df6a5eab3b360534a55d2`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37762155280).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 593.9 MiB (622,720,973 bytes) |
| Build, cache export and image load | 40.69s |
| Public-artifact behavior and inventory verification | 12.18s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:16:25.223772Z.

Plan about **2 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/python-dev@sha256:ccd38b0cfb59a887a18d489be40ecf68a2a0ef083c46de634c0b0c424bfff3d5`; 1,191.8 MiB in the same image store. Change: **-50.2%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:16:43.147499Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
