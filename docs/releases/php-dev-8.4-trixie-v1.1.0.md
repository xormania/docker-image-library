# php-dev/8.4-trixie v1.1.0

- Add opt-in trust for a mounted proxy CA before dropping privileges; preserve workspace ownership.

Migration: Compatible additive update. Mount one PEM certificate read-only and set LIBRARY_CA_FILE to its container path when needed. Root-owned workspaces can use PUID=0 and PGID=0 without bypassing the entrypoint.

Source: `b37b38aeb332765ee2beb889fdaf1030dfed4589` (`php-dev/8.4-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/php-dev@sha256:d3f9483df7c3f30837dab772acaa53f55ab1af5b7bdb21af8d320d80f4bd9029`.

Base/parent: `docker.io/library/php:8.4-cli-trixie@sha256:1d2cf2b7d715b5b3aa959f0150ccbcc7b71e0181b637e443abf40a7fb56bf79a`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37762155280).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 873.7 MiB (916,170,867 bytes) |
| Build, cache export and image load | 152.10s |
| Public-artifact behavior and inventory verification | 12.03s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:18:18.047279Z.

Plan about **2 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/php-dev@sha256:cb229768983aa9f97ddbe6e399775eb9a644c8399cfad0243a63dbdd5166a968`; 873.7 MiB in the same image store. Change: **+0.0%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:18:23.364860Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
