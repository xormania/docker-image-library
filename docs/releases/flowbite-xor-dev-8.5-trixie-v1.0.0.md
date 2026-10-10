# flowbite-xor-dev/8.5-trixie v1.0.0

- Add Node 22/npm to the exact FrankenPHP parent and provide a flowbite-xor demo/test profile.

Migration: New optional project profile. Select its verified digest, install project lockfiles, and use the companion version derived from package-lock.json.

Source: `b37b38aeb332765ee2beb889fdaf1030dfed4589` (`flowbite-xor-dev/8.5-trixie/v1.0.0`).

Artifact: `ghcr.io/xormania/flowbite-xor-dev@sha256:a3ad6f61bb56d39060a060c7dbd99c1a65ae32f0ae7d9d7e9df0f6258afca474`.

Base/parent: `ghcr.io/xormania/php-frankenphp@sha256:3ac6ca8f9ba8d4155eb7a83c5a512a344673a3d1f62073fd0b53730030aa457d`.

[Verification](https://github.com/xormania/docker-image-library/actions/runs/37762155280).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,091.6 MiB (1,144,606,807 bytes) |
| Build, cache export and image load | 30.02s |
| Public-artifact behavior and inventory verification | 45.84s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37762155280); 2026-10-08T10:21:51.379666Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
