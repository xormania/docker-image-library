# Implementation status

The initial implementation defines six Debian Trixie / Linux amd64 lines:
PHP development and browser profiles for 8.4 and 8.5, Rust 1.99 and Python 3.14.
The PHP scope is the first release; Rust/Python reuse the same machinery.
The additional `php-frankenphp` and `flowbite-xor-dev` definitions for PHP 8.4
and 8.5 supply worker-mode PHP and a Node 22 derivative with cached Tailwind
and an official Playwright companion. See [the flowbite-xor profile](flowbite-xor.md) for the
pinned source inspection and real consumer acceptance recipe.

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

[Source validation on 8 October 2026](https://github.com/xormania/docker-image-library/actions/runs/37713857904)
passed all six builds and their behavioral recipes: both PHP runtimes and real
Panther browser interactions, Python/PostgreSQL, native/WASM Rust, mounted file
ownership, caches and inventory validation. This is GitHub Actions execution,
not registry publication or a live Claude observation. Publication/writeback
permissions and anonymous pulling must still be exercised after source merge.

Required acceptance: mock requirement scenarios with real Docker behavior using
the documented recipes. Optional: a live Claude cloud observation. No live model
session is needed to complete acceptance, and none is claimed here.
