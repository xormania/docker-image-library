#!/usr/bin/env bash
set -euo pipefail
cargo test --locked
cargo fmt --check
cargo clippy --locked -- -D warnings
cargo build --locked --target wasm32-unknown-unknown
test -s target/wasm32-unknown-unknown/debug/image_library_fixture.wasm
printf 'native and WASM passed\n' >workspace-proof.txt
