# Docker image library

Ready-to-pull development environments for PHP/Symfony, browser tests, Rust,
and Python. Give an agent this repository URL together with its project task.
It can read the [catalog](catalog.json), follow the [selection procedure](docs/selection.md),
and run the [usage recipes](docs/usage.md). No skill, plugin, or discovery service
is required. The host needs a working Docker engine and access to the registry.

## Available images

<!-- catalog:start -->
| Line | Revision | Verified platform | Exact reference |
| --- | --- | --- | --- |
| [flowbite-xor-dev/8.4-trixie](docs/images/flowbite-xor-dev-8.4-trixie.md) | 1.0.0 | linux/amd64 | `ghcr.io/xormania/flowbite-xor-dev:8.4-trixie-v1.0.0` |
| [flowbite-xor-dev/8.5-trixie](docs/images/flowbite-xor-dev-8.5-trixie.md) | 1.1.0 | linux/amd64 | `ghcr.io/xormania/flowbite-xor-dev:8.5-trixie-v1.1.0` |
| [php-browser/8.4-trixie](docs/images/php-browser-8.4-trixie.md) | 1.1.0 | linux/amd64 | `ghcr.io/xormania/php-browser:8.4-trixie-v1.1.0` |
| [php-browser/8.5-trixie](docs/images/php-browser-8.5-trixie.md) | 1.1.0 | linux/amd64 | `ghcr.io/xormania/php-browser:8.5-trixie-v1.1.0` |
| [php-dev/8.4-trixie](docs/images/php-dev-8.4-trixie.md) | 1.1.0 | linux/amd64 | `ghcr.io/xormania/php-dev:8.4-trixie-v1.1.0` |
| [php-dev/8.5-trixie](docs/images/php-dev-8.5-trixie.md) | 1.1.0 | linux/amd64 | `ghcr.io/xormania/php-dev:8.5-trixie-v1.1.0` |
| [php-frankenphp/8.4-trixie](docs/images/php-frankenphp-8.4-trixie.md) | 1.0.0 | linux/amd64 | `ghcr.io/xormania/php-frankenphp:8.4-trixie-v1.0.0` |
| [php-frankenphp/8.5-trixie](docs/images/php-frankenphp-8.5-trixie.md) | 1.0.0 | linux/amd64 | `ghcr.io/xormania/php-frankenphp:8.5-trixie-v1.0.0` |
| [python-dev/3.14-trixie](docs/images/python-dev-3.14-trixie.md) | 1.1.0 | linux/amd64 | `ghcr.io/xormania/python-dev:3.14-trixie-v1.1.0` |
| [rust-dev/1.99-trixie](docs/images/rust-dev-1.99-trixie.md) | 1.1.0 | linux/amd64 | `ghcr.io/xormania/rust-dev:1.99-trixie-v1.1.0` |
<!-- catalog:end -->

Use catalog entries marked `available`, check their verified architecture and
capabilities, and pin the chosen `digest_reference`. Keep an existing compatible
project pin unless an update is requested. Never pull a guessed tag from a
planned profile.

## Using an image

1. Read the project's runtime constraints, extensions, lockfiles, services, and test needs.
2. Follow [selection](docs/selection.md), or pass a requirements JSON file to
   `python3 scripts/library.py select requirements.json` after cloning this repository.
3. Use the exact digest from the result in [usage](docs/usage.md).
4. Run its readiness checks; install project dependencies from project lockfiles.

The images supply toolchains. Your project's dependencies and database remain
explicit. `php-browser` adds Chromium and Panther prerequisites; it does not
assume Node is needed for Symfony UX or Tailwind. The
[flowbite-xor profile](docs/flowbite-xor.md) offers PHP 8.4/8.5, adds Node 22 and cached Tailwind to FrankenPHP, and uses
the project-locked official Playwright companion. New lines remain unavailable
until their verified public releases enter the catalog.

## Documentation

- [Selection and requirement gaps](docs/selection.md)
- [Workspace, caches, database, and browser recipes](docs/usage.md)
- [FrankenPHP and flowbite-xor development/testing](docs/flowbite-xor.md)
- [Cloud prerequisites and verification evidence](docs/compatibility.md)
- [Versions, pins, upgrades, and rollback](docs/versioning.md)
- [Verified release measurements](docs/metrics.md)
- [Publication, retry, and repository setup](docs/releases.md)
- [Adding images and refreshing dependencies](docs/contributing.md)
- [Implementation status](docs/implementation.md)

Generated inventories describe measured released artifacts. Supported upstream
platforms and vendor claims do not establish that these images were tested there.
