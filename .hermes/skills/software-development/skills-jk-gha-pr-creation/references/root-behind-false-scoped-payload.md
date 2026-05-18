# Root-behind false scoped payload in skills-jk cleanup

Pattern observed during repeated `main branch 업데이트하고, 로컬 변경사항 파악하여 PR 작성해줘` requests.

## Symptom

The user asks for a PR for scoped repo-managed files such as:

- `.hermes/config.yaml`
- `.hermes/memories/MEMORY.md`
- `.hermes/memories/USER.md`

`cmp` or `git diff HEAD..origin/main -- <paths>` reports differences, but `git status --short -- <paths>` shows no local modification.

## Cause

The root checkout is simply behind `origin/main`. The scoped files differ because the remote main branch has newer content, not because there is a local payload to review.

This often happens right after a follow-up PR has merged and the remote branch was deleted:

- `git fetch --prune` shows `origin/main` advanced and a previous PR branch deleted
- root `main` shows `[behind N]`
- stale PR worktrees still show historical diffs for the same paths

## Correct handling

1. Distinguish local dirt from remote advancement:
   ```bash
   git status --short -- .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md
   git diff --name-status HEAD..origin/main -- .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md
   ```
2. If `git status --short` is empty for the scoped files, do not create a PR that would revert `origin/main` back to the stale root contents.
3. Preserve only true local dirt from `git diff` / `git status` before pulling.
4. Fast-forward root `main` with `git pull --ff-only origin main` once tracked local dirt is preserved or restored.
5. Re-check the scoped files with direct equality:
   ```bash
   for p in .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md; do
     cmp -s "$p" <(git show origin/main:"$p") && echo "$p same" || echo "$p differs"
   done
   ```
6. If another real local skill/reference diff remains, PR only that surviving diff from a fresh latest-main worktree.

## Reporting rule

Say explicitly that the scoped config/memory files produced no PR payload because local root was behind and the latest remote main already contains the current version. Then report any separate surviving PR payload by its actual file list.
