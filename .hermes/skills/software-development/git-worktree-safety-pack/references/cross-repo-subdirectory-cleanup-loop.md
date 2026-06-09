# Cross-repo subdirectory workspace cleanup loop

Use when the user asks to clean a workspace containing multiple repository directories, e.g. `하위 디렉토리의 repo 를 순환하면서 workspace 정리해줘`.

## Scope

- Treat the current workspace directory's immediate child Git repositories as the default scope unless the user explicitly asks for recursive nested discovery.
- For each child repo, preserve the normal repo-local cleanup semantics: update the default branch, keep meaningful/open-PR worktrees, and remove only stale/merged/equivalent residue.
- Do not collapse multiple sibling checkouts blindly. First group by `git remote get-url origin` and remove a duplicate standalone clone only when it is clean, on the remote default branch, HEAD equals the remote default head, has no registered nested worktrees, and another canonical sibling remains.

## Practical loop

1. Enumerate immediate children that contain `.git`.
2. For each repo:
   - fetch/prune origin;
   - resolve the default branch from `refs/remotes/origin/HEAD`;
   - cleanly align root default branch to `origin/<default>` after preserving any dirty authored payload;
   - enumerate `git worktree list --porcelain` and inspect every linked worktree status before deletion.
3. For every retained worktree branch, run a targeted open-PR lookup by head branch. Preserve clean open-PR worktrees even when they look stale locally.
4. Prefer visible, bounded probes over one large black-box cleanup script. If a cross-repo script with fetch/`gh pr list` calls runs longer than the user's responsiveness threshold, stop it and switch to short per-repo or per-category scans; then re-scan live state because the interrupted job may have already fast-forwarded roots or deleted some stale worktrees.
5. Before deleting duplicate worktrees that point at the same commit under different branch names, check for dirty uncommitted payload. If one duplicate branch is tied to a clean docs/spec PR and another worktree at the same HEAD has dirty follow-up implementation files, do not remove the dirty duplicate as residue. Treat the clean/open-PR branch as the base, commit the dirty payload on its own branch, and open a stacked PR against the docs/spec branch before rerunning the final dirty sweep.
6. For PR-less clean worktrees, classify carefully:
   - protected long-lived branches such as `release` can remain if intentionally retained;
   - merged/equivalent/no-upstream residue can be removed after targeted PR lookup and dirty check;
   - meaningful PR-less diffs should be promoted to a PR/worktree before root cleanup.
7. After creating or amending a preservation PR, verify both the remote ref (`git ls-remote origin refs/heads/<branch>`) and GitHub PR metadata (`gh pr list/view --json headRefOid`). GitHub can briefly return stale `headRefOid`; retry a few short times before treating it as a failure.
8. Run a final all-repo verification sweep:
   - every root is on its default branch;
   - every root `git status --porcelain` is empty;
   - every root HEAD equals `origin/<default>`;
   - no duplicate-origin standalone clone remains;
   - every retained worktree is clean and either tied to an open PR or explicitly justified (for example protected `release`).
9. If a clean/no-op worktree reappears as dirty only because of untracked `tmp/` or extraction artifacts, inspect the files before removal. For generated document/image extraction residue with no repo references and no tracked diff, `git clean -fd -- <tmp-path>` first, then remove the no-op worktree/branch and rerun the final sweep.

## Final report shape

Keep the final report compact and operational:

- number of repositories scanned;
- root status invariant: default branch, clean, equals origin;
- duplicate-origin result;
- deleted stale worktrees/branches grouped by repo;
- preserved PRs with URL and branch/head OID when relevant;
- intentionally retained worktrees with reason;
- paths to any machine-readable logs produced during the sweep.

Do not report a workspace sweep as complete until the final verification sweep has no root issues and all retained worktrees are either clean open-PR worktrees or explicitly justified protected branches.
