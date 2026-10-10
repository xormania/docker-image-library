# flowbite-xor-dev/8.5-trixie v1.2.1

- Retain only the prepared PHPStan Turbo binary matching the image runtime; omit incompatible native binaries in the installation layer while preserving PHPStan and its Symfony/PHPUnit extensions.

Migration: Compatible packaging fix. Select a verified new digest to obtain the smaller image. Prepared PHPStan remains opt-in; project-owned dependencies and analysis configuration are unchanged. Linux PHP 8.4/8.5 ZTS continues to use the upstream fallback when no matching binary is supplied.

Source: `fe9dd2386cafb65936477548b3dbe368ba339a27` (`flowbite-xor-dev/8.5-trixie/v1.2.1`).

Artifact: `ghcr.io/xormania/flowbite-xor-dev@sha256:7c795be0d818b4458d7c8730ddebab68878684d0ec52cd3ef5b41f80e29efcd2`.

Base/parent: `ghcr.io/xormania/php-frankenphp@sha256:905faba01fd159953b9fd0e3878f0b2e4cb2661584515c087c95bd5474408afc`.

[Verification](https://github.com/xormania/xorder/actions/runs/38002658722).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,229.9 MiB (1,289,599,243 bytes) |
| Build, cache export and image load | 30.87s |
| Public-artifact behavior and inventory verification | 91.72s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38002658722); 2026-10-09T23:14:45.393057Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.2.0, `ghcr.io/xormania/flowbite-xor-dev@sha256:71fe8c343367fe83c9b0d39623f9843e627b99763270cddf00b29bae446f3e38`; 1,455.8 MiB in the same image store. Change: **-15.5%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:50:08.345141Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
