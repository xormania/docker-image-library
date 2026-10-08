# flowbite-xor-dev/8.4-trixie v1.0.0

- Add PHP 8.4/FrankenPHP with Node 22 and the project-pinned cached Tailwind CLI.

Migration: Compatible addition. Use the updated runner to seed the cached Tailwind binary; project dependency lockfiles and version-matched browser selection remain authoritative.

Source: `d70d6147534972c34dded90977551f25d98bc61e` (`flowbite-xor-dev/8.4-trixie/v1.0.0`).

Artifact: `ghcr.io/xormania/flowbite-xor-dev@sha256:39d0dfa2cae629a9bc65e09d3cd44b5e1a3b92b54c55fb111286f4c4e2a4b374`.

Base/parent: `ghcr.io/xormania/php-frankenphp@sha256:9cd194f21ef4600fbba343fa5a471528fff3f6db6a1889ea280fb58d68cf30d2`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37852642503).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,168.4 MiB (1,225,206,317 bytes) |
| Build, cache export and image load | 27.08s |
| Public-artifact behavior and inventory verification | 93.03s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37852642503); 2026-10-08T22:27:17.513207Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
