# Project EditorConfig

`configuration/editorconfig` provides one project-local `.editorconfig` as a
small starting point. It sets UTF-8, LF, final newlines and four-space defaults,
uses two spaces for JSON/YAML, keeps Markdown trailing whitespace, and keeps
Makefile recipe tabs. Review these choices against the consuming project's
conventions before selecting the resource.

The [definition](../../artifacts/configuration/editorconfig/definition.json)
maps [its payload](../../artifacts/configuration/editorconfig/payload/editorconfig)
to `.editorconfig` relative to the selected project root. Its `any` target means
the text format is portable; it does not mean every editor integration was
tested. Formatting takes effect only in an editor with EditorConfig support.

Use only an accepted `available` release in the [typed catalog](../../catalog-v2.json)
for managed installation. Verify its exact archive SHA before extracting it to
a staging directory. With a trusted source checkout matching its release record,
check the extracted file:

```sh
python3 scripts/xorder/verify-bundles.py configuration/editorconfig /path/to/staging
```

The staging root contains `editorconfig` directly. The check parses the settings
and checks the documented PHP, structured-file, Markdown and Makefile cases.
It verifies the configuration payload, rather than claiming it has reformatted
the project or tested the user's editor.

Inspect existing `.editorconfig` files first. Existing project files and local
edits are conflicts for managed installation. Keep them until the owner decides
how to reconcile the settings; do not force replacement or append another
complete configuration. For a manual installation into a project with no such
file, review the staged file and copy it as `.editorconfig`. Updates made after
that manual copy remain the project's responsibility.

EditorConfig searches parent directories and stops at `root = true`. Review this
boundary when the project belongs to a larger workspace. Nested project
configuration may override the root defaults. This bundle has its own revision
and can be updated independently of a runtime or context resource.

Source: [EditorConfig format and precedence](https://editorconfig.org/).
