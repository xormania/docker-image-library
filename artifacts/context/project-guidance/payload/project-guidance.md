# Project guidance (example)

This is an xorder example for a Codex project. It is not a statement of xor's
personal philosophy or a source of authority over the project owner. Review and
adapt it before adopting it. Current owner instructions govern the task.

Read the project's README and contribution guidance to find its architecture,
runtime requirements, and documented verification commands. Inspect the relevant
source and lockfiles before changing a dependency or choosing a runtime.

Keep responsibilities separate and reuse existing project interfaces where they
fit. Introduce an abstraction when it removes a real repeated responsibility or
isolates a meaningful boundary. Keep the change focused on the requested result.

Verify the affected behavior with the project's documented checks. Test the
observable contract and relevant failure cases. Report what was checked, the
result, and any checks that could not run in the current environment.

Use the project's own instructions for branching, review, and publication.
Never derive credentials or private machine assignments from this sample.
