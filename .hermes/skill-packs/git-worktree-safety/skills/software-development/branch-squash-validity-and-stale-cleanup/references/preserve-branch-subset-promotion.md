# Preserve branch subset promotion during stale cleanup

Use when a local-only `preserve/*` branch remains after repeated workspace cleanup and latest `origin/main` has already absorbed several earlier PRs.

## Pattern

- The preserve branch has no open PR.
- Its raw diff versus `origin/main` is broad.
- The raw diff mixes useful current notes with old deletion/revert hunks.
- A direct PR from the preserve branch would undo latest-main content.

## Rule

Do not publish the preserve branch directly. Use it as a source to classify and transplant only meaningful current payload.

1. Inspect path-level diff and group by topic.
2. Create fresh latest-main worktrees for meaningful subsets.
3. Copy or patch only durable additions.
4. Preserve user/memory preference updates additively if the preserve branch replaced a still-valid preference.
5. Drop stale deletion hunks and stale generated-bundle residue.
6. Verify each promoted branch remote SHA and PR URL.
7. Delete the local-only preserve branch after all meaningful payload is represented elsewhere.

Useful label:

- `stale preserve branch deleted after meaningful subset promotion`
