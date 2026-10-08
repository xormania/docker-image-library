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
3. Read the compact [catalog](catalog-v2.json) for available resources matching
   those requirements; image inventories remain in the [image view](catalog.json).
4. Follow the entry's usage link, pin its exact `identity`, and run its readiness
   recipe before installing project dependencies from their own lockfiles.
5. Report any missing capability or prerequisite precisely. Keep an established
   compatible project pin unless an update is requested.

## Resource kinds

| Kind | Current availability | Purpose |
| --- | --- | --- |
| Images | Verified releases below | Ready-to-pull PHP/Symfony, browser, Rust, and Python toolchains |
| Binaries | No verified release yet | Downloadable software with exact hashes and explicit runtime/platform prerequisites |
| Environments | No verified release yet | Reusable native definitions, starting with devenv and its locked inputs |
| Configuration | No verified release yet | Independently versioned settings installed into explicit owned scopes |
| Context | No verified release yet | Selected guidance or skills for an explicit task, role, or harness |

[Architecture](docs/architecture.md) describes the extension boundaries and
profiles that compose resources. Planned kinds are not selectable releases.
Reading the catalog does not activate context bundles.

## Available downloadable resources

<!-- resources:start -->
No verified non-image releases yet. Authored definitions are not available artifacts.
<!-- resources:end -->

The generated [resource index](docs/resources/index.md) links verified usage,
prerequisites, release records, and evidence as new resources become available.

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
capabilities, and pin the chosen `identity` (`digest_reference` in the image view).
Never pull a guessed tag
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

## Optional discovery helper

After cloning, Python 3 and `requirements-ci.txt` provide the same catalog through
read-only commands:

```sh
python3 scripts/xorder_cli.py list
python3 scripts/xorder_cli.py show image/php-dev/8.5-trixie
python3 scripts/xorder_cli.py resolve profile.json --target target.json
```

The last command reads an authored local profile and observed target facts; it
prints an exact resolution lock or precise requirement gaps and changes no files.
[Architecture](docs/architecture.md#read-only-profile-resolution) describes the
inputs, existing pins, and explicit private overlays. Discovery through the URL
and direct usage pages remains sufficient.

## Documentation

- [Architecture, resource boundaries, and discovery](docs/architecture.md)
- [Verified downloadable resources and prerequisites](docs/resources/index.md)
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
