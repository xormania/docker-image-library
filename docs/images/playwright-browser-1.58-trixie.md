# playwright-browser/1.58-trixie

Version-matched Chromium, Firefox and WebKit browser server without PHP or development build tools.

Available revision: **1.0.0**. Pin:

```text
ghcr.io/xormania/playwright-browser@sha256:0e16fe1ce8a199880035fc6d9937682c18cc8d9b4b732f228716d33942831f76
```

[Verification evidence](https://github.com/xormania/xorder/actions/runs/38055213253); 2026-10-10T13:23:00.666640Z.

## Measured inventory — linux/amd64

Runtime: 1.58.2; OS: Debian GNU/Linux 13 (trixie).

| Tool | Version |
| --- | --- |
| node | v22.23.3 |
| playwright | Version 1.58.2 |

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 2,213.9 MiB (2,321,443,126 bytes) |
| Build, cache export and image load | 156.17s |
| Public-artifact behavior and inventory verification | 4.99s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38055213253); 2026-10-10T13:23:00.606311Z.

External build cache at start: `empty`. This does not assert that every layer was a cache hit.

[Release notes](../releases/playwright-browser-1.58-trixie-v1.0.0.md).

Capabilities: `playwright`, `chromium`, `firefox`, `webkit`, `browser-server`, `node`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- Use the exact Playwright version pinned by the consuming project.
- Linux/amd64 only. All three engines are included; size savings are measured during validation and publication.
