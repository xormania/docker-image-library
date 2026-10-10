# playwright-browser/1.58-trixie v1.0.0

- Prepare Playwright 1.58.2 and its Chromium, Firefox and WebKit engines; verify each engine offline before catalog availability.

Migration: New optional companion. The runner retains the official image for versions without an accepted xorder browser release. BROWSER_IMAGE explicitly selects a local candidate or verified digest.

Source: `45e9220d768155b15b4d7ca89cdc5e58cebcd3b2` (`playwright-browser/1.58-trixie/v1.0.0`).

Artifact: `ghcr.io/xormania/playwright-browser@sha256:0e16fe1ce8a199880035fc6d9937682c18cc8d9b4b732f228716d33942831f76`.

Base/parent: `docker.io/library/node:22-trixie-slim@sha256:154ba2f4d6fec323d28e4f4bb86bba4677f1223391a1979cf521304e03a98dfa`.

[Verification](https://github.com/xormania/xorder/actions/runs/38055213253).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 2,213.9 MiB (2,321,443,126 bytes) |
| Build, cache export and image load | 156.17s |
| Public-artifact behavior and inventory verification | 4.99s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38055213253); 2026-10-10T13:23:00.606311Z.

Plan about **5 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
