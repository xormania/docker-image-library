# Composer PHAR

`binary/composer` delivers an exact upstream Composer PHAR. It needs an existing
PHP CLI; it does not supply a PHP runtime, extensions, a database, or application
dependencies. Use an [image](../usage.md) when the target also needs a runtime,
or select a compatible native environment from the catalog when available.

Read the [definition](../../artifacts/binary/composer/definition.json) for intended
inputs and the [typed catalog](../../catalog-v2.json) for accepted releases.
Only an entry marked `available` is an accepted xorder release. A definition or
an upstream download alone does not establish xorder publication or behavior
verification. The initial execution target is `linux/amd64`; upstream Composer
support for other systems is broader than xorder's measured target.

## Select and run

Before choosing this resource, inspect the project's PHP constraint, required
extensions, lockfile and existing Composer pin. PHP CLI 7.2.5 or later with PHAR
support is the upstream minimum, but the project may require newer PHP. Composer
also uses archive tools and version-control clients according to the packages
it installs. Retain an existing compatible project pin unless upgrading it is
part of the task.

Take the exact HTTP reference and SHA-256 from an available catalog entry. Put
the selected bytes in a new version-specific directory and verify them before
execution. For the authored upstream input, this complete example downloads
Composer 2.10.3 directly from its official distribution:

```sh
mkdir -p .xorder-tools/composer-2.10.3
curl --fail --location --proto '=https' --tlsv1.2 \
  https://getcomposer.org/download/2.10.3/composer.phar \
  --output .xorder-tools/composer-2.10.3/composer.phar
printf '%s  %s\n' \
  7a2d379d5b8ffdaa028580ef26494c36d2feef4b178d3dd1473a4dbc5e17c8d6 \
  .xorder-tools/composer-2.10.3/composer.phar | sha256sum --check -
php .xorder-tools/composer-2.10.3/composer.phar --version
```

These are official upstream bytes, separate from an accepted xorder release.
When selecting xorder, substitute its exact released URL and recorded hash.
Never replace either with a moving `latest` URL or use `composer self-update` on
a file tracked by an xorder receipt. Resolve a new release instead.

With a trusted checkout of the source revision from the release record, run the
same readiness check used during publication:

```sh
bash scripts/xorder/verify-composer.sh .xorder-tools/composer-2.10.3
```

It checks the SHA before execution, the PHP prerequisite, the expected Composer
version, embedded upstream license, and offline validation of a locked consumer
fixture. Project dependency installation is a separate check. From the consuming
project, run `php /path/to/composer.phar install` using its own `composer.lock`
and then its documented tests. No global installation is needed.

## Ownership and licensing

The resource's managed destination is `bin/composer.phar` relative to the chosen
installation root. Invoke it with PHP. The PHAR retains upstream license notices;
the [upstream MIT license](../../artifacts/binary/composer/LICENSE.upstream) is
also retained beside the definition. New packaging revisions and upstream
Composer versions are distinct values.

Sources: [Composer downloads and checksums](https://getcomposer.org/download/),
[system requirements and PHAR installation](https://getcomposer.org/doc/00-intro.md),
and [upstream license at 2.10.3](https://github.com/composer/composer/blob/2.10.3/LICENSE).
