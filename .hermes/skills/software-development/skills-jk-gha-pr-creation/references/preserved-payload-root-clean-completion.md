# Preserved payload vs clean root completion

Use this when a `skills-jk` workspace sweep starts from a dirty root `main` checkout and the user asks to update `main`, summarize local changes, and preserve meaningful changes in PRs.

## Lesson

Copying root-local changes into a fresh latest-main worktree is a preservation mechanism, not necessarily the final workspace state. After the PR branch has been pushed and verified, decide whether the root checkout should remain dirty based on the user intent:

- If the user explicitly asked only to copy/clone changes and preserve the original dirty checkout, leave root dirt intact and report that clearly.
- If the request is a workspace cleanup / main update flow, or the user asks to update `main` and make PRs for meaningful local changes, treat a clean root `main` aligned with `origin/main` as the desired completion state once the payload is safely preserved.
- Before cleaning root, verify the PR branch remote ref matches local HEAD and the branch payload is based on latest `origin/main`.
- For root paths that are byte-identical to latest `origin/main`, restore/reset them rather than creating duplicate PRs.
- For root paths preserved in an open PR, restore those same root paths after remote verification so root `main` can fast-forward cleanly.
- Re-fetch after PRs merge during the same session; `origin/main` can advance while cleanup is in progress, requiring another root fast-forward and possibly a rebase of still-open follow-up PR branches.

## Reporting pattern

Report three facts separately:

1. `main` / `origin/main` alignment and final root cleanliness.
2. Which local changes collapsed because latest `origin/main` already contained them or because earlier PRs merged.
3. Which surviving changes were preserved in new or updated PRs, with branch, commit, and payload list.

Do not call workspace cleanup complete while root `main` still contains the same dirty files already preserved in a PR, unless the user explicitly asked to keep those originals dirty.
