# Reusable PHP test tasks

Select a verified PHP image with `php-testing` and `pcov` capabilities from the
[catalog](../catalog-v2.json). Authored new revisions remain unavailable until
their normal build, behavioral verification, publication and release-record
acceptance complete. Earlier image revisions retain their existing tools.
The authored [`profile/php-tests`](../profiles/php-tests.json) selects the new
PHP 8.5 CLI line; it resolves only after that exact image revision is available.
FrankenPHP and browser-derived lines inherit the same test capabilities.

`library-php-tests` offers independently usable PHPUnit, coverage and PHPStan
commands. `all` runs PHPUnit with coverage, followed by PHPStan. It stops on the
first failure and returns the tool's exit status. The image supplies PHP extensions and orchestration; the project
owns its test cases, PHPUnit version, configurations, bootstraps and assertions.

Install the selected project's development dependencies from `composer.lock`
before testing. The runner checks that the tool's installed package version and
source/dist references match that lock, and invokes the project's `vendor/bin`
proxy. It never downloads a different PHPUnit through a Symfony bridge or
installs a global PHPUnit. A missing tool or stale installed tool fails before
the aggregate command begins. `composer install`, platform checks and ordinary
dependency audit remain separate project setup/checks.

Inside a selected image with the project mounted at `/workspace`:

```sh
cd /workspace
library-php-tests phpunit
library-php-tests coverage --filter 'ImportantBehavior'
library-php-tests phpstan --level=max src
library-php-tests all
```

Existing Compose workflows can execute the same commands inside their app
container. Supply the project's database, app and test environment as usual.
Configuration auto-discovery follows each tool's own behavior; explicit files
are supported when the defaults do not fit.

| Variable | Meaning and default |
| --- | --- |
| `PHPUNIT_PROJECT` | Directory containing PHPUnit's Composer lock and installed `vendor/bin/phpunit`; current directory |
| `PHPSTAN_PROJECT` | Directory containing PHPStan's Composer lock and installed `vendor/bin/phpstan`; current directory |
| `PHPUNIT_CONFIGURATION` | Optional PHPUnit XML path, absolute or relative to `PHPUNIT_PROJECT` |
| `PHPSTAN_WORKSPACE` | Analysis working directory, independently of the tools installation; current directory |
| `PHPSTAN_CONFIGURATION` | Optional PHPStan configuration path, absolute or relative to `PHPSTAN_WORKSPACE` |
| `PHPSTAN_AUTOLOAD_FILE` | Optional application autoloader, absolute or relative to `PHPSTAN_WORKSPACE` |
| `PHPSTAN_PATHS` | Optional JSON array of analysis paths when they are not declared by the project's config |
| `COVERAGE_DRIVER` | `pcov` (default) or `xdebug` |
| `COVERAGE_SOURCE` | Source directory for PCOV; PHPUnit project's `src/` when present, otherwise the PHPUnit project |
| `COVERAGE_CLOVER` | Clover output path; PHPUnit project's `var/coverage/clover.xml` |

Both projects may differ from the mounted workspace root. Absolute source,
bootstrap and analysis paths are useful when the kit and demo are separate.
The PHPUnit XML remains authoritative for its coverage include/exclude filter;
set `COVERAGE_SOURCE` to include the code that filter names. PCOV collects line
coverage; use Xdebug and the project's PHPUnit options when path coverage is
needed. Extra CLI arguments belong to the individual task; `all` accepts its
configuration through the environment.

## Prepared mutation testing

The PHP images also supply [Infection 0.35.6](https://github.com/infection/infection/releases/tag/0.35.6).
Publication downloads its independent PHAR and checks the upstream SHA-256
recorded in `images/tools.json`. Consumers need no GitHub download to invoke
`infection`. Its launcher enables Xdebug coverage only for that invocation and
its child test processes; PCOV stays disabled, and existing workers keep their
configuration. Mutation testing is an explicit task, independent of the `all`
coverage/PHPStan aggregate.

The consuming project owns its Infection configuration, source directories,
PHPUnit installation and score policy. For a kit with PHPUnit under `demo/`, an
`infection.json` in the kit root can explicitly select both kit and recipe PHP:

```json
{
  "source": {"directories": ["src", "recipes"]},
  "phpUnit": {"configDir": "demo", "customPath": "demo/vendor/bin/phpunit"},
  "bootstrap": "demo/vendor/autoload.php",
  "logs": {"summaryJson": "demo/var/mutation-summary.json"}
}
```

```sh
infection --configuration=infection.json --threads=2 --no-progress --no-interaction
```

Source paths and exclusions follow [Infection's configuration contract](https://infection.github.io/guide/usage.html).
The PHPUnit coverage filter must include those recipe paths too. Supply score
thresholds explicitly when establishing a gate; a report can first show which
mutants escape. The image fixture uses its own pinned PHPUnit 13.4.1 dependency
closure and proves that a boundary assertion kills a comparison mutant while a
type-only assertion lets it escape. It runs the installed PHAR, checks its JSON
results and preserves the fixture lock.

## Optional prepared PHPStan

The image also prepares PHPStan 2.3.0, its Symfony extension 2.1.0 and its PHPUnit
extension 2.1.1 from the independent
[`images/shared/php-tools-composer.lock`](../images/shared/php-tools-composer.lock)
under `/opt/xorder/php-tools`. This tools directory contains no app dependencies
or global PHPUnit. Select it explicitly if the app has no PHPStan package, or
keep the project's own PHPStan lock with the default project selection.

```sh
PHPUNIT_PROJECT=/workspace/demo \
PHPSTAN_PROJECT=/opt/xorder/php-tools \
PHPSTAN_WORKSPACE=/workspace \
PHPSTAN_CONFIGURATION=/workspace/tools/phpstan.neon \
PHPSTAN_AUTOLOAD_FILE=/workspace/demo/vendor/autoload.php \
PHPSTAN_PATHS='["demo/src/Demo", "demo/tests", "recipes/my-recipe/src"]' \
COVERAGE_SOURCE=/workspace/src \
library-php-tests all
```

PHPStan executes from `PHPSTAN_WORKSPACE`, independently of where its pinned
packages live. Explicit paths/configuration identify the app being analyzed.
The application autoloader is supplied by the
project's PHPStan configuration/CLI options as it is in CI. xorder does not
replace it with the tools directory's autoloader.

## Per-process coverage

Both PCOV and Xdebug coverage hooks are disabled by default. The upstream
[PCOV interoperability contract](https://github.com/krakjoe/pcov#interoperability)
requires avoiding a loaded Xdebug when PCOV is enabled. The coverage launcher
copies the current CLI configuration into temporary files, removes Xdebug's
loader directives, retains the remaining main/scanned settings, and enables
PCOV for that child process. It removes those files on completion. Existing app
workers and subsequent commands keep their original settings.

```sh
COVERAGE_SOURCE=/workspace/src library-php-coverage pcov vendor/bin/phpunit --coverage-text
library-php-coverage xdebug vendor/bin/phpunit --coverage-text
```

`xdebug` enables `XDEBUG_MODE=coverage` and explicitly disables PCOV. PCOV's
stable input is pinned to [1.0.12](https://pecl.php.net/package/pcov/1.0.12) and
included in the normal upstream refresh workflow. The image acceptance fixture
checks the actually executed and unexecuted source return lines with both
drivers, confirms PCOV runs without Xdebug, and confirms ordinary PHP still
loads Xdebug with PCOV disabled afterward. Compatibility with the selected
PHP runtime is established by those image builds rather than inferred solely
from the extension's minimum PHP requirement.
