# xorder architecture and discovery

xorder makes prepared tools, environments, configuration, and context available
to computers and containers. The public repository URL is the discovery entry
point: [README](../README.md) → catalog or resource page → direct usage and
readiness instructions. GitHub rendering and raw files carry the same information.
An installed CLI, skill, plugin, or separate discovery service is unnecessary.

## Current capability and extension boundaries

The verified resources currently available are [images](../catalog.json). Their
existing definitions, records, commands, GHCR references, and usage remain the
working path. Additional kinds extend that structure as verified examples land:

| Kind | Owns |
| --- | --- |
| Image | OCI identity, platform inventory, toolchain and container behavior |
| Binary | Downloaded bytes, upstream version, checksum, dependencies and invocation |
| Environment | Native backend files, locked inputs, tools/services and activation |
| Configuration | Application/version scope, destination files and update behavior |
| Context | Audience, task/harness scope, source and selected guidance payload |

A profile composes resources for an explicit target; it is not another software
payload. The first binary example will be Composer, whose PHAR requires PHP.
The first environment backend will be devenv, which retains responsibility for
native package resolution and process lifecycle. Neither is available merely
because its intended definition is documented.

## Separate intent, evidence, selection, and target state

| Concept | Responsibility |
| --- | --- |
| Definition | Authored identity, purpose, capabilities, prerequisites and recipe |
| Release record | Exact content, source identity, measured facts and verification evidence |
| Catalog | Compact generated view of eligible releases with direct usage links |
| Profile | Resource selection, requirements, alternatives and target assignments |
| Resolution lock | Exact releases and target assumptions chosen before applying |
| Installation receipt | Owned target files, hashes and activation/recovery state |

Maintain common material once and assign it selectively. This is the useful
fleet pattern: reusable defaults plus explicit assignments. Public profiles
contain reusable examples; private machine inventories and user-specific values
can be supplied separately. Catalog discovery never activates every context
bundle, and delivering an instruction file does not establish that a model
followed it. Current user direction remains authoritative.

Use a small common model with validated kind-specific fields. An OCI digest,
HTTP checksum, native environment lock and installation receipt have different
roles. Preserve them rather than pretending all resources install alike.

## One model, generated compatibility views

Existing image definitions live in `images/`, with measured release evidence in
`release-records/`. Keep those paths and historical facts intact. New resource
definitions belong under `artifacts/<kind>/<name>/` when their implementation
arrives; reusable compositions belong in `profiles/`.

Normalize image data and new resources into one shared model. Generate the
existing schema-1 `catalog.json` as the image compatibility view and a compact
typed `catalog-v2.json` for broader discovery. The latter is an extension target,
not a currently available file. Both views must share sources and cannot be
edited independently. Keep existing script entry points and selection behavior
while common responsibilities move into small shared modules.

Detailed inventories remain linked evidence; discovery should not require
loading every OS package or context payload. Only tested, publicly retrievable
releases become available. Target checks distinguish unsupported variants,
missing prerequisites, unavailable downloads and untested execution surfaces.

## Delivery and application

Keep current image package names in GHCR. Use GitHub Releases initially for
downloadable artifacts and bundles. Locations may gain CDN mirrors later;
content identity remains an exact digest or checksum. Reuse release orchestration
and evidence while each kind owns its build and behavior checks.

Resolve exact selected resources before applying them. Stage and verify bytes,
materialize only selected scopes, track owned files, and preserve locally edited
or unrelated destinations. Native backends own their services. Installing context
or changing configuration is independent of building a toolchain. Optional
helpers use these same operations; direct documented use remains available.

## Repository rename and image provenance

The canonical URL is https://github.com/xormania/xorder. Current navigation uses
that identity; historical source/run links can retain their original provenance.
GHCR family names and exact references do not change with the repository name.

Dockerfile source labels remain on the old URL until the next deliberate patch
refresh. Their bytes affect image fingerprints, so updating them requires fresh
affected revisions and normal publication. See [contributing](contributing.md)
for that explicit next-refresh item and [versioning](versioning.md) for the
existing exact-release contract.
