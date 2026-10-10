# playwright-browser/1.58-trixie v1.0.1

- Use RGB subpixel rendering to match the consuming project's Noble Chromium screenshot baselines; verify fontconfig and committed screenshot parity.

Migration: Compatible rendering fix. Select the accepted 1.0.1 digest after publication; existing 1.0.0 digest pins remain unchanged.

Source: `7982c49526d03f5c203ef309b046692360b798c7` (`playwright-browser/1.58-trixie/v1.0.1`).

Artifact: `ghcr.io/xormania/playwright-browser@sha256:72a68659cad38ce291d683a198a150c1d959e3ded6287ea4c7bd033e0599a63b`.

Base/parent: `docker.io/library/node:22-trixie-slim@sha256:154ba2f4d6fec323d28e4f4bb86bba4677f1223391a1979cf521304e03a98dfa`.

[Verification](https://github.com/xormania/xorder/actions/runs/38082421686).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 2,213.9 MiB (2,321,443,157 bytes) |
| Build, cache export and image load | 173.82s |
| Public-artifact behavior and inventory verification | 226.19s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38082421686); 2026-10-10T20:16:22.300063Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/playwright-browser@sha256:0e16fe1ce8a199880035fc6d9937682c18cc8d9b4b732f228716d33942831f76`; 2,213.9 MiB in the same image store. Change: **+0.0%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/38055213253); 2026-10-10T13:23:00.606311Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
