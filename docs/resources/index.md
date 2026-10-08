# Verified downloadable resources

Generated from accepted release records. Read the prerequisites and usage before applying a resource. Targets describe the published verification claim; they do not establish behavior in every vendor cloud. Profiles select these exact releases; authored definitions without records remain unavailable.

## binary/composer v1.0.0

Exact upstream Composer PHAR for a target that already has compatible PHP CLI.

Exact identity: `sha256:7a2d379d5b8ffdaa028580ef26494c36d2feef4b178d3dd1473a4dbc5e17c8d6`. Tested targets: linux/amd64.

Required commands: `php`.

- PHP CLI 7.2.5 or later with PHAR support; this resource does not install PHP.
- The consuming project's extensions, services, archive tools and dependencies remain explicit.

[Usage](../../docs/resources/binary-composer.md) · [Release record](../../release-records/artifacts/binary/composer/1.0.0.json) · [Verification evidence](https://github.com/xormania/xorder/actions/runs/37861336161) (github-actions-linux-amd64).

