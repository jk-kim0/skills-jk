# Preserve branch cleanup after meaningful subset promotion

Use this reference when a local-only `preserve/*` branch remains after repeated workspace cleanup.

## Signal pattern

- `gh pr list --head preserve/<name> --state all` returns no PR.
- `git diff origin/main..preserve/<name>` is broad and contains both:
  - meaningful new notes or memory additions
  - stale deletions/reverts of files now present on latest `origin/main`
- The user asked to clean local branches/worktrees, not to keep old preservation snapshots forever.

## Handling rule

Treat the preserve branch as an adjudication source, not a publishable branch.

1. Inspect the branch diff by path and topic.
2. Create fresh latest-main branch(es) for meaningful subsets.
3. Copy or patch only current durable additions.
4. Add memory/user preference updates additively when the preserve branch replaced a still-valid existing preference.
5. Drop old deletion hunks and reverted generated files.
6. Push/PR every meaningful subset and verify remote heads.
7. Delete the stale local-only preserve branch after all useful payload is represented elsewhere.

## Useful commands

```bash
gh pr list --head preserve/<name> --state all --json number,state,mergedAt,url,title
git rev-list --left-right --count origin/main...preserve/<name>
git diff --stat --find-renames origin/main..preserve/<name> --
git diff --name-status --find-renames origin/main..preserve/<name> -- | sed -n '1,160p'
```

When deleting after promotion:

```bash
git branch -D preserve/<name>
git worktree prune
```

## Reporting label

Use a clear label such as:

- `stale preserve branch deleted after meaningful subset promotion`
