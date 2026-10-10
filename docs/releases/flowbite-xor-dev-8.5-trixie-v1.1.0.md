# flowbite-xor-dev/8.5-trixie v1.1.0

- Pre-cache the project-pinned Tailwind CLI and seed fresh demo cache volumes without downloading it per checkout.

Migration: Compatible addition. Use the updated runner to seed the cached Tailwind binary; project dependency lockfiles and version-matched browser selection remain authoritative.

Source: `d70d6147534972c34dded90977551f25d98bc61e` (`flowbite-xor-dev/8.5-trixie/v1.1.0`).

Artifact: `ghcr.io/xormania/flowbite-xor-dev@sha256:23f4b1755d665c3d0a7fbedebc6fcc6da0edef7ea9a0d71898bee3345ba77df0`.

Base/parent: `ghcr.io/xormania/php-frankenphp@sha256:3ac6ca8f9ba8d4155eb7a83c5a512a344673a3d1f62073fd0b53730030aa457d`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37852642503).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,198.2 MiB (1,256,357,028 bytes) |
| Build, cache export and image load | 49.45s |
| Public-artifact behavior and inventory verification | 84.54s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37852642503); 2026-10-08T22:23:57.290148Z.

Plan about **3 GiB free for a cold pull**, plus space for project dependencies and test output. This estimate is twice the measured unpacked image size, rounded up; shared layers may lower it, while the image store, temporary files and sandbox quotas can increase the requirement. Check free space on the Docker data filesystem; it may differ from the checkout filesystem.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/flowbite-xor-dev@sha256:a3ad6f61bb56d39060a060c7dbd99c1a65ae32f0ae7d9d7e9df0f6258afca474`; 1,091.6 MiB in the same image store. Change: **+9.8%**. [Baseline measurement](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:21:51.379666Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
