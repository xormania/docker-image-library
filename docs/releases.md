# Publication and recovery

Source PRs build and execute behavioral fixtures on Linux amd64. After a source
PR lands on master, `Publish verified images` follows this path:

1. Build each changed/unreleased line with locked base digests and version labels.
2. Exercise the public readiness recipe and collect actual inventory.
3. Push a separate source/revision-qualified candidate tag. Pull that same
   artifact by digest without credentials, and execute its readiness recipe.
4. Persist `record.json` and the inventory as assets on a draft namespaced
   GitHub Release before changing an exact tag.
5. Promote the candidate digest to the exact tag. Refuse any different existing
   digest, verify the public exact reference and publish the source Release.
6. Open a PR containing verified release records and generated catalog/docs.
   Partial successes may be cataloged independently; failed exact promotions
   are excluded by writeback.
7. After this PR lands, `Promote accepted aliases` fetches the latest master
   ledger and points compatible aliases to its newest available revisions.

The source tag identifies the build commit. The generated documentation commit
is later. The GitHub Release assets retain the definition and inventory needed
to understand the exact historical artifact. The root README describes accepted
available images. Image source changes and record-only writeback have distinct
workflow path filters, preventing a publication loop.

The release/alias workflows share a repository-wide concurrency group and do
not cancel in-progress promotion. Different line jobs within a release may run
in parallel. An older queued job reads the current accepted ledger before
advancing an alias; it cannot overwrite a newer accepted recommendation.

## First publication setup

The repository uses GitHub-hosted runners. Master has an active PR ruleset,
allows merge commits, and has automatic merge disabled as inspected on
8 October 2026. Automation stages protected-branch changes in PRs; it does not
bypass those controls or invent an automatic merge entitlement.

Required settings:

- Permit Actions and the pinned official actions used by these workflows.
- Permit the workflow token to create/write repository-associated GHCR packages
  and GitHub Releases. Source PR validation uses read-only repository permissions.
- Permit automation to create PRs. `LIBRARY_BOT_TOKEN` is an optional repository
  secret for a suitably scoped bot token, so bot-created PRs trigger normal CI.
  PRs created with GITHUB_TOKEN do not trigger other Actions workflows; run
  `Validate` manually or use the bot token. Never commit the token.
- After the first candidate push, set each GHCR package (`php-dev`,
  `php-browser`, `rust-dev`, `python-dev`) to **public** using its package settings.
  GHCR creates packages private by default and provides no container-visibility
  mutation in this workflow. Rerun the failed publication job; it will reuse the
  candidate, not rebuild. Browser packages are created after their PHP parent
  passes, so first publication can need a second visibility/setup pass.
- Merge generated catalog/input-refresh PRs using the permitted merge method.
  Fully unattended default-branch writeback needs an explicitly authorized
  merge mechanism consistent with the current ruleset; it is not configured
  merely by adding these workflows.

Actual package permissions and anonymous pulling are checked by publication,
not assumed because a repository is public. There are no stable published
references until that succeeds and the records are accepted.

## Retry and failure boundaries

GitHub, git and the registry do not form an atomic transaction.

| Failure point | Recovery |
| --- | --- |
| Build/test before candidate push | Fix the failure and retry; no stable recommendation changed |
| Candidate pushed, public pull blocked | Make package public/fix network, rerun; existing candidate is pulled and tested |
| Record persisted, exact promotion failed | Rerun; download durable record and promote the same digest |
| Exact/GitHub Release succeeded, docs PR failed | Rerun; use release asset and restage docs; old aliases remain |
| Docs merged, alias job failed | Rerun `Promote accepted aliases`; fetch current ledger and verify exact references |
| Exact tag exists with a different digest | Stop; workflow refuses overwrite; allocate a fresh revision or recover the intended record |
| Existing record cannot be fetched | Stop; do not interpret an API failure as an absent release |

The candidate tag includes full source SHA and revision. A different-input retry
of a persisted revision fails, requiring a new revision. An exact tag without
its durable record is ambiguous and requires recovery, not a silent rebuild.
No failed candidate advances the catalog or alias. GitHub Release publication
alone does not complete catalog writeback and alias promotion; workflow status
and the default-branch catalog show those separate steps.

Retain all exact released artifacts required by projects. Candidate cleanup is
separate: inspect package version tags and record digests, preserve any version
referenced by an exact tag or release record, and only remove abandoned,
unreferenced candidates after review. Do not apply generic registry retention
to released digest pins. Docker Hub mirroring is a later optional step and would
need its own anonymous-pull verification before entering the catalog.
