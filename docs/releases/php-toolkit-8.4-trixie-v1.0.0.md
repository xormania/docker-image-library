# php-toolkit/8.4-trixie v1.0.0

- Prepare independently locked UX Toolkit validation dependencies and a clean Symfony 7.4 application for recipe-install testing without consumer dependency downloads.

Migration: New optional family. Select an accepted catalog digest and use examples/php-toolkit/run.sh; keep each fresh recipe-install application in a new directory.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`php-toolkit/8.4-trixie/v1.0.0`).

Artifact: `ghcr.io/xormania/php-toolkit@sha256:ecd476253546a991dbab18753b3f60eee192e51240b33890542c9d387dce50f5`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:bed7ada0f7a6d3d9ff119125afc87c6d3fd96ac29fd1210e6f52f516692c6510`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,155.7 MiB (1,211,881,582 bytes) |
| Build, cache export and image load | 12.55s |
| Public-artifact behavior and inventory verification | 33.92s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:48:17.746506Z.

Plan about **3 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
