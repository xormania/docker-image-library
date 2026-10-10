# Prepared Serena for PHP and Symfony

`php-serena/8.5-trixie` adds Serena v2 REPL and PHPactor to xorder's PHP 8.5
development image. It is an independent stdio MCP service for source discovery
and editing. The [catalog](../catalog-v2.json) is the availability authority:
the authored image is not available until publication and verification produce
an accepted release record. No image is pulled automatically during MCP startup.

## Use with flowbite-xor

Select an available `image/php-serena/8.5-trixie` entry from the catalog, pull its
exact digest, and retain it in the MCP client's configuration. Configure the
client to launch this command, supplying absolute paths and the selected digest:

```sh
python3 /path/to/xorder/examples/serena/run.py /path/to/flowbite-xor \
  --project demo --image "$SERENA_IMAGE"
```

The runner mounts the whole checkout at `/workspace` and activates
`/workspace/demo`. This keeps the demo's sibling kit source and Composer path
mappings visible. Use `--project .` for a PHP project at the checkout root.
Install dependencies from the consuming application's own Composer lock with its
normal development runner before using Serena. This image does not supply a
substitute application `vendor/`. Existing flowbite-xor app/browser images and
their launch configuration remain useful independently.

The image defaults to the persistent `serena_repl` interface. Call
`initial_instructions` first, then pass its issued session ID as `session` on every
`serena_repl` call, with Python in `code`. For example, within one Serena session:

```python
s.info('lsp.find_symbol', 'lsp.find_referencing_symbols')
s.lsp.find_symbol('CspNonce', relative_path='src/Security/CspNonce.php')
s.lsp.find_referencing_symbols('CspNonce', 'src/Security/CspNonce.php')
```

Use upstream API discovery for the selected revision. The REPL retains variables
between cells. A failed cell may already have edited source: inspect its textual
error and the resulting files before retrying. Reconnecting starts a new REPL;
variables and temporary indexes/memories are lost, while source edits remain.
There is no automatic replay of a failed or interrupted cell.

## Workspace and session behavior

The Linux/amd64 runner requires Python 3.9+ and a working Docker engine with the
chosen image already present. Each invocation creates a separate container and
temporary state, preserving parallel worktree/session separation. It runs as the
host UID/GID, keeps protocol stdout clean, disables runtime networking, and
exposes only the selected checkout. It mounts no host home or Docker socket.
The checkout is read-only by default, enforced by the mount as well as upstream
editing APIs. Pass `--write` explicitly to allow the REPL and PHP tooling to modify
a trusted checkout. `--read-only` explicitly selects the default behavior.

Startup completes PHPactor's initial project index before exposing MCP. Cold
startup therefore takes longer for large dependency trees, but the first reference
query sees a complete initial index. Indexing uses the private session cache and
does not require runtime networking or write generated files into the checkout.

Serena's Python REPL has the container user's capabilities. This runner does not
implement Agentscient's role policy, operation locks, process auditing or work
coordination. Give concurrent editing sessions separate worktrees, or coordinate
their writes through the owning application.

The launcher reads existing `.serena/project.yml` and `project.local.yml`, applies
the prepared PHPactor default when no backend is selected, and keeps generated
configuration outside the source tree. Repository activation commands and
language-server-specific settings are discarded; global trusted project paths are
explicitly empty. A `phpactor_version` or `ls_path` override is rejected with an
actionable error, as is an incompatible backend selection. This profile
uses session-local state and does not persist newly written Serena memories.

## What the Symfony profile establishes

The image provides PHP semantic tools, a PHP runtime and Composer. Acceptance
uses actual flowbite-xor Symfony source: class/method lookup, cross-file references,
an edit and semantic reread, persistent REPL variables, a partial edit followed by
an error, and a fresh read-only session. PHP attributes and constructor types are
present in this consumer. This does not establish semantic Twig navigation,
resolution of service identifiers from YAML, or runtime container inspection.
Use the application's installed Symfony/Mate capabilities for runtime facts.

Dependency installation happens before acceptance starts the network-disabled
MCP runner. The test establishes offline language-server startup and operations;
it does not claim that an arbitrary application's dependencies are already cached.

## Build, verify and update

The parent is the exact PHP 8.5/Trixie artifact selected by xorder's normal build
and publication machinery. Existing accepted parents are reused. To build a
candidate with an explicitly chosen accepted parent:

```sh
python3 scripts/build.py php-serena/8.5-trixie image-library-serena:candidate \
  --parent "$PHP_DEV_DIGEST" --inventory out/php-serena.json
```

The shared verifier checks inherited PHP capabilities and runs
`tests/fixtures/serena/check.py` against its pinned flowbite-xor revision. The
fixture clones a disposable checkout, installs its Composer lock without scripts
or plugins, and drives the public runner through real stdio MCP. No model account
is required. Evidence is written to `out/serena/acceptance.json`; CI retains it
alongside image inventory and metrics. Publication repeats behavior checks before
catalog availability. A passing PR test is not a published artifact.

Serena source and its upstream `uv.lock` are pinned to
`b79e2a55f9d4072084977dd35bd07d31146d88b9` (v2 beta). The Dockerfile pins uv and
PHPactor; `requirements-build.txt` contains the hash-checked build-tool closure.
Installation uses `uv sync --locked --no-build-isolation` and checks that upstream
metadata remains unchanged. Source and upstream licenses remain in
`/opt/serena-source`. The inherited PHP image owns its OS package provenance;
this Trixie variant does not claim Agentscient's Bookworm snapshot configuration
or byte-identical rebuilds.

Update source/backend pins together when needed, regenerate the build-tool closure
against that source's lock, allocate a new image revision, and repeat real MCP
acceptance. A source-label check alone cannot prove that packaging changes landed;
select by the verified image digest and measured inventory.

## Reference lineage

This package applies the existing Agentscient work, inspected on `dev` on
2026-10-10, to a standalone xorder distribution:

- [PR 304](https://github.com/uscient/agentscient/pull/304): selected v2 beta REPL,
  persistent state, real PHP discovery/editing, partial failures and restart.
- [PR 316](https://github.com/uscient/agentscient/pull/316): separate container
  provider, prepared checksum-pinned PHPactor, offline execution and workspace
  binding. It superseded the initial Intelephense packaging for this route.
- [PR 373](https://github.com/uscient/agentscient/pull/373): upstream runtime lock
  plus a separately locked build-tool closure, exact source and artifact checks.
- [PR 380](https://github.com/uscient/agentscient/pull/380): observe-only process
  auditing and its limits. That Agentscient-owned observer is not included here.

The prior Serena readiness and session-handoff research supplied acceptance cases;
current source supplied implementation facts. Agentscient's coordination policies
are not imposed on independent projects. Upstream remains
[oraios/serena](https://github.com/oraios/serena/tree/b79e2a55f9d4072084977dd35bd07d31146d88b9).
