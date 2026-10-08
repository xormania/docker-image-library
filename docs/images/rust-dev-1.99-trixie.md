# rust-dev/1.99-trixie

Rust 2024 native compilation, Clippy, formatting and wasm32-unknown-unknown builds.

**Not available:** no verified public release. The following capabilities describe the intended profile.

Capabilities: `rust`, `cargo`, `rustfmt`, `clippy`, `native-build`, `postgresql-client`, `wasm32-unknown-unknown`.

Workspace `/workspace`, HOME `/home/dev`, default UID/GID 1000; configure `PUID` and `PGID`.

[Usage](../usage.md) · [Selection](../selection.md) · [Compatibility evidence](../compatibility.md)

## Limitations

- WASM target compilation is tested; a WASM runtime and browser execution are not provided.
- No CUE executable or global third-party Cargo tools are included.
