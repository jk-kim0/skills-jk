# Invalid OpenSpec change to base spec promotion

Use this pattern when an active `openspec/changes/<change-id>/` is no longer a valid OpenSpec change but its requirements already belong in durable `openspec/specs/`.

## Signals

- `openspec validate <change-id>` fails with `No delta sections found` because `openspec/changes/<change-id>/specs/**/spec.md` uses base-spec `## Requirements` instead of delta headers such as `## ADDED Requirements`.
- The same requirements are already copied into a base spec, or the change is effectively complete and should stop appearing in `openspec list` as an active invalid change.
- The topic is a durable implementation contract, not a one-off change checklist.

## Recommended workflow

1. Work from latest `origin/main` in a repo-local `.worktrees/<topic>` worktree.
2. Identify whether the topic deserves its own base spec.
   - If the contract crosses route namespace, schema constraints, service validation, helper generation, and tests, prefer a class-level `contract-*` base spec over burying it inside a broad domain schema spec.
3. Create `openspec/specs/<contract-topic>/spec.md` with normal base-spec structure:
   - `# <spec-id>`
   - `## Purpose`
   - `## References`
   - `## Requirements`
   - `### Requirement: ...`
   - `#### Scenario: ...`
4. Remove duplicated detailed requirements from the broader base spec and leave either:
   - a short delegation Requirement pointing to the new spec, or
   - only a Reference if no executable scenario is needed.
5. Update `openspec/specs/README.md` inventory so future agents discover the new base spec.
6. Preserve the old active change under `openspec/archive/<yyyymmdd>-<change-id>/` instead of silently deleting it.
   - Add a short archive `README.md` explaining the new canonical spec path and why the active change was removed from validation.
7. Remove the active `openspec/changes/<change-id>/` so `openspec list` no longer reports the invalid change.
8. Verify targeted correctness:
   - `openspec validate <new-spec-id>`
   - `openspec validate <broader-base-spec-id>`
   - `openspec list --specs`
   - `git diff --check`
9. Run `openspec validate --all`, but distinguish this PR's fixed target from unrelated existing OpenSpec debt.
   - If `--all` still fails on unrelated specs/changes, report that clearly in the PR body instead of expanding the PR scope.

## Example shape

For a stale `changes/slug-uniqueness-contract` whose requirements already live inside `contract-mvp-domain-schema`:

- Create `openspec/specs/contract-slug-uniqueness/spec.md`.
- Move route namespace, reserved route collision, Team-scoped slug, parent-scoped artifact slug, and default Team slug fallback contracts there.
- Replace the detailed slug section in `contract-mvp-domain-schema` with a delegation Requirement.
- Move the old change to `openspec/archive/<date>-slug-uniqueness-contract/`.
- Confirm `openspec validate contract-slug-uniqueness` and `openspec validate contract-mvp-domain-schema` pass.

## Pitfalls

- Do not keep a completed/invalid change active just because it contains historical context; archive it.
- Do not convert an invalid change spec by merely renaming `## Requirements` to `## ADDED Requirements` if the actual intent is now a durable base contract.
- Do not duplicate the same detailed requirements in both a broad base spec and a new focused base spec.
- Do not claim `openspec validate --all` is fixed when unrelated legacy OpenSpec failures remain; report target validation separately from all-repo validation.
