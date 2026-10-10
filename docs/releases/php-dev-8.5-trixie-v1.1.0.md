# php-dev/8.5-trixie v1.1.0

- Add opt-in trust for a mounted proxy CA before dropping privileges; preserve workspace ownership.

Migration: Compatible additive update. Mount one PEM certificate read-only and set LIBRARY_CA_FILE to its container path when needed. Root-owned workspaces can use PUID=0 and PGID=0 without bypassing the entrypoint.

Source: `b37b38aeb332765ee2beb889fdaf1030dfed4589` (`php-dev/8.5-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/php-dev@sha256:53a1728c55ad8059184ef2ccc0bfb5c62e1b97c3cda87f14ae0897e46cf1317d`.

Base/parent: `docker.io/library/php:8.5-cli-trixie@sha256:01a109229f4465bc9ef042d9198f09a4d9da7775a825dbd8572dcdbd8756c4d3`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37762155280).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 903.5 MiB (947,431,802 bytes) |
| Build, cache export and image load | 171.56s |
| Public-artifact behavior and inventory verification | 11.62s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:18:34.043560Z.

Plan about **2 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/php-dev@sha256:8a824a7e88ef81f63611629ad5e4a1de1fc17adc7cb278e8c48ab1d43e745b0c`; 903.5 MiB in the same image store. Change: **+0.0%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:18:37.954772Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
