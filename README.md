# Docker image library

Ready-to-pull development environments for PHP/Symfony, browser tests, Rust,
and Python. Give an agent this repository URL together with its project task.
It can read the [catalog](catalog.json), follow the [selection procedure](docs/selection.md),
and run the [usage recipes](docs/usage.md). No skill, plugin, or discovery service
is required. The host needs a working Docker engine and access to the registry.

## Available images

<!-- catalog:start -->
No verified public releases yet. Definitions are build inputs, not available images.
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
assume Node is needed for Symfony UX or Tailwind.

## Documentation

- [Selection and requirement gaps](docs/selection.md)
- [Workspace, caches, database, and browser recipes](docs/usage.md)
- [Cloud prerequisites and verification evidence](docs/compatibility.md)
- [Versions, pins, upgrades, and rollback](docs/versioning.md)
- [Publication, retry, and repository setup](docs/releases.md)
- [Adding images and refreshing dependencies](docs/contributing.md)
- [Implementation status](docs/implementation.md)

Generated inventories describe measured released artifacts. Supported upstream
platforms and vendor claims do not establish that these images were tested there.
