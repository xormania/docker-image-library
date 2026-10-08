# rust-dev/1.99-trixie

Rust 2024 native compilation, Clippy, formatting and wasm32-unknown-unknown builds.

Available revision: **1.0.1**. Pin:

```text
ghcr.io/xormania/rust-dev@sha256:3d01dc8505b9861f947b2b8567f0cba520f56dac06bafec19680ff0483cad43b
```

[Verification evidence](https://github.com/xormania/docker-image-library/actions/runs/37750479509); 2026-10-08T08:34:01.523003Z.

## Measured inventory — linux/amd64

Runtime: 1.99.0; OS: Debian GNU/Linux 13 (trixie).

| Tool | Version |
| --- | --- |
| bash | GNU bash, version 5.2.37(1)-release (x86_64-pc-linux-gnu) |
| cargo | cargo 1.99.0 (5f94df478 2026-08-27) |
| clippy | clippy 0.1.99 (b940084d7e 2026-09-28) |
| curl | curl 8.14.1 (x86_64-pc-linux-gnu) libcurl/8.14.1 OpenSSL/3.5.7 zlib/1.3.1 brotli/1.1.0 zstd/1.5.7 libidn2/2.3.8 libpsl/0.21.2 libssh2/1.11.1 nghttp2/1.64.0 nghttp3/1.8.0 librtmp/2.3 OpenLDAP/2.6.10 |
| gh | gh version 2.46.0 (2025-01-13 Debian 2.46.0-3) |
| git | git version 2.47.3 |
| jq | jq-1.7 |
| psql | psql (PostgreSQL) 17.11 (Debian 17.11-0+deb13u1) |
| rg | ripgrep 14.1.1 |
| rustc | rustc 1.99.0 (b940084d7 2026-09-28) |
| rustfmt | rustfmt 1.10.0-stable (b940084d7e 2026-09-28) |
| rustup | rustup 1.29.1 (d95a37b6a 2026-08-13) |

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 1,274.9 MiB (1,336,840,122 bytes) |
| Build, cache export and image load | 52.08s |
| Public-artifact behavior and inventory verification | 1.35s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37750479509); 2026-10-08T08:34:01.464104Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

[Release notes](../releases/rust-dev-1.99-trixie-v1.0.1.md).

Capabilities: `rust`, `cargo`, `rustfmt`, `clippy`, `native-build`, `postgresql-client`, `wasm32-unknown-unknown`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- WASM target compilation is tested; a WASM runtime and browser execution are not provided.
- No CUE executable or global third-party Cargo tools are included.
