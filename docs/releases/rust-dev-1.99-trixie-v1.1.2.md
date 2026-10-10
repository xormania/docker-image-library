# rust-dev/1.99-trixie v1.1.2

- Refresh shared source inputs for PHP testing helpers while preserving complete PEM bundle trust.

Migration: Compatible source refresh. Existing exact pins remain valid; select this revision only after its normal publication and verification.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`rust-dev/1.99-trixie/v1.1.2`).

Artifact: `ghcr.io/xormania/rust-dev@sha256:a83e113d10653abffb8896e5d41ec898b9e9c768e9007816fea545d675935890`.

Base/parent: `docker.io/library/rust:1.99-slim-trixie@sha256:24e632c09342c20abf8312cf4f61430a911c01ed3a5e4c02b87292b1c39c5273`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,274.9 MiB (1,336,842,800 bytes) |
| Build, cache export and image load | 63.85s |
| Public-artifact behavior and inventory verification | 8.46s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:41:49.591415Z.

Plan about **3 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

Size baseline: v1.1.0, `ghcr.io/xormania/rust-dev@sha256:3bd310edbdd171c59bde5818d7fae4ff05e1b1f63f9a5c3ff5e3da8b5311e809`; 1,274.9 MiB in the same image store. Change: **+0.0%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:16:28.971289Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
