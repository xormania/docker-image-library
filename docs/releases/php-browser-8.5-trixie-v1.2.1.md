# php-browser/8.5-trixie v1.2.1

- Retain only the prepared PHPStan Turbo binary matching the image runtime; omit incompatible native binaries in the installation layer while preserving PHPStan and its Symfony/PHPUnit extensions.

Migration: Compatible packaging fix. Select a verified new digest to obtain the smaller image. Prepared PHPStan remains opt-in; project-owned dependencies and analysis configuration are unchanged. Linux PHP 8.4/8.5 ZTS continues to use the upstream fallback when no matching binary is supplied.

Source: `fe9dd2386cafb65936477548b3dbe368ba339a27` (`php-browser/8.5-trixie/v1.2.1`).

Artifact: `ghcr.io/xormania/php-browser@sha256:3bd07aa66ea6af93ee3e690be1cb2e09352d3fa2e19f522f458e7020d664aded`.

Base/parent: `ghcr.io/xormania/php-dev@sha256:cd670b7c7b9624ce7dc7ee6b7b2a4d5b19ce36d6226f077a417667ae8505e000`.

[Verification](https://github.com/xormania/xorder/actions/runs/38002658722).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,645.3 MiB (1,725,237,927 bytes) |
| Build, cache export and image load | 50.30s |
| Public-artifact behavior and inventory verification | 24.24s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38002658722); 2026-10-09T23:12:13.407279Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.2.0, `ghcr.io/xormania/php-browser@sha256:28dcd4508de2caeefbab9db7319bd9edd84b2be51f380c418fab07fec2f18590`; 1,864.3 MiB in the same image store. Change: **-11.7%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:47:29.043585Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
