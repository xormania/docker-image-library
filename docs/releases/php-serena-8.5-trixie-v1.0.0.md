# php-serena/8.5-trixie v1.0.0

- Package the tested Serena v2 REPL/PHPactor pair with locked Python dependencies, private session configuration and offline MCP acceptance against flowbite-xor.

Migration: New opt-in image. Keep existing application images and Composer locks. Pull a verified exact digest before configuring an MCP client; select the checkout and project directory explicitly. Source is read-only by default; opt into editing with --write.

Source: `fa8d56c5d733f0903883a2578016e904b27fa3c3` (`php-serena/8.5-trixie/v1.0.0`).

Artifact: `ghcr.io/xormania/php-serena@sha256:9efe7bb1989723578a3eed03a2ee5802145af1efaba4a1297dd994d5abe62718`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:cd670b7c7b9624ce7dc7ee6b7b2a4d5b19ce36d6226f077a417667ae8505e000`.

[Verification](https://github.com/xormania/xorder/actions/runs/38030147899).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,087.2 MiB (1,139,965,670 bytes) |
| Build, cache export and image load | 36.85s |
| Public-artifact behavior and inventory verification | 91.02s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38030147899); 2026-10-10T06:17:43.640904Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
