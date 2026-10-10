# php-frankenphp/8.5-trixie v1.1.1

- Retain only the prepared PHPStan Turbo binary matching the image runtime; omit incompatible native binaries in the installation layer while preserving PHPStan and its Symfony/PHPUnit extensions.

Migration: Compatible packaging fix. Select a verified new digest to obtain the smaller image. Prepared PHPStan remains opt-in; project-owned dependencies and analysis configuration are unchanged. Linux PHP 8.4/8.5 ZTS continues to use the upstream fallback when no matching binary is supplied.

Source: `fe9dd2386cafb65936477548b3dbe368ba339a27` (`php-frankenphp/8.5-trixie/v1.1.1`).

Artifact: `ghcr.io/xormania/php-frankenphp@sha256:905faba01fd159953b9fd0e3878f0b2e4cb2661584515c087c95bd5474408afc`.

Base/parent: `docker.io/dunglas/frankenphp:1-php8.5-trixie@sha256:06e3a490ff76db5bfd1c3c410677fc22bdbcb2c735c240cfa4111727d7641f38`.

[Verification](https://github.com/xormania/xorder/actions/runs/38002658722).

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 993.3 MiB (1,041,501,363 bytes) |
| Build, cache export and image load | 170.51s |
| Public-artifact behavior and inventory verification | 25.43s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38002658722); 2026-10-09T23:10:25.177407Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.1.0, `ghcr.io/xormania/php-frankenphp@sha256:c60aee9639a4e9b377c1f48e26dd5d351edc7f39673344debe1afb677c8b0572`; 1,219.2 MiB in the same image store. Change: **-18.5%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/37884893194); 2026-10-09T04:45:01.446171Z.

The release record and GitHub Release asset retain the exact definition and per-platform inventory. The generated documentation commit is later than the build source commit.
