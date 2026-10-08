# xorder

xorder distributes prepared software, development environments, configuration,
and agent context for computers and containers. **Give an agent
https://github.com/xormania/xorder together with its project task.** This README,
the catalog, and the linked usage pages provide discovery without an installed
CLI, skill, plugin, or discovery service.

Start here:

1. Inspect the project's runtime constraints, lockfiles, services, and test needs.
2. Inspect the execution environment and its prerequisites. Images need a working
   Docker engine and registry access; a Docker client alone is insufficient.
3. Read the [catalog](catalog.json) and [selection procedure](docs/selection.md)
   for available resources matching those requirements.
4. Pin an exact verified release and run the [usage/readiness recipe](docs/usage.md)
   before installing project dependencies from their own lockfiles.
5. Report any missing capability or prerequisite precisely. Keep an established
   compatible project pin unless an update is requested.

## Resource kinds

| Kind | Current availability | Purpose |
| --- | --- | --- |
| Images | Verified releases below | Ready-to-pull PHP/Symfony, browser, Rust, and Python toolchains |
| Binaries | Planned | Downloadable software with exact hashes and explicit runtime/platform prerequisites |
| Environments | Planned | Reusable native definitions, starting with devenv and its locked inputs |
| Configuration | Planned | Independently versioned settings installed into explicit owned scopes |
| Context | Planned | Selected guidance or skills for an explicit task, role, or harness |

[Architecture](docs/architecture.md) describes the extension boundaries and
profiles that compose resources. Planned kinds are not selectable releases.
Reading the catalog does not activate context bundles.

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
capabilities, and pin the chosen `digest_reference`. Never pull a guessed tag
from a planned profile. Existing GHCR image names and exact references remain
valid after the repository rename.

## Using an image

Follow [selection](docs/selection.md) and use the selected exact digest in
[usage](docs/usage.md). An optional deterministic helper accepts an explicit
requirements JSON file after cloning this repository:

```sh
python3 scripts/library.py select requirements.json
```

The helper requires Python and the dependencies in `requirements-ci.txt`.
Reading the catalog and following its usage instructions does not require it.

The images supply toolchains. Your project's dependencies and database remain
explicit. `php-browser` adds Chromium and Panther prerequisites; it does not
assume Node is needed for Symfony UX or Tailwind. The
[flowbite-xor profile](docs/flowbite-xor.md) offers PHP 8.4/8.5, adds Node 22 and cached Tailwind to FrankenPHP, and uses
the project-locked official Playwright companion. New lines remain unavailable
until their verified public releases enter the catalog.

## Documentation

- [Architecture, resource boundaries, and discovery](docs/architecture.md)
- [Selection and requirement gaps](docs/selection.md)
- [Workspace, caches, database, and browser recipes](docs/usage.md)
- [FrankenPHP and flowbite-xor development/testing](docs/flowbite-xor.md)
- [Cloud prerequisites and verification evidence](docs/compatibility.md)
- [Versions, pins, upgrades, and rollback](docs/versioning.md)
- [Verified release measurements](docs/metrics.md)
- [Publication, retry, and repository setup](docs/releases.md)
- [Contributing resources and refreshing dependencies](docs/contributing.md)
- [Implementation status](docs/implementation.md)

Generated inventories describe measured released artifacts. Supported upstream
platforms and vendor claims do not establish that these images were tested there.
