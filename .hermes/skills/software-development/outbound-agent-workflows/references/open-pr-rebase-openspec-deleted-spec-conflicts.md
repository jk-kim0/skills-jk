# Open PR rebase conflicts after OpenSpec spec deletion

Use this reference when rebasing Outbound Agent open PRs onto latest `main` and a branch conflicts because latest `main` deleted or renamed an OpenSpec spec that the PR still modifies.

## Pattern observed

A common conflict shape is `modify/delete` during `git rebase origin/main`:

- latest `main` deleted a broad legacy spec such as `openspec/specs/contract-mvp-domain-schema/spec.md` after splitting its contract into narrower `entity-*`, `contract-*`, `integration-*`, or `ui-*` specs;
- an older PR modifies that deleted file for a narrow purpose, such as restoring strict validation markers;
- blindly accepting the PR side would resurrect the deleted broad source of truth and undo the main-branch refactor.

## Resolution rule

1. Treat latest `main` as the canonical structural baseline.
2. Do not resurrect a deleted broad OpenSpec file unless the PR's explicit purpose is to restore that exact canonical spec.
3. Preserve the PR's still-valid payload in the surviving canonical spec/change files.
   - For strict validation cleanup PRs, keep marker fixes in existing `openspec/changes/**/specs/**/spec.md` and active `openspec/specs/**/spec.md` files.
   - Remove the deleted path with `git rm <deleted-spec-path>` when the only conflict is a stale modification to a deleted spec.
4. Continue the rebase with `GIT_EDITOR=true git rebase --continue`.
5. Verify with `git diff --check`, conflict-marker search, and final merge-base equality against latest `origin/main`.

## Example

If `openspec/specs/contract-mvp-domain-schema/spec.md` is deleted on `main` and a rebase of `docs/openspec-strict-validation-cleanup` reports `DU openspec/specs/contract-mvp-domain-schema/spec.md`, resolve by keeping the deletion:

```bash
git rm openspec/specs/contract-mvp-domain-schema/spec.md
git diff --check
! grep -R '<<<<<<<\|=======\|>>>>>>>' -n openspec docs front || true
GIT_EDITOR=true git rebase --continue
```

Then confirm the strict validation cleanup commit still includes its intended additions on the remaining OpenSpec change/spec files before force-pushing with lease.
