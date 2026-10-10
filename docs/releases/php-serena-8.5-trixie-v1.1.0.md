# php-serena/8.5-trixie v1.1.0

- Disable PHPactor configuration prompts on clean read-only checkouts; add locked JavaScript tooling, configurable request timeout, complete-index reuse, structured sessions and shell access.

Migration: Compatible additions. Existing MCP invocation remains valid; select a verified 1.1 digest for the new capabilities. Pass --write for trusted editing, --languages php_phpactor,typescript for mixed projects and --cache-dir for persistent indexes.

Source: `45e9220d768155b15b4d7ca89cdc5e58cebcd3b2` (`php-serena/8.5-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/php-serena@sha256:f2d9b40e72a4bc029f56fa152b4e25363b38898be9dc1b19262c2a29705b04a6`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:cd670b7c7b9624ce7dc7ee6b7b2a4d5b19ce36d6226f077a417667ae8505e000`.

[Verification](https://github.com/xormania/xorder/actions/runs/38055213253).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,242.6 MiB (1,303,011,277 bytes) |
| Build, cache export and image load | 44.36s |
| Public-artifact behavior and inventory verification | 106.33s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38055213253); 2026-10-10T13:23:51.907682Z.

Plan about **3 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/php-serena@sha256:9efe7bb1989723578a3eed03a2ee5802145af1efaba4a1297dd994d5abe62718`; 1,087.2 MiB in the same image store. Change: **+14.3%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/38030147899); 2026-10-10T06:17:43.640904Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
