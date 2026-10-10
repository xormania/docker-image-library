# php-browser/8.5-trixie v1.1.0

- Add opt-in trust for a mounted proxy CA before dropping privileges; preserve workspace ownership.

Migration: Compatible additive update. Mount one PEM certificate read-only and set LIBRARY_CA_FILE to its container path when needed. Root-owned workspaces can use PUID=0 and PGID=0 without bypassing the entrypoint.

Source: `b37b38aeb332765ee2beb889fdaf1030dfed4589` (`php-browser/8.5-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/php-browser@sha256:fd4f250816cd15db0e111ea9cb71c40df1def9174633ce1b7e9bdba587cd6882`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:53a1728c55ad8059184ef2ccc0bfb5c62e1b97c3cda87f14ae0897e46cf1317d`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37762155280).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,606.7 MiB (1,684,722,779 bytes) |
| Build, cache export and image load | 55.74s |
| Public-artifact behavior and inventory verification | 12.46s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:20:37.139406Z.

Plan about **4 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/php-browser@sha256:b4bc2f409c6ca21a828855e25fec51c8df32d778b119e1e0c7a84be68f912d86`; 1,606.7 MiB in the same image store. Change: **+0.0%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:20:46.753398Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
