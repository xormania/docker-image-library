# Verified downloadable resources

Generated from accepted release records. Read the prerequisites and usage before applying a resource. Targets describe compatibility; verification evidence records the actual execution surface. Do not infer behavior in every vendor cloud. Profiles select these exact releases; authored definitions without records remain unavailable.

## binary/composer v1.0.0

Exact upstream Composer PHAR for a target that already has compatible PHP CLI.

Exact identity: `sha256:7a2d379d5b8ffdaa028580ef26494c36d2feef4b178d3dd1473a4dbc5e17c8d6`. Declared targets: linux/amd64.

Required commands: `php`.

- PHP CLI 7.2.5 or later with PHAR support; this resource does not install PHP.
- The consuming project's extensions, services, archive tools and dependencies remain explicit.

[Usage](../../docs/resources/binary-composer.md) · [Download](https://github.com/xormania/xorder/releases/download/binary/composer/v1.0.0/composer.phar) (file, 3,642,137 bytes) · [Release record](../../release-records/artifacts/binary/composer/1.0.0.json) · [Verification evidence](https://github.com/xormania/xorder/actions/runs/37861336161) (github-actions-linux-amd64).

## configuration/editorconfig v1.0.0

Small project-local EditorConfig starting point for PHP and common repository files.

Exact identity: `sha256:5aa2360af22e47bb84708bd2262268527f7359e94f224f04213c0fc929dbddea`. Declared targets: any.

Required commands: none.

- An editor with EditorConfig support is needed to apply the formatting settings.

[Usage](../../docs/resources/configuration-editorconfig.md) · [Download](https://github.com/xormania/xorder/releases/download/configuration/editorconfig/v1.0.0/editorconfig-1.0.0.tar) (tar, 10,240 bytes) · [Release record](../../release-records/artifacts/configuration/editorconfig/1.0.0.json) · [Verification evidence](https://github.com/xormania/xorder/actions/runs/37863331446) (github-actions-linux-amd64).

## context/project-guidance v1.0.0

Example Codex project-local guidance delivered explicitly as AGENTS.md.

Exact identity: `sha256:4a1c7ff451e8f835c1d921c9a212af8d129e3ed166789d3cd52c9c01aef442ff`. Declared targets: any.

Required commands: none.

- Select only when project-local Codex guidance is wanted; review the sample before adoption.

[Usage](../../docs/resources/context-project-guidance.md) · [Download](https://github.com/xormania/xorder/releases/download/context/project-guidance/v1.0.0/project-guidance-1.0.0.tar) (tar, 10,240 bytes) · [Release record](../../release-records/artifacts/context/project-guidance/1.0.0.json) · [Verification evidence](https://github.com/xormania/xorder/actions/runs/37863331446) (github-actions-linux-amd64).

## environment/php-symfony v1.0.0

A reusable native devenv PHP 8.4 and Symfony development toolchain for a project on Linux amd64.

Exact identity: `sha256:59ae1dd08d906bb3c897e7c4b26ad2dcfe0d9cd7bc76a3fe08132a1908be3c6f`. Declared targets: linux/amd64.

Required commands: `nix`, `devenv`.

- Nix with nix-command and flakes enabled
- devenv 2.4.0
- Writable Nix store and access to the locked upstream inputs and binary caches

[Usage](../../docs/resources/environment-php-symfony.md) · [Download](https://github.com/xormania/xorder/releases/download/environment/php-symfony/v1.0.0/php-symfony-1.0.0.tar) (tar, 10,240 bytes) · [Release record](../../release-records/artifacts/environment/php-symfony/1.0.0.json) · [Verification evidence](https://github.com/xormania/xorder/actions/runs/37863331446) (github-actions-linux-amd64).

