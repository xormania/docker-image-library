# playwright-browser/1.58-trixie

Version-matched Chromium, Firefox and WebKit browser server without PHP or development build tools.

**Not available:** no verified public release. The following capabilities describe the intended profile.

Capabilities: `playwright`, `chromium`, `firefox`, `webkit`, `browser-server`, `node`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- Use the exact Playwright version pinned by the consuming project.
- Linux/amd64 only. All three engines are included; size savings are measured during validation and publication.
