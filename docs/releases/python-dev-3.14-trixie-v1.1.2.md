# python-dev/3.14-trixie v1.1.2

- Refresh shared source inputs for PHP testing helpers while preserving complete PEM bundle trust.

Migration: Compatible source refresh. Existing exact pins remain valid; select this revision only after its normal publication and verification.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`python-dev/3.14-trixie/v1.1.2`).

Artifact: `ghcr.io/xormania/python-dev@sha256:f9821a6dba4ee2e50715c37421ff46437dc9104d4652ead1bc74eec561bcafba`.

Base/parent: `docker.io/library/python:3.14-slim-trixie@sha256:f85c5697265c178cc6887276c55fe16cf3d14ca35c3df6a5eab3b360534a55d2`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 593.9 MiB (622,722,691 bytes) |
| Build, cache export and image load | 39.93s |
| Public-artifact behavior and inventory verification | 22.71s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:41:45.296878Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

Size baseline: v1.1.0, `ghcr.io/xormania/python-dev@sha256:2868a42d29b7c340a1c592b8135bf40dd78bc028a2fddb50fb80eb3970d1f97d`; 593.9 MiB in the same image store. Change: **+0.0%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:16:25.223772Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
