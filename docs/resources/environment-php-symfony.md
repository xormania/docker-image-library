# PHP/Symfony with devenv

`environment/php-symfony` supplies PHP 8.4, matching Composer, Symfony CLI,
Git and unzip through native devenv files. It enables intl, mbstring, PDO
PostgreSQL, DOM, bcmath, zip and curl. The project's Composer lock continues to
control its application dependencies.

Choose this resource for a Linux amd64 project on a computer or inside a
container that can use Nix. If Docker is already the chosen runtime, the
[PHP images](../selection.md) supply their own toolchain and Composer.
Installing the Composer binary resource separately is unnecessary here.

Read the available release in [catalog-v2.json](../../catalog-v2.json) for the
exact downloadable archive URL and SHA-256. A definition in `artifacts/` is
authored intent; availability requires a verified published release record.

## Prerequisites and pinned inputs

Install [Nix](https://devenv.sh/getting-started/) with `nix-command` and `flakes`
enabled and a writable Nix store, then install the tested devenv CLI:

```sh
nix profile install 'github:cachix/devenv/b904dcb51fe48c30db250038241507f60752f222#devenv'
devenv --version
```

This source commit is devenv 2.4.0. The native YAML requires that version and
pins both its modules and the nixpkgs input. `devenv.lock` records resolved
source revisions and NAR hashes, including transitive inputs. PHP and other
package versions come from that locked package set; the environment revision
is independent of PHP's patch version. Access to those inputs and upstream
binary caches is needed when their contents are absent locally. A paid cache
or an xorder-specific cache is unnecessary.

## Use in a new project

Download the exact archive from the selected catalog entry and verify its
SHA-256 before extraction. Its root contains `devenv.nix`, `devenv.yaml` and
`devenv.lock`. For a project without existing devenv files, copy all three to
the project root and enter its shell:

```sh
devenv shell
php --version
composer --version
symfony version
composer install
composer check-platform-reqs
```

Project dependencies use `composer install` with the project's lock. For a
single command, use `devenv shell -- composer check-platform-reqs`.

## Compose with project configuration

Keep the extracted native files in `.xorder/php-symfony/`, then use devenv's
local YAML composition. For a project that has no existing devenv definition,
its root `devenv.yaml` can contain:

```yaml
imports:
  - ./.xorder/php-symfony
```

Its root `devenv.nix` can add project settings:

```nix
{ ... }: {
  env.APP_ENV = "dev";
}
```

Copy the delivered `devenv.lock` to the project root before activation. The
publication fixture exercises this exact local import route without updating
the lock. If a project already has devenv inputs, files or a lock, merge the
import and reconcile its existing inputs deliberately. A project that adds
new inputs owns the resulting lock; keep both the xorder release identity and
that project lock in version control.

The PHP version and language-server setting use native `lib.mkDefault`, so
project Nix modules can override them normally. The advertised and tested
resource is PHP 8.4; an override becomes the consuming project's own runtime
choice and must pass its checks.

Local YAML imports can compose the input definitions. Remote input imports
compose Nix modules, while devenv does not currently compose remote YAML
inputs. Importing only the remote Nix module therefore does not automatically
inherit this resource's YAML pins or lock. Use the complete verified native
bundle for the documented route.

## Behavior and lifecycle

This toolchain does not start a database, web server or browser. Projects own
their service configuration. Native `devenv up` and `devenv processes down`
manage the processes configured by that project. The publication fixture adds
its own PHP HTTP process; `devenv test` starts and stops it through devenv's
lifecycle.

Publication runs `bash scripts/xorder/verify-devenv.sh EXTRACTED_ROOT` on Linux
amd64. It composes the delivered native files, installs the existing locked
Symfony dependency fixture, verifies runtime extensions, exercises request
and routing behavior, checks successful and missing HTTP routes, checks
workspace writes, and confirms that the HTTP listener has stopped. Both the
native environment lock and Composer lock must remain unchanged. It does not
claim PostgreSQL connection tests, browser tests, FrankenPHP workers, or
acceptance in every cloud vendor's sandbox.

Upgrade by selecting a newer verified xorder revision and rerunning the
project's checks. `devenv update` changes the native dependency lock and is an
explicit project update, rather than an activation step. Roll back with the
previous verified native files and project lock.

References:

- [devenv 2.4.0 PHP module](https://github.com/cachix/devenv/blob/b904dcb51fe48c30db250038241507f60752f222/src/modules/languages/php.nix)
- [Inputs and locking](https://devenv.sh/inputs/)
- [Native composition](https://devenv.sh/composing-using-imports/)
- [Tests and process lifecycle](https://devenv.sh/tests/)
- [GitHub Actions integration](https://devenv.sh/integrations/github-actions/)
