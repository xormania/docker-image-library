# Implementation status

The initial implementation defines six Debian Trixie / Linux amd64 lines:
PHP development and browser profiles for 8.4 and 8.5, Rust 1.99 and Python 3.14.
The PHP scope is the first release; Rust/Python reuse the same machinery.

Runtime choices were checked against project manifests on 8 October 2026:
`flowbite-xor/demo/composer.json` requires PHP >=8.4 and Symfony 8.1;
`cue-rust/Cargo.toml` declares Rust 1.96 and edition 2024;
`chess-crawl/pyproject.toml` declares Python >=3.11 and psycopg. Rust 1.99
and Python 3.14 are available stable upstream lines at input resolution time.
These constraints justify candidates; they do not establish that every project
dependency works without the project's own validation.

Implemented: definitions and schemas, a deterministic catalog/docs generator,
selection scenarios and pin preservation, shared workspace handling, locked
real consumer fixtures, PHP/browser/native/WASM/Python recipes, Actions CI,
candidate/durable-record/exact publication, PR writeback, accepted aliases and
weekly/manual refresh PRs.

Availability is represented only by [catalog.json](../catalog.json). This status
document never promotes a definition to a published image. CI and publication
results, exact digests, dates and inventories are retained by workflow artifacts
and verified release records. First publication needs the concrete repository
settings listed in [releases](releases.md), including public GHCR visibility.

Required acceptance: mock requirement scenarios with real Docker behavior using
the documented recipes. Optional: a live Claude cloud observation. No live model
session is needed to complete acceptance, and none is claimed here.
