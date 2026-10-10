# php-browser/8.4-trixie v1.1.0

- Add opt-in trust for a mounted proxy CA before dropping privileges; preserve workspace ownership.

Migration: Compatible additive update. Mount one PEM certificate read-only and set LIBRARY_CA_FILE to its container path when needed. Root-owned workspaces can use PUID=0 and PGID=0 without bypassing the entrypoint.

Source: `b37b38aeb332765ee2beb889fdaf1030dfed4589` (`php-browser/8.4-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/php-browser@sha256:ba7a438a054450fe0e8387e233dee829d0c8ed883be5aa76568175ed1607ae82`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:d3f9483df7c3f30837dab772acaa53f55ab1af5b7bdb21af8d320d80f4bd9029`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37762155280).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,576.9 MiB (1,653,461,844 bytes) |
| Build, cache export and image load | 57.39s |
| Public-artifact behavior and inventory verification | 13.26s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:20:29.592528Z.

Plan about **4 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/php-browser@sha256:371dbe808e951915d9c0ed3c41fb6e830f2cabb40ecc76733b9da92d957174ae`; 1,576.9 MiB in the same image store. Change: **+0.0%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:20:44.384601Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
