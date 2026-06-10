# Repeated cleanup after a merged preservation PR: avoid stale deletion hunks

Use this when a repo-local `main 업데이트` / `workspace 정리` sweep is run shortly after a previous dirty-root preservation PR was merged, and the root checkout is both dirty and behind `origin/main`.

## Pattern

A root checkout can contain valid new local skill/docs edits while its `main` commit is still older than `origin/main`. If a prior preservation PR was just merged, a broad `git diff origin/main --` from the stale root may show many apparent deletions for files that actually exist on latest main. Those deletion hunks are usually stale-baseline artifacts, not intentional local removals.

## Safe preservation sequence

1. Fetch first: `git fetch origin --prune`.
2. Record live state before cleanup:
   - `git status --short --branch`
   - `git rev-parse main origin/main`
   - `git diff --name-status origin/main --`
   - untracked file list
3. Back up the dirty root patch and untracked list outside the repo, for example under `/tmp/<repo>-preserve-<date>/`.
4. Do not apply the entire `git diff origin/main` patch onto a new branch when the root is behind. Instead, classify paths:
   - keep authored skill/docs/reference additions and modifications;
   - exclude runtime residue such as `.hermes/lsp/`, `node_modules`, caches, logs, or generated local state;
   - exclude deletion hunks for files that exist on `origin/main` unless the user explicitly requested those deletions and they still make sense against latest main.
   - if a same-session feature/preservation PR has just merged, compare each dirty skill/reference path against latest `origin/main` before preserving it. Wording-only or same-concept edits already present on latest main should be discarded, while genuinely missing repo-local pointers or new `references/*.md` files should be preserved on a fresh branch.
5. Create a fresh worktree from latest `origin/main` and copy only the selected authored payload into it.
6. Validate before committing:
   - `git diff --check`
   - conflict-marker scan for `<<<<<<<`, `=======`, `>>>>>>>`
   - inspect staged file list and stat for unintended mass deletions.
7. Commit, push, create/update the PR through the repository's standard PR path, then verify local head, remote head, and PR head SHA match.
8. Only after the PR branch is verified, reset/clean the root checkout to latest `origin/main`, remove runtime residue, and delete merged/gone prior preservation worktrees or branches.
9. Finish with a repeated sweep: root status, remaining worktrees, targeted PR lookup for retained branches, and unregistered `.worktrees/` child check.

## Pitfalls

- Do not treat apparent mass deletions from `git diff origin/main` as real intent when root `main` is stale.
- Do not delete root untracked authored files until the preservation PR head is verified.
- Do not reuse or force-push a branch from a merged preservation PR; create a fresh branch from latest main for the new preservation payload.
- Do not include local runtime directories such as `.hermes/lsp/` in docs/skill preservation PRs.

## Reporting

The final report should explicitly distinguish:

- root `main` SHA and `origin/main` SHA;
- root cleanliness;
- the new preservation PR URL, branch, author, and head SHA verification;
- stale deletion/runtime residue that was excluded;
- merged/gone worktrees and local branches removed;
- intentionally retained open-PR worktrees.