# Example project guidance for Codex

`context/project-guidance` contains a short, public example of project guidance.
It demonstrates explicit context delivery. It is not xor's personal instruction
set, a reconstruction of past chats, or a promise that an agent will obey the
material. Reading the xorder catalog does not activate it.

The [definition](../../artifacts/context/project-guidance/definition.json)
declares the `codex` audience and `project` scope. Its
[payload](../../artifacts/context/project-guidance/payload/project-guidance.md)
maps to `AGENTS.md` in the selected project root. The
[PHP project profile](../profiles.md) selects it only for a target explicitly
described as a Codex project. It supplies guidance, not executable tooling.
The resolver also enforces this audience on the resource itself. A custom profile
or private overlay cannot select it for another harness, and a missing harness
fact must be supplied before resolving it.

Review the example before adoption. Inspect the project's existing `AGENTS.md`,
any `AGENTS.override.md`, and its documented instruction hierarchy. Preserve
existing project guidance; an unowned or locally edited file is a conflict,
rather than a reason to append or overwrite automatically. Owner instructions
and the consuming project's current policies determine what should be used.

Choose an accepted `available` catalog release for managed delivery and verify
its exact archive SHA before extraction. With a trusted source checkout
matching the release record, check the staged payload:

```sh
python3 scripts/xorder/verify-bundles.py context/project-guidance /path/to/staging
```

The staging root contains `project-guidance.md` directly. This check establishes
that the payload is present, identifies its sample status and owner authority,
and fits within Codex's documented default guidance budget. It does not execute
Codex or measure instruction following. For manual adoption into a project with
no existing guidance, review the staged text and copy it to `AGENTS.md`.

Codex reads project instructions when a run starts. Start a new session after
delivery and inspect its reported guidance sources if checking activation.
An `AGENTS.override.md` in the same directory takes precedence over `AGENTS.md`.
Do not remove that override automatically. Keep personal history, credentials
and machine assignments outside this public example.

Source: [Codex project instruction discovery](https://developers.openai.com/codex/guides/agents-md/).
