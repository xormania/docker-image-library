# python-dev/3.14-trixie

Python development with uv, pip, venv, native compilation and PostgreSQL clients.

Available revision: **1.0.1**. Pin:

```text
ghcr.io/xormania/python-dev@sha256:b8fce60b87734551462a90cee2e1c6fbf224082430e09971834d27a6de45e154
```

[Verification evidence](https://github.com/xormania/docker-image-library/actions/runs/37750479509); 2026-10-08T08:34:08.431960Z.

## Measured inventory — linux/amd64

Runtime: 3.14.8; OS: Debian GNU/Linux 13 (trixie).

| Tool | Version |
| --- | --- |
| bash | GNU bash, version 5.2.37(1)-release (x86_64-pc-linux-gnu) |
| curl | curl 8.14.1 (x86_64-pc-linux-gnu) libcurl/8.14.1 OpenSSL/3.5.7 zlib/1.3.1 brotli/1.1.0 zstd/1.5.7 libidn2/2.3.8 libpsl/0.21.2 libssh2/1.11.1 nghttp2/1.64.0 nghttp3/1.8.0 librtmp/2.3 OpenLDAP/2.6.10 |
| gh | gh version 2.46.0 (2025-01-13 Debian 2.46.0-3) |
| git | git version 2.47.3 |
| jq | jq-1.7 |
| pip | pip 26.2.1 from /usr/local/lib/python3.14/site-packages/pip (python 3.14) |
| psql | psql (PostgreSQL) 17.11 (Debian 17.11-0+deb13u1) |
| python | Python 3.14.8 |
| rg | ripgrep 14.1.1 |
| uv | uv 0.12.23 (x86_64-unknown-linux-musl) |

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 593.9 MiB (622,720,013 bytes) |
| Build, cache export and image load | 40.56s |
| Public-artifact behavior and inventory verification | 11.17s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/docker-image-library/actions/runs/37750479509); 2026-10-08T08:34:08.387897Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

[Release notes](../releases/python-dev-3.14-trixie-v1.0.1.md).

Capabilities: `python`, `uv`, `pip`, `venv`, `native-build`, `postgresql-client`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- Install project dependencies from uv.lock, requirements files, or the project manifest.
- Compatibility with a particular project must include its dependencies, not only requires-python.
