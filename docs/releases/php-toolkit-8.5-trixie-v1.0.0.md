# php-toolkit/8.5-trixie v1.0.0

- Prepare independently locked UX Toolkit validation dependencies and a clean Symfony 7.4 application for recipe-install testing without consumer dependency downloads.

Migration: New optional family. Select an accepted catalog digest and use examples/php-toolkit/run.sh; keep each fresh recipe-install application in a new directory.

Source: `ea9133bbb23d222c1e0ff800250ccbb98066f254` (`php-toolkit/8.5-trixie/v1.0.0`).

Artifact: `ghcr.io/xormania/php-toolkit@sha256:5ba23c9c72a8ddc6f65d79fcbad055ff0ad86c4dd6ff523cddaf4aac5137b818`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:766e2d2ffe1b043160a0fb9d67825982a87948a4b4e13b41a84298014b34f49d`.

[Verification](https://github.com/xormania/xorder/actions/runs/37884893194).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,185.6 MiB (1,243,142,997 bytes) |
| Build, cache export and image load | 13.35s |
| Public-artifact behavior and inventory verification | 34.77s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:49:08.050211Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
