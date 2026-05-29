# Repeated cleanup: old active skill residue after pack migration

Use this note during `skills-jk` local sweep / `main 업데이트` / `workspace 정리` work when root `main` is behind and local dirt remains under an old active `.hermes/skills/**` path that latest `origin/main` has already moved into an inactive `.hermes/skill-packs/**` pack.

## Durable pattern

1. Fetch/prune and inspect root status before trying to fast-forward main.
2. If a local dirty path no longer exists on `origin/main`, do not create a PR that resurrects the deleted active skill path.
3. Locate the canonical latest-main destination with `git ls-tree -r origin/main` or content search against `.hermes/skill-packs/**` and active pack entrypoints.
4. Port only the still-useful guidance/reference content into the canonical pack path.
5. Link the new reference from the canonical pack skill rather than re-adding a broad active skill.
6. Commit/push/create or update the appropriate PR from a fresh latest-main worktree.
7. Restore/remove the stale root old-path copy, then fast-forward root `main` and continue stale worktree cleanup.

## Pitfall

A behind root checkout can make deleted active skill files look like valid local changes. Treat `origin/main` as the source of truth for current skill layout before PR-ing `.hermes/skills/**` residue. If latest main moved the class to `.hermes/skill-packs/<pack>/...`, preserve the learning there and leave the old active path deleted.
