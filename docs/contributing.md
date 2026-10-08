# Maintaining and expanding the library

Use feature branches and PRs against master. The canonical source layout is:

| Path | Responsibility |
| --- | --- |
| `images/*/definition.json` | Authored intent, runtime/OS lines, revisions, capabilities, limitations and changes |
| `images/*/Dockerfile` | Build recipe |
| `images/shared/` | Shared tools and workspace/user handling |
| `images/tools.json` | Resolved Composer/uv digests, PECL versions and verified Symfony CLI artifact |
| `release-records/<family>/<line>/<revision>.json` | Published, behavior-tested release facts; created by publication |
| `schemas/` | Definition/release/catalog structure; cross-field invariants live in the validator |
| `catalog.json`, README table, `docs/images/`, `docs/releases/` | Generated outputs |
| `scripts/` | Small build, inventory, release, generation and refresh helpers |
| `tests/fixtures/`, `tests/requirements/` | Locked real consumer fixtures and independent mock requirements |

Local metadata validation:

```sh
python3 -m pip install -r requirements-ci.txt
python3 scripts/library.py generate
python3 scripts/library.py check
python3 -m unittest discover -s tests -v
```

On a Docker-capable host, use `scripts/build.py LINE_ID LOCAL_TAG` and
`scripts/verify-image.sh LINE_ID IMAGE`. Browser build input must be the exact
matching php-dev artifact; PR tests use the just-built local parent. Publication
uses its immutable registry digest. Image builds collect measured versions,
packages, runtime and extensions using `scripts/inventory.py`.

Before editing a released recipe/input, allocate the appropriate image revision
and write meaningful `changes` plus migration guidance in the line definition.
Do not hand-edit measured tool versions in generated docs. A global shared tool
refresh intentionally changes all consumers; image-specific changes stay scoped.
README/docs/record-only PRs do not rebuild images. The release jobs additionally
skip source-identical lines already in the accepted ledger.

Validation scopes container jobs to changed recipes and consuming fixtures;
release orchestration and unit-test changes still run metadata tests. Unknown
build/verification helpers conservatively select all images. Publication also
checks the accepted ledger before allocating runners, retaining incomplete PHP
parent/browser pairs and changed-input guards.

Build caches use family-specific input fingerprints rather than commit SHAs.
Source labels are applied after install layers. Each image revision is passed
as `APT_REFRESH`, intentionally invalidating Debian package installs during a
weekly refresh. PHP CI uses Docker's containerd image store so its exact local
parent remains visible while both parent and browser caches can be exported.
Build artifacts and job summaries retain image size and build/verification
times. A source-label-only rebuild checks that filesystem layers stay identical.

`Refresh build inputs` runs weekly and manually. It resolves upstream digests,
PECL versions and the Symfony artifact checksum, then stages fresh patch
revisions in a PR. It allocates a rebuild even if pins are unchanged so Debian
packages can refresh. Review upstream compatibility/security changes and adjust
the revision when a patch refresh would break the contract. Never reuse an exact
release for a fresh build. Dependabot proposes Actions/validation dependency
updates separately.

Fixtures have committed Composer, uv and Cargo locks. Updating a fixture lock
is a source change and reruns behavior, rather than substituting the fixture's
dependency versions for the consuming project's own lock. No global PHPUnit,
Panther, CUE or speculative Cargo tools are bundled.

To add a family/line, inspect the target project's requirements, choose an
official upstream base and resolve its digest, define its intended profile,
extend the build/inventory/behavior recipes, add independent selection scenarios,
and keep it unavailable until the shared publication path produces a verified
record. Extend platform schema/build/tests together before adding arm64.
Do not create a second catalog, pipeline service, MCP server or agent skill.

Pins make build inputs traceable; apt repositories and project download
services still change. Byte-for-byte reproducible rebuilds are not claimed.
