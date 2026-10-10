# playwright-browser/1.58-trixie v1.0.2

- Retain RGB screenshot parity and isolate browser locks and fixtures by runtime line; prepare matched releases when the consumer Playwright pin changes.

Migration: Select the accepted 1.0.2 digest after publication for isolated browser inputs and RGB rendering. Existing exact release pins remain unchanged.

Source: `201dcf12755be051163db4f7327d982acd809c07` (`playwright-browser/1.58-trixie/v1.0.2`).

Artifact: `ghcr.io/xormania/playwright-browser@sha256:48c7089b8ca4353f74ba66bda332f94e8ace76743ebd9a98560c83f9f82c3627`.

Base/parent: `docker.io/library/node:22-trixie-slim@sha256:154ba2f4d6fec323d28e4f4bb86bba4677f1223391a1979cf521304e03a98dfa`.

[Verification](https://github.com/xormania/xorder/actions/runs/38082448522).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 2,213.9 MiB (2,321,443,134 bytes) |
| Build, cache export and image load | 157.28s |
| Public-artifact behavior and inventory verification | 213.29s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38082448522); 2026-10-10T20:34:02.590398Z.

Plan about **5 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/playwright-browser@sha256:0e16fe1ce8a199880035fc6d9937682c18cc8d9b4b732f228716d33942831f76`; 2,213.9 MiB in the same image store. Change: **+0.0%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/38055213253); 2026-10-10T13:23:00.606311Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
