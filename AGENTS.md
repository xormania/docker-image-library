# Working on this repository

Read [README.md](README.md), [the release contract](docs/versioning.md), and
[contributing](docs/contributing.md). No installed agent skill is required.

Image intent belongs in `images/*/definition.json`; measured facts belong in
verified `release-records/`. Generate `catalog.json`, the README availability
table, and `docs/images/` with `python3 scripts/library.py generate`.
Never add an unverified image to the available catalog or reassign an exact tag.

Use feature branches and PRs against master. Run `python3 scripts/library.py check`
and `python3 -m unittest discover -s tests`. Container behavior is checked by
`scripts/verify-image.sh`, also used by the public usage instructions.
