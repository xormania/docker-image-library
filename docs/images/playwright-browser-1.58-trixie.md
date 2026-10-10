# playwright-browser/1.58-trixie

Version-matched Chromium, Firefox and WebKit browser server without PHP or development build tools.

Available revision: **1.0.1**. Pin:

```text
ghcr.io/xormania/playwright-browser@sha256:72a68659cad38ce291d683a198a150c1d959e3ded6287ea4c7bd033e0599a63b
```

[Verification evidence](https://github.com/xormania/xorder/actions/runs/38082421686); 2026-10-10T20:15:37.538408Z.

## Measured inventory — linux/amd64

Runtime: 1.58.2; OS: Debian GNU/Linux 13 (trixie).

| Tool | Version |
| --- | --- |
| node | v22.23.3 |
| playwright | Version 1.58.2 |

### Release measurements — linux/amd64

| Metric | Measured value |
| --- | ---: |
| Local image size | 2,213.9 MiB (2,321,443,157 bytes) |
| Build, cache export and image load | 173.82s |
| Public-artifact behavior and inventory verification | 226.19s |

Size method: `docker-image-inspect-size`; image store: `overlay2/classic`. [Measurement evidence](https://github.com/xormania/xorder/actions/runs/38082421686); 2026-10-10T20:16:22.300063Z.

External build cache at start: `restored`. This does not assert that every layer was a cache hit.

Size baseline: v1.0.0, `ghcr.io/xormania/playwright-browser@sha256:0e16fe1ce8a199880035fc6d9937682c18cc8d9b4b732f228716d33942831f76`; 2,213.9 MiB in the same image store. Change: **+0.0%**. [Baseline measurement](https://github.com/xormania/xorder/actions/runs/38055213253); 2026-10-10T13:23:00.606311Z.

[Release notes](../releases/playwright-browser-1.58-trixie-v1.0.1.md).

Capabilities: `playwright`, `chromium`, `firefox`, `webkit`, `browser-server`, `node`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- Use the exact Playwright version pinned by the consuming project.
- Linux/amd64 only. All three engines are included; size savings are measured during validation and publication.
