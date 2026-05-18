---
name: safe-git-worktree-branch-cleanup
description: Safely update local main and clean stale local git branches/worktrees without deleting dirty or still-attached work.
version: 1.0.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, worktree, branch, cleanup, maintenance, safety]
---

# Safe git worktree/branch cleanup

Use when the user asks to:
- update `main`
- clean stale local branches
- clean stale worktrees
- prune local git state safely
- `workspace 정리` across one or more specific repos

This workflow is for repositories that may have many old worktrees, detached review trees, and branches whose upstream refs were pruned.

- `branch-squash-validity-and-stale-cleanup` — use when the user explicitly wants each local branch judged by a synthetic squash of current local state versus latest `origin/main`, with a disposable rebase-onto-latest-main test before deciding whether to preserve or delete it.

References:
- `references/promote-portable-backup-patch.md` — detailed pattern for repeated cleanup where an old backup branch has a huge stale raw diff but a small portable synthetic-squash payload that should be promoted to a fresh branch/PR before deleting the old worktree.

## Goals

1. Update the local default branch (usually `main`) to match the latest remote HEAD when the root worktree is clean
2. Remove only clearly safe stale worktrees
3. Remove only clearly safe stale local branches
4. Preserve dirty worktrees, active work, and unmerged branches

User-specific requirement:
- treat default-branch update as part of workspace cleanup by default
- for `main`-based repos, align local `main` with the latest `origin/main` via fetch + fast-forward when safe
- if the root worktree has tracked changes or the update is not a clean fast-forward, preserve and report instead of forcing
- untracked-only root dirt does not automatically block `git pull --ff-only`; first check whether the incoming remote diff touches those same paths, and if not, fast-forward is usually still safe

## Scope interpretation for this user

When the user says `workspace 정리`, interpret it from the live cwd first rather than from the generic English word `workspace`.

Execution style for this user:
- start with a very short status line and rough time estimate, then act immediately
- do not pause with a proposal-only response once the repo-local cleanup intent is clear
- after the cleanup actions, do one last live snapshot pass before reporting completion

Practical rule:
- if `pwd` is already inside a git repository, default to **repo-local cleanup** for that current repository
- in that case, do not ask whether they meant the whole `~/workspace` unless they explicitly say all repos / entire workspace
- repo-local cleanup means:
  1. inspect the current repo root and worktree graph
  2. switch the root checkout back to the default branch when safe
  3. fast-forward the root default branch to the latest `origin/<default>` when safe
  4. delete stale local worktrees/branches for that repo only
  5. keep going until the repo is as clean as safely possible, including obvious root-local residue

Escalate to cross-repository cleanup only when the user clearly indicates the whole workspace root, multiple repos, or sibling repositories.

## Safety rules

- Never delete the current branch.
- Never delete a dirty worktree automatically.
- Never delete a branch still attached to any worktree.
- Never delete a branch that is not merged into `origin/main` unless the user explicitly asks for aggressive cleanup.
- If the starting directory is not a git repo, first identify the target repo instead of guessing silently.
- If multiple repos exist under a workspace, ask which repo to target when possible.
- If the user does not answer and you must proceed, state the default repo choice explicitly.

## Procedure

### 1. Confirm repo context

Run:

```bash
pwd
git rev-parse --show-toplevel
```

If not a repo, discover likely repositories or worktrees under the workspace using repository-aware search tools before proceeding.

### 2. Inspect current repo state

Run:

```bash
git branch --show-current
git status --short --branch
git remote -v
git worktree list --porcelain
git for-each-ref --format='%(refname:short)|%(upstream:short)|%(committerdate:iso8601)|%(subject)' refs/heads
```

This reveals:
- current branch
- dirty root repo state
- all linked worktrees
- branch/upstream relationships

### 3. Refresh remote refs

Run:

```bash
git fetch origin --prune
```

Then check:

```bash
git rev-parse main
git rev-parse origin/main
git branch --merged origin/main
```

Also identify branches whose upstream ref was removed:

```bash
for b in $(git for-each-ref --format='%(refname:short)' refs/heads); do
  u=$(git for-each-ref --format='%(upstream:short)' refs/heads/$b)
  if [ -n "$u" ] && ! git show-ref --verify --quiet refs/remotes/$u; then
    echo "$b|$u"
  fi
done
```

## 4. Classify worktrees

For each worktree, collect:
- path
- branch or detached state
- whether it is dirty
- a short status preview

Only treat a worktree as immediately removable when all are true:
- detached HEAD
- clean working tree
- not the primary active worktree

Do not remove:
- any dirty worktree
- any branch-attached worktree unless the branch is explicitly being retired and the tree is clean

## 5. Cross-check open PR reality before deciding what to keep

In repositories that use many temporary worktrees for PR follow-up, a branch-attached worktree is often still stale even though it is not detached.

Before preserving branch-backed worktrees, query actual open PRs and compare them to local branch/worktree state.

If GitHub CLI is available:

```bash
gh pr list --state open --json number,title,headRefName,isDraft,url
```

Then classify each branch-backed worktree using this stricter order:

1. keep the current repo worktree
2. keep any truly dirty worktree with real user changes
3. keep a worktree whose branch matches an open PR head branch
4. remove a clean worktree whose branch has no open PR and is clearly old/stale

Strong stale signals for branch-backed worktrees:
- no open PR for the branch
- upstream ref is gone after `git fetch --prune`
- `gh pr list --state all --head <branch>` shows the PR was already merged/closed
- the branch tip is already equivalent to `origin/main`
- the worktree only exists for an old review/rebase/squash/follow-up context

Counter-signal that should usually preserve a branch-backed worktree even with no PR:
- the worktree has real tracked modifications or meaningful untracked source files
- the branch appears to be an active local exploratory/refactor branch not yet published
- the local branch tracks a differently named upstream branch, indicating temporary local branch reshaping rather than stale residue

But do not over-preserve branch-backed worktrees just because they are not perfectly clean. Some branch worktrees are effectively stale except for disposable helper files. Check for repo-local temp artifacts such as:
- `.tmp-issue-*.md`
- `.tmp-pr-body*.md`
- other one-off scratch markdown files clearly unrelated to source changes

If those temp files are the only dirt in an otherwise stale merged/non-open-PR worktree, treat the worktree as effectively clean stale residue and remove it after confirming no tracked source changes remain.

Additional practical check for issue/PR body scratch files:
- repositories often accumulate untracked markdown files with names like `ISSUE_*.md`, `PR_BODY*.md`, or similar
- do not preserve these automatically just because they are human-readable documents
- compare them against the actual GitHub issue/PR bodies when you can, for example with `gh issue view <n> --json body` or `gh pr view <n> --json body`
- if the local file is effectively just a copy of an already-posted GitHub issue body or PR description, classify it as disposable stale residue rather than meaningful unpublished local work
- only preserve it when it contains materially new draft content not already represented on GitHub

Special case: open PRs can still have removable helper worktrees.
- In some repos, there are detached helper worktrees named like `pr157-mainrewrite`, `pr158-mainrewrite`, `pr157-rebase`, etc.
- Do not preserve these automatically just because the corresponding PR is open.
- If such a worktree is detached, clean, and its `HEAD` exactly matches the open PR's remote head commit, it is just a redundant local clone of the PR state and is safe to remove.
- Also, if multiple detached helper worktrees for the same PR are clean and all point to the same non-remote local commit, they are still usually removable as redundant local clones, as long as the meaningful PR state is preserved elsewhere (for example the draft/open PR itself remains on GitHub, and optionally a local branch remains for that fallback commit).
- Keep the worktree if it contains conflicts, tracked modifications, or untracked project files; those indicate real local intermediate state rather than a disposable helper clone.

Additional practical stale signals for branch-backed worktrees:
- the branch's PR is already `MERGED` and the upstream ref is `[gone]`
- the worktree is clean and exists only as leftover local residue after the PR merged
- the only remaining dirt is a disposable helper file such as `.tmp-pr-body.md`

In that case, it is usually safe to:
1. remove the disposable helper file
2. remove the worktree
3. delete the local branch afterward

Important practical lessons:
- Do not assume every branch-backed worktree should be preserved.
- Do not assume every worktree related to an open PR should be preserved either; clean detached helper clones can still be stale.
- But also do not assume "no open PR" means removable; a dirty branch-backed worktree may be active unpublished work.
- In PR-heavy repos, the real source of truth is the combination of open PR head branches plus actual local worktree dirtiness, not merely whether a branch is attached to a worktree.

## 6. Classify branches

For each local branch, determine:
- merged into `origin/main` or not
- attached to a worktree or not
- protected/current branch or not
- whether upstream still exists
- ahead count vs `origin/main`
- whether it corresponds to an open PR head branch
- whether any PR for that branch is already merged/closed

A local branch is safe to delete only when all are true:
- not current branch
- not `main`
- not needed by any open PR
- not attached to any worktree that must be kept
- either merged into `origin/main`, or confirmed as stale residue from an already merged/closed PR that no longer needs local preservation

Notes:
- Upstream being gone is not enough to delete by itself.
- A branch may have a stale or mismatched upstream; merge status, PR state, and worktree attachment matter more.
- `git cherry origin/main <branch>` is useful when a squash/rebase merge means the branch is not a direct ancestor of `origin/main` even though its PR is already merged.

## 7. Dirty-worktree false positives to check before preserving

Some worktrees look dirty only because of transient helper files created during agent workflows.

## 7e. A branch can be stale while its current dirty worktree changes are still meaningful

Important practical case from repo-local workspace cleanup:
- a branch/worktree may no longer be attached to any open PR
- the branch history may be stale relative to latest `origin/main`
- but the worktree can still contain meaningful uncommitted local edits that should not be deleted blindly

Typical signal pattern:
- PR for the branch is `CLOSED` or `MERGED`, or no open PR exists
- `git rev-list --left-right --count origin/main...<branch>` shows the branch is far from latest main
- a rebase of the branch tip onto latest `origin/main` quickly produces broad structural conflicts
- yet `git status --short` inside the worktree shows a small focused set of dirty files
- `git diff --stat` for those dirty files shows coherent implementation work rather than conflict junk or temp-file residue

Recommended decision flow for this case:
1. inspect the worktree dirt directly:
   ```bash
   git -C <worktree> status --short --branch
   git -C <worktree> diff --stat
   git -C <worktree> diff -- <paths...>
   ```
2. compare those same dirty files against latest main, not just against branch history:
   ```bash
   git -C <worktree> diff --stat origin/main -- <paths...>
   ```
3. if needed, simulate `git rebase origin/main` in a disposable helper worktree to judge whether the branch history itself is salvageable or just stale
4. separate the verdict into two parts:
   - branch history stale vs not stale
   - current dirty local edits meaningful vs disposable

Practical interpretation:
- if the branch history is stale but the current dirty edits are narrow, coherent, and purposeful, preserve the worktree even if you intend to retire the branch history later
- in that situation, the best follow-up is often:
  - discard or retire the stale branch history
  - recreate a fresh latest-main branch/worktree
  - transplant only the meaningful current dirty patch onto the fresh branch
- do not classify the whole worktree as stale just because the branch/PR lineage is stale
- stronger repo-cleanup rule from later usage: when the user explicitly wants branch validity judged by a squash-style comparison, build the synthetic squash from the CURRENT worktree state (tracked + untracked local changes) rather than from the committed branch tip alone
- this matters because a branch may look huge or stale versus latest main, while the live root/main or attached worktree only contains a very small meaningful local patch (for example a repo-local skill edit)
- conversely, a previously clean detached helper at an open-PR head can become a dirty follow-up worktree later in the same session; once it has real local edits, stop treating it as a removable helper clone and preserve it like any other dirty detached worktree

Additional practical case: branch head can be effectively stale or even net-empty, while the worktree still holds meaningful unpublished implementation

Typical signal pattern:
- the branch is not connected to any open PR
- the branch may even track `origin/main` directly or have `git rev-list origin/main...<branch>` close to `0 0`, `behind 1`, or another misleadingly small value
- the branch commit itself may be an old main-equivalent checkpoint or other non-meaningful base
- yet `git status --short` in the attached worktree shows real tracked edits plus meaningful untracked source/test files
- those untracked files are not temp helpers like `.tmp-issue-*.md`, but actual implementation files under `src/` or `tests/`

Example summary language:
- `stale branch pointer + meaningful local worktree patch`

Handling rule:
- judge the branch validity and the live worktree patch separately
- it is acceptable to delete the stale branch later, but only after preserving or transplanting the real worktree patch
- do not delete such a worktree automatically just because the branch itself looks equivalent to old main or not meaningfully ahead

Additional practical case: branch head can be effectively stale or even net-empty, while the worktree still holds meaningful unpublished implementation

Typical signal pattern:
- the branch is not connected to any open PR
- the branch may even track `origin/main` directly or have `git rev-list origin/main...<branch>` close to `0 0`, `behind 1`, or another misleadingly small value
- the branch commit itself may be an old main-equivalent checkpoint or other non-meaningful base
- yet `git status --short` in the attached worktree shows real tracked edits plus meaningful untracked source/test files
- those untracked files are not temp helpers like `.tmp-issue-*.md`, but actual implementation files under `src/` or `tests/`

Example summary language:
- `stale branch pointer + meaningful local worktree patch`

Handling rule:
- judge the branch validity and the live worktree patch separately
- it is acceptable to delete the stale branch later, but only after preserving or transplanting the real worktree patch
- do not delete such a worktree automatically just because the branch itself looks equivalent to old main or not meaningfully ahead

User-specific validation heuristic for repo-local cleanup:
- branches or worktrees not connected to any open PR should be treated as stale candidates by default, not preserved by default just because they are branch-backed
- however, validate any remaining local work against the latest `main`/`origin/main` tree before deleting
- when a branch has multiple commits, judge meaningfulness by the net effect versus latest main rather than by raw commit count; conceptually treat it like a squashed diff against latest main
- when a branch is behind latest main, a disposable rebase onto `origin/main` is a fast way to tell whether the branch history itself is stale; broad immediate conflicts are evidence that the branch lineage is stale even if a small current dirty patch is still worth preserving

Useful summary language:
- `stale branch history + meaningful local dirty work`
- this is distinct from both `fully stale residue` and `actively healthy branch`

Check for obviously disposable artifacts such as:
- `.tmp-pr-body.md`
- temporary comment/body markdown files
- untracked agent runtime directories like `.hermes/` when they are clearly local tool state rather than repo source
- other one-off helper files clearly unrelated to source changes

Practical rule:
- if the only dirt is disposable untracked helper state, remove it or classify it separately and re-check `git status --porcelain`
- common disposable residue in workspace-cleanup passes includes editor/runtime outputs such as `.idea/`, `.codegraph/`, `frontend/tests/test-results/`, and similar generated local diagnostics directories

### Stale `.git/index.lock` after timed-out commit

If a previous `git commit` or other git command timed out, Git may leave a stale `.git/index.lock` that blocks all subsequent git operations in the repo.

Symptom:
```bash
fatal: Unable to create '/path/.git/index.lock': File exists.
Another git process seems to be running...
```

Fix:
1. check if a real git process is still running
2. if none is running, remove the lock file: `rm -f /path/.git/index.lock`
3. retry the blocked command

Do not skip this step and do not use `--force` workarounds just because the lock error appeared once.

If the worktree still has dirt after lock cleanup:
- if those are the only remaining changes, treat the repo/worktree as effectively clean for stale-classification purposes, or delete just those local residue paths when the user asked for cleanup
- if the remaining dirt is real project files (for example tracked deletions like `D postcss.config.mjs`), preserve the worktree

Important provenance check before deleting untracked files:
- do not treat every untracked file as disposable just because it appeared during the current session
- especially under checked-in skill/doc trees such as `.hermes/skills/**`, `.agents/skills/**`, `docs/**`, or `references/**`, an untracked file may be meaningful local authored content rather than runtime junk
- before deleting an untracked file, classify it with evidence:
  - obvious lock/cache/usage artifact (for example `.lock`, machine-local usage DB, cache file)
  - clearly generated diagnostics/build output
  - or potentially user-authored content
- safe rule:
  - `rm` obvious runtime artifacts like lockfiles/caches only when their generated nature is clear
  - do **not** delete prose/reference markdown or other content-like untracked files inside skill/doc trees without confirming provenance first or asking the user
- if a tool interaction such as skill lookup/view seems to have created or modified repo-local files, prefer restoring tracked files only and report the remaining untracked files explicitly instead of silently deleting them all
- useful checks:
  ```bash
  git ls-files --error-unmatch <path> >/dev/null 2>&1 && echo tracked || echo untracked
  file <path>
  ls -l <path>
  ```
- reporting rule: when cleanup restored tracked files but left untracked content-like files alone, say that directly instead of implying all dirt was safely disposable

Important generated-artifact pitfall:
- do not delete a path just because its name looks disposable, such as `log/`, `logs/`, `manifest.json`, `*.pub`, or similar build/output-looking names
- first verify whether the path is actually untracked local residue versus tracked repository content:
  - `git status --short -- <path>`
  - if needed, `git ls-files --error-unmatch <path>`
- some repos intentionally version fixture-like logs or manifest outputs, so deleting them can create tracked deletions instead of cleanup
- safe rule:
  - if the path is untracked and clearly machine-local/generated, it is a cleanup candidate
  - if the path is tracked, do not classify it as junk; preserve it unless the user explicitly wants it removed
  - if you accidentally delete a tracked path while cleaning, immediately restore it with `git restore --worktree -- <path>` and continue from the corrected state

Be especially careful with `.hermes/`-style directories:
- they are often safe to ignore for stale classification, but confirm they are untracked local runtime artifacts before deleting
- if you are not confident they are disposable, preserve the worktree and report it
- if `.hermes/` is the only remaining dirt and the associated remote branch/PR is already merged, treat the worktree as stale and remove it with `git worktree remove --force ...` if needed
- in repo-local Hermes setups, runtime files can be recreated by the very commands used for verification or PR inspection; for example `.hermes/kanban.db` may reappear after earlier cleanup
- SQLite sidecar files can also appear after deleting the main DB, especially `.hermes/kanban.db-shm` and `.hermes/kanban.db-wal`
- therefore, after any final `gh`, skill, or Hermes-related verification command, run one last targeted cleanup of clearly runtime-only files such as `.hermes/kanban.db`, `.hermes/kanban.db-shm`, and `.hermes/kanban.db-wal`, then re-run `git status --short --branch` before declaring the root checkout clean

Do not delete dirty worktrees automatically if the remaining changes are real project files.

## 7a. Detached worktrees may need verification beyond `git status`

A detached worktree can look clean in a simple `git status --short --branch` snapshot, yet `git worktree remove <path>` may still refuse with:

```bash
contains modified or untracked files, use --force to delete it
```

When this happens, do not immediately force-remove blindly. First inspect inside the worktree:

```bash
git -C <path> status --short --branch
git -C <path> diff --stat || true
git -C <path> ls-files --others --exclude-standard || true
```

Interpretation:
- if `diff --stat` is empty and `ls-files --others` is empty, the refusal is just conservative Git behavior and `git worktree remove --force <path>` is acceptable
- if tracked diffs or untracked files exist, preserve the worktree unless those files are clearly disposable temp artifacts

This case showed up with detached PR follow-up worktrees that were effectively clean but still required `--force` to remove.

## 7b. Root-worktree dirty files may actually be residue from another kept worktree

In PR-heavy repos, the primary/root worktree on `main` can accumulate tracked-file edits that are not true `main` work. They may be accidental spillover from an open-PR worktree or another local worktree.

Before deciding that root tracked-file changes must be preserved, compare them against relevant kept worktrees:

```bash
git diff --name-only
```

For each dirty tracked file, compare the root file against the corresponding file in likely source worktrees, especially open-PR worktrees:

```bash
git diff --no-index -- path/in/root path/in/other/worktree || true
```

Interpretation:
- if files are identical, the root change is very likely residue copied from that worktree
- if the diff is very small and clearly the same direction of change, treat it as likely residue/intermediate state and inspect before preserving
- if the file differs materially from every kept worktree, treat it as genuine root-local work and preserve it

This check is especially important before restoring dirty tracked files in `main` so that `main` can be fast-forwarded to `origin/main` safely.

### Additional practical case: root dirt can come from repo-local skill/doc residue rather than intended code work

In repositories that check in agent skills or guidance under paths like `.agents/skills/**` or `docs/**`, the root `main` worktree can become dirty because of local exploratory edits to a skill or guidance file while you were debugging or documenting a different task.

Important split:
- some root skill/doc dirt is disposable residue and should be restored so `main` can fast-forward cleanly
- other root skill/doc dirt is meaningful and should be preserved, but not by leaving root `main` dirty indefinitely

Safe handling:
1. inspect the root diff directly:

```bash
git diff -- .agents/skills/... docs/...
```

2. compare that file against likely source worktrees if relevant
3. do not treat a root-local skill/doc/reference edit as disposable merely because it is outside an open PR; preserve it first unless you can prove it is a machine-generated artifact or an exact duplicate of a kept branch/worktree:

```bash
git diff -- <path>
git ls-files --error-unmatch <path> >/dev/null 2>&1 && echo tracked || echo untracked
```

Practical rule:
- do not silently restore or delete repo-local skill/doc/reference content just to make `main` fast-forward
- capture the full dirty path set first, preserve it onto a fresh latest-`origin/main` worktree/branch, and only then decide whether some paths are duplicate residue

Important follow-up case from corp-web-japan cleanup:
- sometimes the root `main` worktree ends the cleanup with exactly one meaningful repo-local skill/doc edit left (for example a checked-in `.agents/skills/**/SKILL.md` improvement) after all stale worktrees/branches were removed
- in that situation, do **not** leave `main` dirty indefinitely if the user actually wants that edit preserved
- preferred handling when the user wants that change turned into reviewable repo work:
  1. verify the edit is intentionally different from the active kept PR worktrees rather than just copied residue
  2. create a fresh worktree/branch from latest `origin/main`
  3. copy only the intended skill/doc diff into that fresh branch
  4. commit, push, and open a narrow docs/skill PR
  5. then restore the root `main` worktree and fast-forward it to `origin/main`
- lighter-weight variant when the user only asked to refresh local `main` and not to open a PR yet:
  1. create a fresh backup worktree/branch from latest `origin/main`
  2. copy the full dirty root file set into that backup worktree before classifying anything away
     - include tracked and intentional untracked files that the user may want preserved
     - a practical collection pattern is:
       - `git diff --name-only`
       - `git ls-files --others --exclude-standard`
  3. commit them locally on a clearly named backup branch such as `backup/...`
  4. compare the preserved copy against latest `origin/main` and any existing follow-up branch/worktree before restoring anything from root `main`
  5. if the root checkout is now clean, fast-forward it with `git pull --ff-only origin main`
  6. report both the backup branch name and backup worktree path to the user
- practical root-main-update pattern from repeated `skills-jk` use:
  - when the user simply says `main branch 업데이트해줘` while root `main` has meaningful local changes, do not block on the dirty root forever and do not force-reset it
  - before pulling, compare the current dirty tracked paths against the incoming `origin/main` diff paths since overlap means a direct fast-forward can fail or overwrite the user's intent
  - if there is overlap, preserve the full local dirty set first; if an earlier cleanup already created a matching backup worktree/branch for the same root-local line, prefer appending the new files there instead of creating yet another backup branch
- after copying the current tracked/untracked files into that backup worktree, commit the preservation commit there, verify which paths are truly duplicate/absorbed versus still unique, and only then restore the confirmed-duplicate root files before `git pull --ff-only origin main`
- important verification step: after creating the backup worktree from latest `origin/main` and copying the root files over, immediately run `git -C <backup-worktree> status --short --branch` and `git -C <backup-worktree> diff --stat`
  - some root-dirty files may already be absorbed by latest `origin/main`, but do not treat them as discardable until you have compared the preserved copy path-by-path against current main and any PR branch carrying related work
  - keep only the residual meaningful diff instead of assuming every copied file still represents unpublished work
  - practical example: root `next.config.ts` / `tsconfig.next.json` dirt can vanish after the backup worktree is based on newer `origin/main`, leaving only a smaller remaining route/test patch to preserve
- additional stale-file pitfall from later `skills-jk` use:
  - a root-local edit can be genuinely small on an old local `main`, yet become a huge reverse diff if you preserve it by overwriting the whole tracked file inside a fresh backup worktree from latest `origin/main`
  - this happens when latest `origin/main` has heavily evolved the same file, while the old root checkout still contains a stale snapshot plus a small local tweak
  - in that situation, a clean backup commit and even a clean disposable rebase onto latest main do **not** prove the preserved patch is PR-valid; you may have created a branch that mostly rolls back upstream additions
  - therefore split the goals:
    1. `backup-preserved` — raw stale file snapshot safely copied into a backup branch/worktree so nothing is lost
    2. `pr-valid` — minimal intended delta manually re-extracted onto the latest file content
  - if `git diff --stat origin/main...<backup-branch>` shows an unexpectedly huge deletion-heavy diff for a supposedly small local tweak, classify the branch as backup-only first, not as ready for PR
  - useful summary label:
    - `backup preserved, but stale whole-file overwrite not PR-valid`
- this leaves root `main` actually updated while still preserving the user's local work in an inspectable branch/worktree
- prefer this backup-worktree variant over `git stash`

Useful summary labels:
- `root-local skill/doc work preserved before any cleanup classification`
- `latest-main backup worktree created before restoring root`

Additional practical case: when there are no open PRs at all, the desired cleanup end-state is usually much smaller

Signal pattern:
- `gh pr list --state open` returns `[]`
- most linked worktrees are clean and branch tips now show upstream `[gone]` after `git fetch --prune`
- one or more dirty worktrees may still exist with real unpublished local edits
- root `main` is clean or can be made clean safely

Recommended handling:
1. treat every non-root clean worktree as a stale candidate by default
2. remove all clean detached helpers and all clean branch-backed worktrees that are not explicit preservation lines
3. delete the corresponding stale local branches after their worktrees are gone
4. keep only:
   - root default-branch worktree
   - any dirty worktree with meaningful local edits
   - explicit preservation branches such as `preserve/*`
5. fast-forward root `main` to `origin/main`

Practical interpretation:
- when open PR count is zero, there is usually no value in leaving dozens of clean historical worktrees or merged local branches around
- a good final state is often `root main + only genuinely dirty worktree(s) + explicit preserve branch(es)`
- report this outcome explicitly so the user knows the workspace was reduced to the minimum safe set rather than merely lightly pruned

Additional practical case: when there are no open PRs at all, the desired cleanup end-state is usually much smaller

Signal pattern:
- `gh pr list --state open` returns `[]`
- most linked worktrees are clean and branch tips now show upstream `[gone]` after `git fetch --prune`
- one or more dirty worktrees may still exist with real unpublished local edits
- root `main` is clean or can be made clean safely

Recommended handling:
1. treat every non-root clean worktree as a stale candidate by default
2. remove all clean detached helpers and all clean branch-backed worktrees that are not explicit preservation lines
3. delete the corresponding stale local branches after their worktrees are gone
4. keep only:
   - root default-branch worktree
   - any dirty worktree with meaningful local edits
   - explicit preservation branches such as `preserve/*`
5. fast-forward root `main` to `origin/main`

Practical interpretation:
- when open PR count is zero, there is usually no value in leaving dozens of clean historical worktrees or merged local branches around
- a good final state is often `root main + only genuinely dirty worktree(s) + explicit preserve branch(es)`
- report this outcome explicitly so the user knows the workspace was reduced to the minimum safe set rather than merely lightly pruned

Additional lesson from repeated repo-local cleanup:
- the same kind of residue can appear in non-root worktrees too, especially in merged feature worktrees that touched repo-local checked-in skills
- if a merged/closed PR worktree is otherwise clean and its only remaining dirt is repo-local skill residue under `.agents/skills/**`, restore those files first and then re-evaluate the worktree for removal
- this is safer than preserving a merged stale worktree just because of incidental local guidance edits

### Additional practical case: detached worktrees may hold orphan local commits

Not every clean detached worktree is disposable.
A detached worktree can point at a commit that is not contained in any local branch or remote branch.
Deleting it blindly can lose the only remaining reference to that local commit.

Check this before removing a clean detached worktree whose purpose is unclear:

```bash
head=$(git -C <path> rev-parse HEAD)
git branch --contains "$head"
git tag --contains "$head"
```

Interpretation:
- if the commit is already represented by an open PR branch, remote branch, local branch, or another intentional preserved ref, the detached worktree is usually safe to remove
- if the commit is not contained in any branch or tag, preserve it by default or convert it into a named local branch before removing the worktree

Practical rule:
- clean detached helper clones that exactly match an open PR remote head are stale and removable when they are just redundant duplicates of the same preserved PR state
- however, if a detached worktree is the only local checkout at the current open-PR head while the named branch worktree is behind that head, keep the detached worktree until you intentionally realign or replace the older branch checkout
- clean detached worktrees whose `HEAD` is an orphan local commit are not stale by default

### Additional practical case: when the user wants a cleaner workspace, preserve orphan detached commits by promoting them to backup branches first

Sometimes the user wants the workspace itself cleaned up even when several detached worktrees are still worth preserving as local history.
In that case, the right move is often **not** to keep many detached worktrees around.
Instead:

1. classify detached worktrees into:
   - `dirty detached keep as worktree`
   - `clean detached keep as commit`
   - `clean detached stale/remove`
2. for each `clean detached keep as commit`, create a named local backup branch first:

```bash
git branch backup/<descriptive-name> <detached-sha>
```

Examples:
- `backup/pr103-image-click-close`
- `backup/pr223-numeric-ids`
- `backup/pr240-typography-refresh`

3. after the backup branch exists, remove the detached worktree:

```bash
git worktree remove --force <path>
```

Why this is valuable:
- preserves the local-only commit without leaving many detached worktrees cluttering the repo
- gives the user an inspectable named ref instead of an anonymous detached directory
- makes future cleanup easier because remaining worktrees more closely reflect active PRs or real dirty work

Practical rule:
- if a detached worktree is clean and orphaned but not obviously disposable, prefer `promote to backup branch + remove worktree` over leaving the detached worktree in place
- keep a dirty detached worktree as a worktree until its dirty patch is classified separately

### Additional practical case: multiple detached helpers can form a linear history, and only the latest one needs to survive

Some repositories accumulate many detached helper worktrees for one investigation or PR follow-up, for example:
- `pr103-zoomable-figure`
- `pr103-value-diagram-webp`
- `pr103-value-diagram-modal`
- `pr103-image-click-close`

These may all be orphan local commits, yet still be safely reducible if they form a strict ancestry chain.

Check this with:

```bash
git merge-base --is-ancestor <older-sha> <newer-sha>
```

Interpretation:
- if `A` is an ancestor of `B`, keeping `B` preserves reachability to `A`
- if you have a chain `A -> B -> C -> D`, you do **not** need four detached worktrees to preserve that history
- you may keep only the newest representative detached worktree (for example `D`) and remove the older detached helpers (`A`, `B`, `C`), because their commits remain reachable from `D`

Practical rule:
- exact SHA duplication is not the only removable-detached case
- linear detached helper chains can be compressed to the newest kept commit, as long as you are intentionally preserving that newest commit somewhere
- do not apply this rule to a dirty detached worktree unless you separately classify its current dirty patch

### Additional practical case: a detached helper can exactly equal a merged PR head commit

A detached worktree may match the final remote head commit of an already merged PR.
That detached worktree is usually just a leftover local clone of the merged PR state.

Check this with:

```bash
env -u GITHUB_TOKEN gh pr view <number> --json headRefOid,state
```

Then compare the detached `HEAD` to `headRefOid`.

Interpretation:
- if the PR is `MERGED` and the detached `HEAD` exactly equals `headRefOid`, the detached worktree is redundant and removable
- this is true even if no local branch currently contains that exact detached commit, because the merged PR itself already records that state remotely

Practical rule:
- treat `detached HEAD == merged PR remote head` as stale helper residue, not as a unique local preservation obligation

### Additional practical case: local helper branches/worktrees can be redundant aliases of an open PR under a different name

A local branch/worktree may have no PR of its own yet still be redundant because it simply points to the same commit as another open-PR branch.
This often happens with helper names like `pr240-rewrite-main`, `pr240-rebase-main`, or other local-only convenience branches.

Related important case: `backup/pr123-*` branches often do not match the real historical PR head branch name at all.
For example, a local branch like `backup/pr259-ci-fix` may correspond to a merged PR whose actual GitHub head branch was something different like `feat/whitepapers-13-14-local`.
That means `gh pr list --state all --head <local-branch>` can incorrectly return nothing even though the branch is clearly PR residue.

In those cases, extract the PR number from the local branch name and inspect the PR directly:

```bash
env -u GITHUB_TOKEN gh pr view 259 --json number,state,title,url,headRefName,headRefOid,baseRefName,mergeCommit
```

Interpretation:
- if the PR number exists and is `MERGED`, the local `backup/pr123-*` branch is very likely post-merge residue or a local follow-up line derived from that merged PR
- if the branch is also far behind `origin/main`, has no attached meaningful dirty worktree, and disposable rebase checks conflict immediately, treat the branch history as stale even if the branch once represented meaningful local experimentation
- if several local `backup/pr123-*` variants exist, compare them against one another and keep only the one that still preserves unique value, if any

Practical rule:
- for `backup/pr123-*`, do not rely only on `--head <branch-name>` PR lookup
- also inspect the actual PR by number when present in the branch name
- this is often the difference between correctly identifying merged stale residue and incorrectly preserving it as an apparently PR-less local branch

Check for aliasing before preserving a no-PR branch-backed worktree:

```bash
git rev-parse <local-helper-branch>
git rev-parse <open-pr-branch>
git rev-list --left-right --count <local-helper-branch>...<open-pr-branch>
```

Interpretation:
- if the local helper branch points at exactly the same commit as an open PR branch or its remote head, the helper branch/worktree is redundant and can be removed
- if the helper branch has its own unique commits or dirty worktree changes, preserve it until you classify that work explicitly

Practical rule:
- `no open PR for this branch name` is not enough to preserve a helper branch/worktree
- first check whether it is merely an alternate local alias of an already-preserved open PR state

### Additional practical case: a branch can be a no-op local alias of main itself

Some repositories accumulate local convenience branches and worktrees that are not tied to any open PR and no longer represent independent work.
A common pattern is:
- the branch tracks `origin/main` directly
- the branch `HEAD` is exactly equal to local `main` / `origin/main`
- the attached worktree is clean
- the branch name suggests a one-off helper or topic, but the tree no longer differs from main at all

Important counter-case:
- the branch `HEAD` can still equal `main` / `origin/main`, yet the attached worktree may contain meaningful tracked modifications
- in that case, the branch pointer itself is a no-op alias, but the live worktree is **not** stale residue
- do not delete that worktree just because the branch SHA matches main; classify the current dirty patch separately
- if you want cleaner naming, you may rename the branch into an explicit preservation namespace such as `preserve/*` or another user-meaningful local branch name before reporting the final state

Check this with:

```bash
git rev-parse <branch>
git rev-parse main
git rev-parse origin/main
git rev-list --left-right --count origin/main...<branch>
git -C <worktree> status --short --branch
```

Interpretation:
- if the branch SHA equals `main` and `origin/main`, and the worktree is clean, it is just a no-op alias of main
- this is stale even if the branch still has a valid local name and an attached worktree directory

Safe handling:

```bash
git worktree remove <worktree>
git branch -D <branch>
```

Practical rule:
- do not preserve a clean branch/worktree that is literally identical to main just because it is branch-attached
- treat `tracks origin/main + same SHA as main + clean worktree` as a safe stale-deletion case

### Additional practical case: a local alias branch can equal the current open-PR head while the official local PR branch is stale

Sometimes the repository ends up with both:
- the official local PR branch name (for example `docs/publication-refactor-plan`)
- a local helper/alias branch name (for example `pr287-rewrite`)

A nearby variant is a no-PR local helper branch that tracks `origin/main` but actually exists only as an alias for the current open PR head or for current `main`.
Examples from corp-web-japan cleanup included helper names like `pr300-main`, `pr301-main`, and `fix/news-sitemap-indexing`.

Signal patterns:
- the branch name does not match any open PR head branch
- `git rev-list --left-right --count origin/main...<branch>` shows `0 0` or a tiny helper delta like `0 1`
- `git rev-parse <branch>` exactly equals either:
  - the current `origin/main` tip, or
  - an open PR's `headRefOid`
- the attached worktree, if any, is clean

Interpretation:
- if the branch SHA equals `origin/main`, it is just a redundant local alias of main and is stale
- if the branch SHA equals an open PR `headRefOid` but the branch name is not the official PR branch name, it is just a redundant local alias of the PR head and is stale once the official branch/worktree is synchronized

Recommended handling:
1. identify whether the authoritative state should live on `main` or on the official PR branch name
2. if needed, first realign the official clean branch-backed worktree to the remote PR head
3. then delete the alias branch and its clean worktree

Practical rule:
- do not preserve no-PR helper branches that merely mirror `origin/main` or an open PR head under a convenience name
- keep the authoritative branch name; remove the alias

Additional concrete alias pattern:
- a local branch/worktree can track a live upstream branch for another open PR, but still be a stale alias if its local branch name is not an open PR `headRefName` and its SHA exactly equals the authoritative open PR branch/remote head
- example shape: `feat/news-source-audit` tracks `origin/feat/use-cases-collection-migration`, has the same HEAD as `feat/use-cases-collection-migration`, and the worktree is clean
- in that case, preserve the official open PR branch/worktree and delete the alias worktree + local alias branch; do not keep both just because the alias has a non-gone upstream

Additional practical case: a clean branch-backed worktree can be a no-op alias of `origin/main` even when it has a respectable feature/docs branch name

Signal pattern:
- the worktree is clean
- `git diff --stat origin/main..<branch>` is empty
- `git cherry origin/main <branch>` is empty
- a disposable `git rebase origin/main` test is a no-op (`HEAD is up to date.`)
- the branch is not an open PR head branch

Safe handling:
- treat it as stale alias residue, not as meaningful local work
- remove the worktree and then delete the local branch

This catches cases where a leftover worktree/branch survives under a real-looking name such as `docs/...` but is actually identical to latest `origin/main`.

### Additional practical case: root staged residue copied from a merged detached helper worktree

A repository can keep an old local branch like `pr-65` even after the real active PR head branch has moved or been renamed to something else such as `review/pr65-validity` or `refactor/remove-unused-resource-flows`.

Signal pattern:
- `gh pr list --state all --head pr-65` returns nothing
- but `gh pr view 65` shows the PR is still `OPEN`
- the PR's actual `headRefName` is a different branch
- a separate local branch/worktree already matches that real open-PR head SHA
- the local `pr-65` branch is just an older local snapshot or alias

Recommended handling:
1. inspect the PR directly by number when the local branch name encodes it
2. compare the local `pr-<number>` SHA against the real open PR `headRefOid`
3. if another local branch/worktree already represents the real open PR head, delete the stale `pr-<number>` local branch
4. preserve the real open-PR branch/worktree only

Practical rule:
- an open PR does not automatically protect every local branch whose name references that PR number
- protect the branch/worktree that matches the current remote PR head; delete older local aliases such as `pr-65` when they are no longer authoritative

And the helper branch, not the official local branch, matches the current remote PR head commit.

Check this with:

```bash
env -u GITHUB_TOKEN gh pr view <number> --json headRefName,headRefOid

git rev-parse <official-local-branch>
git rev-parse <alias-local-branch>
git rev-parse origin/<official-local-branch>
```

Interpretation:
- if the alias branch SHA exactly equals the PR `headRefOid`, the alias is not independent work; it is just a local mirror of the current PR head under the wrong name
- if the official local PR branch is clean but behind/diverged from `origin/<official-local-branch>`, the right cleanup is usually:
  1. realign the official local PR branch/worktree to `origin/<official-local-branch>`
  2. delete the alias branch/worktree afterward

Safe handling:
- prefer resetting the official clean local PR worktree to `origin/<official-local-branch>` when it has no local dirt:

```bash
git -C <official-worktree> reset --hard origin/<official-local-branch>
```

- after the official branch matches the remote PR head, remove the stale alias worktree and branch:

```bash
git worktree remove <alias-worktree>
git branch -D <alias-branch>
```

Practical rule:
- do not preserve a no-PR alias branch just because it holds the latest PR head commit
- preserve the official PR branch name as the durable local representation, and remove the alias once the official branch is synchronized

### Additional practical case: root staged residue copied from a merged detached helper worktree


Some repositories accumulate local branch-attached helper worktrees with names like:
- `pr277-rewrite-latest`
- `pr280-rewrite-1114436`
- `pr281-rewrite-149d1e2`

These are not detached, and they may even track `origin/main`, but they can still be stale residue rather than meaningful active branches.

Typical signal pattern:
- the branch name is a local helper/rewrite alias rather than the real PR head branch name
- the related PR found by number is already `MERGED`, or still/open only under a different canonical head branch name
- `git status --short --branch` inside the attached worktree is clean
- `git rev-list --left-right --count origin/main...<branch>` shows a small helper delta such as `ahead 1, behind N`
- the branch subject matches a merged/open PR title and looks like a convenience rewrite, squash, or follow-up alias

Recommended handling:
1. inspect the related PR directly by number when present in the branch name:
   ```bash
   env -u GITHUB_TOKEN gh pr view <number> --json number,state,headRefName,headRefOid,title,url
   ```
2. inspect the attached worktree dirtiness:
   ```bash
   git -C <worktree> status --short --branch
   git -C <worktree> diff --stat || true
   ```
3. if the worktree is clean and the branch is only a helper alias of already-preserved or already-merged PR state, treat it as stale and remove both the worktree and the branch
4. if the worktree has tracked or meaningful untracked changes, preserve it even if the branch history itself looks stale

Useful summary labels:
- `stale attached helper alias`
- `merged PR residue with clean attached worktree`
- `stale history + meaningful local dirty worktree`

### Additional practical case: root staged residue copied from a merged detached helper worktree


When a user asks whether a local branch is still valid or stale, do not rely only on raw commit count, branch age, or whether a PR once existed.
A better test is to evaluate the branch as if its current net effect were squashed into one commit, then see whether that single net patch still ports cleanly to the latest `origin/main`.

This is especially useful for:
- old `backup/pr123-*` branches
- rebased or squashed helper branches whose original commit structure is no longer meaningful
- deciding whether a branch still represents a portable change vs stale historical residue

Procedure:

1. find the branch merge-base with latest main:

```bash
base=$(git merge-base origin/main <branch>)
```

2. create a synthetic squash commit using the branch's current tree but the merge-base as parent:

```bash
tree=$(git rev-parse <branch>^{tree})
squash=$(printf 'TEMP SQUASH %s\n' <branch> | git commit-tree "$tree" -p "$base")
```

This does **not** modify the real branch history.
It creates a temporary commit object representing the branch's net diff as one patch.

3. inspect the net diff vs latest main:

```bash
git diff --stat --find-renames origin/main...$squash --
git diff --name-status --find-renames origin/main...$squash --
git cherry origin/main $squash || true
```

4. test portability in a disposable detached worktree:

```bash
tmp=$(mktemp -d)
wt="$tmp/rebase-check"
git worktree add --detach "$wt" "$squash"
git -C "$wt" rebase origin/main
```

Interpretation:
- if the synthetic squash rebases cleanly, the branch still has a coherent portable net change and is usually worth keeping
- if it conflicts immediately and broadly, the branch history and its net patch are stale relative to latest main
- if the branch is stale but a separate dirty worktree on the same base contains a **small focused uncommitted diff**, treat that dirty patch separately instead of judging it by the stale branch alone

Useful summary labels:
- `valid branch: squash patch rebases cleanly onto latest main`
- `stale branch: synthetic squash conflicts broadly on latest main`
- `stale branch history + meaningful dirty detached patch`

Additional practical case: judge the current worktree state, not only the committed branch tip

When the user explicitly asks whether a **local branch is still valid given its current local changes**, the right object to test is often not the branch tip tree alone.
A branch can be merged/stale in committed history while the attached worktree still contains meaningful uncommitted changes.
Conversely, a branch can look large or old, but its *current* worktree state may still squash and rebase cleanly onto latest `origin/main`.

Recommended procedure for branch-backed worktrees:

1. compute the merge-base with latest main as usual:

```bash
base=$(git merge-base origin/main <branch>)
```

2. build a temporary tree from the **current worktree state** rather than from `<branch>^{tree}` alone
   - copy the worktree's current index to a temporary index file
   - stage all tracked + untracked current changes into that temporary index
   - write a tree from that temporary index

Example pattern:

```bash
tmpidx=$(mktemp)
idxpath=$(git -C <worktree> rev-parse --git-path index)
cp "$idxpath" "$tmpidx"
GIT_INDEX_FILE="$tmpidx" git -C <worktree> add -A
worktree_tree=$(GIT_INDEX_FILE="$tmpidx" git -C <worktree> write-tree)
rm -f "$tmpidx"
```

3. create the synthetic squash commit from that current worktree tree and the merge-base parent:

```bash
squash=$(printf 'TEMP SQUASH %s\n' <label> | git commit-tree "$worktree_tree" -p "$base")
```

4. rebase that synthetic squash onto latest `origin/main` in a disposable detached worktree

Interpretation:
- if the synthetic squash built from the **current worktree state** rebases cleanly, the local work is still portable and usually worth preserving
- if the branch lineage is stale or already merged but the current worktree-state squash rebases cleanly, classify it as:
  - `stale branch history + meaningful current local patch`
- if the synthetic squash is effectively empty or rebases as a no-op, classify it as stale residue
- if the synthetic squash conflicts broadly, that is strong evidence the current local state itself is stale or at least not cheaply portable

Practical lessons from corp-web-japan cleanup:
- a merged/no-PR branch can still deserve preservation if its attached worktree contains meaningful uncommitted documents or source edits, and the worktree-state squash rebases cleanly onto latest main
- a no-PR alias branch whose squash diff is empty and whose rebase is a no-op is safe stale residue
- a merged stale branch with only temp PR-body scratch files is still stale even if the synthetic squash technically rebases cleanly

Practical lesson from corp-web-japan cleanup:
- a stale backup branch like `backup/pr223-rebase-squash` can fail the squash-portability test, yet a detached worktree at the same HEAD may still contain a small meaningful local follow-up patch worth preserving
- do not auto-delete the dirty detached worktree just because the related branch failed the squash validity test

### Additional practical case: open-PR detached helpers can form a linear chain; remove redundant older clones too

Open PR work often leaves multiple detached helper worktrees such as `...-pr285b`, `...-pr285c`, `pr277-ci-fix`, etc.
Do not preserve them just because the PR is open.

Check:

```bash
git rev-parse HEAD
env -u GITHUB_TOKEN gh pr view <number> --json headRefOid,state
```

Then, if needed, compare helper commits to one another:

```bash
git merge-base --is-ancestor <older-helper-sha> <newer-helper-sha>
```

Interpretation:
- if a detached helper exactly equals the open PR head commit and is clean, it is a redundant clone and safe to remove
- if another clean detached helper is an ancestor of that newer preserved PR helper state, it is also redundant and safe to remove
- keep only the authoritative branch-backed worktree (or at most the newest detached helper if there is a special reason), not the whole helper chain

Practical lesson from corp-web-japan cleanup:
- `internal-events-demo-pr285c` was a clean detached clone equal to open PR #285 head and safe to remove
- `internal-events-demo-pr285b` was an older clean detached ancestor of that same line and also safe to remove
- later helper chains such as `cta-glow-soften`, `pr301-lint`, and similar detached follow-up clones showed the same pattern: once a clean official branch worktree was reset to the current remote PR head, the detached helper clones became redundant and removable
- a later variant showed the official branch-backed worktree itself could be behind the remote open-PR head while detached helpers held newer commits; in that case, first clear disposable temp files from the official worktree if needed, then hard-reset the official clean branch worktree to `origin/<pr-branch>`, and only after that remove the detached helper clones

### Additional practical case: branch names and PR head names can change mid-cleanup, and new local aliases can appear while you are working

In fast-moving repos, the set of open PR head branches may change during the cleanup session itself.
A branch that was non-open at the start can later become the real open PR head, and new local helper branches/worktrees can also appear mid-session.

Practical rule:
- before each destructive cleanup batch, refresh again with `git fetch --prune`, `gh pr list --state open`, and `git worktree list`
- do not rely on an earlier same-session snapshot when deciding whether a branch/worktree is stale
- if an alias branch becomes the actual open PR head, preserve it and reclassify the formerly official but older local branch/worktree as the stale residue

Additional practical case: a branch-attached no-op alias can point exactly at `origin/main`

Sometimes a local branch/worktree is clearly not an active PR branch, yet it still survives because it simply points at the same commit as `origin/main` or local `main`.
Examples are helper names like `pr300-main`, `pr301-main`, or other temporary labels created during rebase/review work.

Check this with:

```bash
git rev-parse <branch>
git rev-parse origin/main
git rev-list --left-right --count origin/main...<branch>
```

Interpretation:
- if the branch SHA exactly equals `origin/main` and it has no open PR role, it is a no-op local alias and safe to delete
- if its attached worktree is also clean, remove both the branch and the worktree

Useful summary label:
- `stale no-op alias: branch == origin/main`

Additional practical case: duplicated untracked residue across two stale worktrees

Sometimes two old non-open-PR worktrees both carry the same untracked residue, for example:
- copied image assets
- copied generated content-state trees
- identical untracked content directories

Signal pattern:
- both worktrees are already stale candidates by PR/history rules
- the untracked files are byte-for-byte identical (or directory-identical) between the two worktrees
- neither worktree has other unique tracked modifications that justify preserving both

Recommended handling:
1. compare the untracked files/directories directly between the two worktrees
2. if they are identical, keep at most one representative worktree
3. remove the duplicate stale worktree and its branch
4. report clearly which remaining worktree still holds that local residue

Practical rule:
- do not preserve multiple stale worktrees just because each has the same untracked leftovers
- treat `duplicate residue in multiple stale worktrees` as a safe consolidation case

Additional practical case: untracked nested clone inside another repo can be stale residue

A parent repository can contain an untracked subdirectory that is itself a full git clone with its own `.git`, for example a review helper like `confluence-mdx-pr910/`.

Signal pattern:
- the parent repo sees it as `?? <dir>/`
- inside, `git rev-parse --show-toplevel` succeeds
- the nested clone's branch or directory name points at a historical PR number or old task snapshot
- the corresponding GitHub PR is already `MERGED` or `CLOSED`
- the nested clone has no meaningful new dirt of its own

Recommended handling:
1. inspect the nested clone's remote and status
2. check the referenced PR directly by number when available
3. if the nested clone is just a merged PR snapshot, remove the whole nested clone directory from the parent repo

Practical rule:
- do not preserve untracked nested clones by default just because they are full repos
- if they are merged PR leftovers, treat them as disposable workspace residue

Additional practical case: untracked app-like directory may still be pure local junk if it only contains runtime/test artifacts

A surprising untracked directory under a repo (for example `frontend/meetpie/`) can look like a missing project, but may actually be only local residue.

Signal pattern:
- top-level contents are things like `node_modules/`, `playwright-report/`, `test-results/`, `.vite/`, or other runtime/build artifacts
- there are no source files, config files, or meaningful tracked-like project files beyond those generated artifacts
- the directory is not part of the repository's expected tracked app layout

Recommended handling:
1. inspect the top-level contents, not just the directory name
2. if it only contains generated runtime/test/install artifacts, classify it as local junk
3. delete the whole directory

Practical rule:
- when judging untracked directories, prefer content-based classification over name-based caution
- `untracked directory containing only node_modules/test-results/playwright-report` is safe local junk

Additional practical case: root staged residue copied from a merged detached helper worktree

Sometimes the root `main` worktree is not just dirty; it contains a staged set of files that exactly matches a clean detached helper worktree from a recently merged PR.
This can happen after ad hoc comparison, cherry-pick, or conflict-resolution experiments.

Safe handling:
1. inspect staged vs unstaged root changes separately:

```bash
git diff --cached --name-only
git diff --name-only
```

2. compare the suspicious staged file set against likely merged helper worktrees
3. if the root staged files are just residue from a merged PR helper worktree and do not represent new intended `main` work, drop them with targeted restore:

```bash
git restore --staged --worktree -- <paths...>
```

4. if a small remaining root-local edit is genuinely unpublished work, do **not** default to stashing it just to make cleanup look finished.

Preferred rule:
- when preservation matters, prefer keeping a branch/worktree over converting the state into a stash
- use a stash only as a narrow last resort when the user explicitly prefers cleanup completion over branch/worktree preservation, or when the work is already duplicated elsewhere and the stash is just a temporary escape hatch

This is safer than forcing a branch update that would overwrite a real local edit, and aligns better with users who find stash-based preservation low value compared with keeping an inspectable worktree/branch.

## 7c. Large-scale batch worktree cleanup (100+ worktrees)

In repos with extreme worktree counts, individual interactive removal is impractical. Use an automated classification script, but with these important safeguards:

**Parse `git worktree list --porcelain` carefully.**
The porcelain format uses blank-line-separated blocks, not a fixed line-per-block layout. Each block starts with `worktree <path>` and may include `HEAD <sha>`, `branch <ref>`, or `detached` on separate lines. A simple `grep "^worktree "` is not enough for classification; you must parse per-block.

**Classification algorithm for bulk removal:**
1. Fetch open PR heads: `gh pr list --state open --json headRefName,headRefOid`
2. Parse all worktree blocks into (path, head, branch, detached) tuples
3. Skip the root repo path entirely
4. Skip any branch-backed worktree whose branch is an open PR head
5. For everything else, check `git -C <path> status --short`:
   - non-empty status → **keep** (dirty)
   - empty status → **stale candidate**
6. Remove stale candidates with `git worktree remove --force <path>` from the owning repo context

**Post-batch cleanup:**
After any bulk `git worktree remove`, run:
```bash
git -C <repo> worktree prune --expire=now --verbose
git -C <repo> worktree prune
```

**Important failure mode:** `git worktree remove --force` may return a failure code even when the removal succeeded, especially when the filesystem directory was already partially removed by a prior operation. Do not retry blindly. Instead, verify by checking `git -C <repo> worktree list` for the next batch.

**Practical example from corp-web-app cleanup:**
- 112 worktrees detected
- 91 stale candidates identified by the above algorithm
- 84 successfully removed by batch script
- 8 reported failures, but filesystem paths were already gone
- Remaining were recovered by `git worktree prune --expire=now`

## 7d. Orphan worktree refs after filesystem removal

A removed worktree can leave a "ghost" entry in `git worktree list` even when the filesystem directory no longer exists. This happens when:
- a prior `git worktree remove` was interrupted
- a temporary worktree directory was deleted outside git
- a `git worktree remove` partially succeeded without updating git's internal registry

**Symptoms:**
```bash
git worktree list --porcelain
# still shows paths that ls says do not exist
```

**Diagnosis:**
```bash
ls -d <reported-worktree-path> 2>/dev/null || echo "directory does not exist"
git -C <repo> worktree list --porcelain | grep "worktree <missing-path>"
```

**Fix:**
```bash
git -C <repo> worktree prune --expire=now --verbose
git -C <repo> worktree prune
```

If the orphan refs persist after prune, they are usually harmless metadata in `.git/worktrees/*` pointing at non-existent gitdirs. The prune command cleans them. After prune, re-run `git worktree list` to confirm.

**Never run `rm -rf .git/worktrees/<name>` manually unless you have verified it is truly orphaned.** The `worktree prune` command is the correct and safe cleanup path.

## 7e. Clean root checkout on non-default branch with tracked changes tied to an open PR

When the root checkout is sitting on a non-default branch (e.g., `docs/hermes-skill-followup`) and that branch is connected to an **open PR**, the cleanup procedure is:

1. Inspect root diff with `git diff --stat HEAD --`
2. If changes are meaningful and tied to the open PR:
   - `git add -A && git commit -m "..."
   - `git push origin <branch>`
3. Only after successful push, switch root to default branch:
   ```bash
   git checkout main
   git pull --ff-only origin main
   ```
4. If `main` is not checked out anywhere, also update it directly:
   ```bash
   git branch -f main origin/main
   ```

Do NOT switch root to `main` before committing and pushing the open-PR branch changes. Doing so would leave uncommitted work that must be stashed or transplanted.

## 7f. Repo-internal worktree directories can leave root `?? .worktrees/` noise

Some repositories keep linked worktrees under a repo-internal directory such as `.worktrees/<name>`.
This is a valid and often preferred layout; see the common `repo-root-worktree-path-policy` skill.
After cleanup, the root worktree can still appear dirty with:

```bash
?? .worktrees/
```

This does not mean the remaining worktree is stale. It often just means the repo does not ignore its own local worktree container directory.

Safe handling:
- if the remaining worktree is intentionally kept, do not delete the directory just to make `git status` clean
- prefer a local-only ignore entry in `.git/info/exclude` such as:

```bash
.worktrees/
```

Why this is useful:
- it keeps the root checkout visually clean without changing tracked repo files
- it avoids committing `.gitignore` noise for machine-local worktree layout
- it is appropriate when the user wants a "workspace cleanup" result that leaves active internal worktrees intact

Additional practical case: `.worktrees/` can remain on disk as tracked placeholder infrastructure, while its child directories are orphan residue

A repository may intentionally track a placeholder like:

```bash
.worktrees/.gitkeep
```

In that case:
- the top-level `.worktrees/` directory itself is not disposable residue
- but many child directories under `.worktrees/*` can still be stale orphan leftovers from older worktrees

Safe validation flow:
1. enumerate currently registered worktrees:
   ```bash
   git worktree list --porcelain
   ```
2. compare each on-disk `.worktrees/<name>` directory against that registered set
3. inspect whether it has a `.git` file pointing to a live gitdir:
   - `.git` missing entirely -> likely orphan copy/residue
   - `.git` file exists but target `gitdir:` path no longer exists -> broken orphan residue
   - directory not registered in `git worktree list` -> do not treat it as a live worktree even if files remain inside
4. only after that, delete the orphan child directories
5. re-check whether `.worktrees/.gitkeep` or other tracked placeholder files remain, and preserve them if tracked

Useful checks:

```bash
git worktree list --porcelain
git ls-files --error-unmatch .worktrees/.gitkeep
```

Practical interpretation:
- `registered in git worktree list` is the source of truth for live worktrees
- an on-disk directory full of repo files or `.next/` outputs is still safe stale residue if it is not registered and its gitdir metadata is missing/broken
- do not remove the `.worktrees/` container itself when the only remainder is a tracked placeholder such as `.gitkeep`

## 7d. After deleting a worktree, your shell/session cwd may become invalid

If you remove the worktree that your current shell session is effectively rooted in, subsequent shell startup or commands can fail with errors like:

```bash
getcwd: cannot access parent directories: No such file or directory
```

This is especially common when agent sessions were launched from a repo-internal `.worktrees/...` path.

Safe handling:
- after batch worktree deletion, run subsequent commands with an explicit stable repo-root working directory
- prefer `workdir=<repo-root>` in tool calls or `git -C <repo-root> ...` command forms
- do not assume the session's inherited cwd is still valid after removing a sibling or current worktree path

Practical rule:
- once cleanup starts deleting worktrees, switch all remaining destructive/verification commands to explicit repo-root context
- this avoids false command failures unrelated to git state itself

Important Hermes/tooling quirk observed in practice:
- after a deleted/pruned worktree invalidates the session's inherited cwd, some later `terminal()` calls can still fail with `FileNotFoundError` even when you pass an explicit `workdir`
- if that happens, do not keep retrying the same `terminal()` pattern blindly
- fall back to `execute_code()` with Python `subprocess.run(..., cwd=<stable-repo-root>)` or otherwise force execution from a known-good cwd in a fresh context
- then clean the stale/prunable worktree registration with `git worktree prune` and continue verification from the stable repo root

Practical rule:
- once cleanup starts deleting stale worktrees/branches, re-run `git fetch --prune`, re-check open PR heads, and re-check `git worktree list` before each new deletion batch if the repo is actively changing
- this matters in fast-moving repos where `origin/main` or PR heads can advance during the cleanup session itself
- an especially important variant is when a branch that was open earlier in the session later becomes `MERGED`, while a different branch becomes the new active PR line; do not preserve the old branch/worktree based on stale earlier assumptions
- another common fast-moving case is that a candidate worktree path from an earlier snapshot may already have been removed, renamed, or replaced by the time you execute the deletion batch; always refresh the live worktree list and skip paths that are no longer registered instead of failing the whole cleanup batch on a stale pathname
- practical shell-loop lesson: a batch `git worktree remove ...` sequence can partially succeed for earlier entries and then fail on a later stale/non-registered path; after any such failure, assume the repo state already changed, refresh `git worktree list --porcelain`, and continue only from the refreshed live list rather than retrying the original batch blindly
- when another agent or human may be modifying the same repository concurrently, do not trust any earlier same-session snapshot for the final report either
- in that concurrent-edit case, branches can reappear under new names/paths, helper worktrees can be recreated, upstream tracking can change, open-PR state can flip while you are still auditing, and even a branch/worktree you just deleted can later reappear with the same name but a different tip/upstream because another actor recreated it
- also, a candidate that looked like a clean no-op alias a minute ago can become dirty or become an open-PR branch before you act; treat every destructive decision as valid only for the exact pre-delete snapshot you just verified
- therefore, before the final user-facing summary, re-run the full snapshot set (`git branch -vv`, `git worktree list --porcelain`, root `git status --short --branch`, and open PR query) and treat that last snapshot as the only authoritative statement of current state
- if the final snapshot contradicts an earlier deletion/classification result, explicitly report the latest live state instead of the earlier intermediate conclusion
- practical reporting rule: separate `what I deleted during this session` from `what exists right now` so the user can understand both the cleanup actions and any concurrent re-creations
- additional practical case: a branch can look like a local no-PR stale candidate at delete time, yet show up as an open remote PR immediately afterward because another actor opened/pushed it during the cleanup window or GitHub state changed between snapshots
- practical handling for that case:
  1. treat the pre-delete snapshot you verified as the basis for the local deletion decision
  2. after each destructive batch, refresh open PR state again before the final report
  3. if a just-deleted local branch/worktree now corresponds to an open remote PR, report this explicitly as `local cleanup completed, remote PR still/open now visible`
  4. do not pretend the branch was never deleted locally, and do not imply the remote PR was closed or removed unless you actually performed that action
- this distinction matters because the user's request may be repo-local cleanup only; deleting a local branch/worktree is not the same thing as closing or removing the remote PR
- after the cleanup batch, fast-forward the root `main` worktree to the latest `origin/main` when the root checkout is clean so the workspace ends in a refreshed baseline

Additional practical case: branch names and PR head names can change mid-cleanup, so a stale candidate can become active before you delete it

In repositories with active stacked follow-up work, a branch that looked like a non-open-PR stale candidate at the start of the session can later become the actual head branch of a newly opened PR, or an official branch can be replaced by a rewrite/rebase alias that now carries the real PR head.

Check this immediately before any destructive deletion batch:

```bash
env -u GITHUB_TOKEN gh pr list --state open --json number,headRefName,headRefOid,title,url
git for-each-ref --format='%(refname:short)|%(objectname:short)' refs/heads
git worktree list --porcelain
```

Then verify for each deletion candidate:
- whether the branch name now exactly matches an open PR `headRefName`
- whether the branch SHA now exactly matches an open PR `headRefOid`
- whether an attached helper branch/worktree with a different name has become the authoritative current PR head while the older official local branch is now stale

Practical interpretation:
- `non-open-PR at T1` does not guarantee `non-open-PR at T2`
- do not delete a candidate based only on an earlier snapshot from the same session
- if an alias branch becomes the actual open PR head, preserve it and reclassify the formerly official but outdated branch/worktree as the stale residue instead
- if a branch/worktree points exactly at `origin/main` and has no open PR role, treat it as a no-op local alias and delete it

## Additional practical case: clean root checkout can itself be a stale merged branch

Sometimes the repository root checkout is still sitting on a non-default branch even though:
- the root worktree is clean
- the branch has no open PR
- a related PR for that branch is already `MERGED` or clearly finished
- the user asked for workspace cleanup, which implies returning root checkouts to their default branches when safe

Typical examples:
- a root checkout left on `docs/...` after the PR merged
- a setup or spike branch like `jk/setup-1` whose PR already merged, while the repo should really end on `main` or `develop`

Recommended handling:
1. verify the root worktree is actually clean
2. confirm the branch is not needed by any open PR
3. confirm merged/finished PR evidence when available
4. check out the repo default branch in the root worktree
5. fast-forward that default branch to the latest remote tip
6. delete the old root branch locally

Example pattern:

```bash
git -C <repo> fetch origin --prune
git -C <repo> checkout <default-branch>
git -C <repo> pull --ff-only origin <default-branch>
git -C <repo> branch -D <old-root-branch>
```

Practical rule:
- do not leave a clean root checkout parked on an already-merged feature/docs/setup branch after workspace cleanup
- if the root worktree is clean and the branch is stale, returning the root checkout to the default branch is part of the cleanup result

## Additional practical case: the root checkout itself can be sitting on a merged stale branch

A repeated cleanup pattern is:
- the root repository path is not on `main`
- the root checkout branch is clean
- `gh pr list --state all --head <branch>` shows the branch's PR is already `MERGED`
- the user's real intent for `workspace 정리` is still `switch root back to main and refresh it`

Safe handling:
1. verify the root checkout is clean:
   ```bash
   git status --short --branch
   ```
2. verify the current branch is stale residue rather than active local work:
   ```bash
   env -u GITHUB_TOKEN gh pr list --state all --head <branch> --json number,state,title,url,headRefName,headRefOid
   git diff --stat origin/main..<branch> -- || true
   ```
3. if the branch is merged residue and the root checkout is clean, switch the root checkout back to `main` first:
   ```bash
   git checkout main
   git pull --ff-only origin main
   ```
4. only after the root is safely back on `main`, re-check whether the old branch still exists locally before trying to delete it

Important practical nuance:
- do not assume a branch seen in an earlier snapshot will still exist after the branch switch or by the time you run deletion commands
- after switching the root checkout back to `main`, refresh with `git branch -vv --no-abbrev` before any `git branch -d/-D` call
- if the branch is already gone, treat that as a normal concurrent/local-state change rather than an error that blocks cleanup

Useful summary label:
- `root checkout restored from merged stale branch to main`

## 8. Update local main safely

If `main` is not checked out in any worktree, update it directly:

```bash
git branch -f main origin/main
```

This is faster and safer than checking out `main` in a busy multi-worktree repo.

Verify:

```bash
git rev-parse main
git rev-parse origin/main
```

They should match.

## 7. Apply cleanup

### Remove safe detached clean worktrees

```bash
git worktree remove <path>
```

If a stale entry is already marked `prunable` and its linked `.git`/gitdir is broken or missing, `git worktree remove` may fail validation instead of cleaning it up. In that case, do not force repeated removal attempts; rely on prune from the owning repo:

```bash
git worktree prune
```

After batch removal:

```bash
git worktree prune
```

### Delete safe local branches

Use non-force delete first:

```bash
git branch -d <branch>
```

If `-d` refuses, do not immediately keep the branch by default. First verify whether all of the following are true:
- the branch is no longer attached to any kept worktree
- `gh pr list --state all --head <branch>` confirms the PR is already merged or closed
- the upstream ref is already gone or otherwise no longer authoritative
- `git cherry origin/main <branch>` shows the branch is only carrying squash/rebase residue rather than active unpublished work

When those checks confirm the branch is just post-merge local residue, force-delete is appropriate:

```bash
git branch -D <branch>
```

Only preserve the branch when those checks do not clearly prove it is stale.

## 8. Review backup branches before deleting them

Local `backup/*` branches often accumulate during repeated workspace cleanup and PR follow-up work. Do not treat every backup branch as automatically preservable just because it is not attached to a worktree.

Also recognize explicit preservation branches such as `preserve/*` as a separate category from stale helper residue.

Practical rule:
- if the branch name is an explicit preservation namespace like `preserve/*`, keep it by default during ordinary workspace cleanup unless the user explicitly asks to audit or delete preservation branches too
- this is especially important after earlier main-checkout recovery flows that created a named preservation branch to save meaningful local work before refreshing `main`
- do not auto-delete a `preserve/*` branch just because it has no open PR and no attached worktree
- instead, report it as an intentionally preserved backup line and leave the final decision to the user unless they clearly asked for deeper stale-branch adjudication
- do not imply that a `preserve/*` branch has a GitHub URL or web-review surface by default; verify first with `git ls-remote origin refs/heads/<branch>` and, if useful, `gh pr view <branch>` or `gh pr list --head <branch>`
- if the preserve branch exists only locally, report it explicitly as `local-only preserve branch; no GitHub link yet` and offer push as a separate explicit action instead of talking as though a review URL already exists

Also recognize explicit preservation branches such as `preserve/*` as a separate category from stale helper residue.

Practical rule:
- if the branch name is an explicit preservation namespace like `preserve/*`, keep it by default during ordinary workspace cleanup unless the user explicitly asks to audit or delete preservation branches too
- this is especially important after earlier main-checkout recovery flows that created a named preservation branch to save meaningful local work before refreshing `main`
- do not auto-delete a `preserve/*` branch just because it has no open PR and no attached worktree
- instead, report it as an intentionally preserved backup line and leave the final decision to the user unless they clearly asked for deeper stale-branch adjudication

For each backup branch, collect:

```bash
git rev-parse <backup-branch>
git show -s --format='%s' <backup-branch>
git rev-list --left-right --count origin/main...<backup-branch>
git cherry origin/main <backup-branch> || true
git branch --contains $(git rev-parse <backup-branch>)
env -u GITHUB_TOKEN gh pr list --state all --head <backup-branch> --json number,state,title,url,headRefName
```

Then validate portability with a disposable rebase worktree:

```bash
tmp=$(mktemp -d)
wt="$tmp/rebase-check"
git worktree add --detach "$wt" <backup-branch>
git -C "$wt" rebase origin/main
# if conflicting, inspect `git -C "$wt" status --short --branch` and abort
```

Important backup-branch diff pitfall:
- a backup branch that tracks `origin/main` but is far behind can make `git diff origin/main..<backup-branch>` look enormous, especially in repositories where generated/bundled skill libraries or other broad artifacts changed on `main`
- do not delete the branch solely because that direct two-dot diff shows huge stale deletions or churn
- first build the synthetic squash commit from the backup branch tree using the branch merge-base as parent, then inspect `git diff --stat origin/main...$squash` and run the disposable rebase test
- if the synthetic squash reduces to a small focused diff and rebases cleanly onto latest `origin/main`, classify it as portable unpublished local work and preserve it, even if the raw branch-vs-main diff is huge
- useful label: `old backup baseline with small portable net patch`

Repeated-cleanup escalation for a portable backup branch:
- if a repeated `workspace 정리` request arrives after you already reported such a backup as preserved, treat that as permission to make the workspace cleaner without losing the work
- promote only the synthetic-squash net patch to a fresh latest-`origin/main` branch/worktree, preferably opening a PR if this repo's completion rules expect PRs
- if applying the generated patch directly onto latest `origin/main` fails because the newest main context drifted, do not abandon the preservation: create the new branch/worktree at the synthetic squash commit itself, then `git rebase origin/main`; the same rebase test that proved portability should carry it forward
- after the fresh branch/PR remote head is verified, remove the old backup worktree and delete the old backup branch, then reset/fast-forward root `main` to `origin/main`
- final report should distinguish: old backup removed, portable payload preserved on the new branch/PR, root main now clean

Interpretation:
- if the backup branch is already contained in a more official kept branch (for example an open-PR branch or an intentionally kept follow-up branch), it is usually redundant and can be deleted
- if the disposable rebase exits clean but reports `skipped previously applied commit`, the branch is effectively already absorbed by latest `main` and is stale
- if the branch immediately produces broad structural conflicts on rebase and is only an old backup of an abandoned line, that is strong stale evidence
- if the branch is the newest representative of a local experimental line, keep it and consider deleting older backup branches from the same chain
- if two backup branches preserve the same exploratory area, prefer keeping the newer or more representative one and delete the older helper copy

Useful summary labels:
- `stale backup: absorbed by main`
- `stale backup: redundant with kept branch`
- `keep backup: latest representative of local line`
- `uncertain backup: orphan local line with no clear replacement`

### Additional practical case: after a branch-by-branch stale audit, old backup branches with no remaining local work should usually be deleted

In PR-heavy repositories, it is common to accumulate many `backup/pr123-*` branches that once preserved meaningful exploratory or follow-up work.
That historical meaning alone is **not** a reason to keep them forever.

After you have already done the branch-by-branch review, use this stricter cleanup rule:

Delete the backup branch when all are true:
- it is not the current branch
- it is not attached to a kept worktree
- it is not needed by any open PR
- any associated PR is already `MERGED` or `CLOSED`
- there is no remaining dirty local worktree carrying uncommitted changes for that line
- the branch exists only as stale historical residue, even if its commits once represented meaningful work

Practical interpretation:
- `historically meaningful` is different from `currently worth preserving locally`
- if the useful part of the line has already been merged, superseded, or intentionally abandoned, and there is no surviving dirty patch to protect, prefer deletion
- preserve only the cases where there is still active local state to save, such as a dirty attached/detached worktree or a clearly designated latest representative branch

This is especially useful after a cleanup audit where several stale backups were initially reported as `meaningful historical lines` but were later deleted because they had no open PR, no kept worktree, and no current local edits.

## 9. Final verification

Run:

```bash
git rev-parse main
git rev-parse origin/main
git branch --show-current
git worktree list
```

Also report remaining dirty worktrees explicitly so the user can decide on follow-up cleanup.

## 9a. Do not assume all local worktrees live under the repo's internal `.worktrees/` directory

A practical failure mode is to clean only `git worktree list` entries that happen to be under the repo root (for example `.worktrees/...`) and forget about sibling worktrees elsewhere in the workspace, such as:

- `/Users/.../corp-web-japan-querypie-ja-guardrails`
- `/Users/.../corp-web-japan-querypie-ja-skill`
- `/Users/.../corp-web-japan-t-cookie-preference`

These still appear in `git worktree list`, but they are easy to overlook if you visually focus only on `.worktrees/` paths.

Practical rule:
- when the user asks to clean non-open-PR worktrees/branches, classify **all** entries from `git worktree list --porcelain`, regardless of whether the path is inside the repo root or in a sibling directory elsewhere in the workspace
- only after that should you filter by open-PR connection, dirtiness, and stale-vs-meaningful-local-work status

Additional practical rule:
- for detached helper worktrees with no branch, treat them as open-PR-connected if their path/name clearly encodes an open PR number such as `pr318-*`, even if they are not branch-backed
- this prevents accidentally sweeping open-PR helper clones into the non-open-PR stale bucket

Typical safe classification order:
1. enumerate every worktree from `git worktree list --porcelain`
2. map branch-backed worktrees to open PR head branches
3. map detached helpers by path/name PR-number hints like `pr318`, `pr-318`, or `pr_318`
4. only then classify the remainder as true non-open-PR candidates

## 9b. Final live-state recheck should separate deletion history from current reality

For this user, the final answer should not stop at "I deleted X". Re-run a final live snapshot and report both:
- what was deleted during this cleanup pass
- what exists right now

Minimum final snapshot for repo-local cleanup:

```bash
git status --short --branch
git worktree list --porcelain
gh pr list --state open --json number,headRefName,headRefOid,url
git branch -vv --no-abbrev
```

If the repo uses a repo-internal worktree container such as `.worktrees/`, also compare the registered worktrees against the on-disk child directories so you can report whether orphan residue still exists:

```bash
find <repo>/.worktrees -mindepth 1 -maxdepth 1 -type d | sort
```

Interpretation:
- if the remaining state is just root `main` plus branch-backed worktrees for currently open PR head branches, the repo is already at the minimum safe repo-local state
- in that case, say explicitly that no additional safe stale worktrees/branches remain
- if the on-disk `.worktrees/*` directories match the registered worktrees and no extra orphan directories remain, report that the repo-internal worktree container is consistent too

### Minimal-safe end-state rule

Do not keep hunting for deletions just to make the repo look emptier.
If the final live snapshot shows only this reduced set, the cleanup is already complete:
- the root/default-branch checkout
- branch-backed worktrees that correspond to currently open PR head branches
- dirty worktrees with meaningful local tracked or source-like untracked changes

In that situation:
- do not describe the repo as "partially cleaned" or imply more automatic deletion is still expected
- explicitly report that no further safe stale deletions remain
- distinguish `stale branch/worktree history` from `meaningful current dirty patch`
- if a no-open-PR worktree is dirty and its diff/untracked files look like real source/test work rather than disposable residue, preserve it and call it out as an intentional remaining line

Useful summary labels:
- `already at minimum safe repo-local state`
- `remaining non-PR worktree preserved because it has meaningful local edits`
- `no additional safe stale worktrees/branches remain`

### Additional practical case: clean non-PR worktree can still be meaningful unpublished local work

A local branch-backed worktree should not be deleted just because:
- its earlier PR is already `MERGED`
- the branch is not tied to any current open PR
- the worktree itself is currently clean

Signal pattern:
- `gh pr list --state all --head <branch>` shows only an older merged PR for the same branch name
- `git status --short --branch` in the worktree is clean
- but `git diff --stat origin/main..<branch>` is non-empty
- and `git rev-list --left-right --count origin/main...<branch>` shows the branch is still ahead of latest `origin/main`

Interpretation:
- this is not ordinary merged-PR residue anymore
- it usually means the branch accumulated a later unpublished follow-up commit after the merged PR
- classify it as `meaningful unpublished local work`, not `stale`

Safe handling:
1. verify the branch is really still unique versus latest main:
   ```bash
   git diff --stat origin/main..<branch>
   git log --oneline -1 <branch>
   ```
2. if the worktree is clean but the branch is ahead with a real diff, preserve it by default
3. report it separately from open-PR worktrees as a local unpublished line the user may later push, PR, or discard intentionally

Useful summary label:
- `clean unpublished follow-up branch preserved`

### Additional practical case: an open PR branch can still be ahead of its remote head and should be preserved as active follow-up work

A local branch-backed worktree is not stale just because the GitHub PR is open and the local branch no longer matches the current remote PR head exactly.
A common pattern during PR follow-up is:
- `gh pr list --state open` still shows the branch as the open PR head branch
- but local `git branch -vv` shows something like `ahead 1` or `ahead N, behind M`
- the worktree may even be clean at that moment because the extra follow-up is already committed locally but not pushed yet

Recommended handling:
1. if the branch name still matches an open PR head branch, treat it as active by default
2. compare the local branch SHA to the open PR `headRefOid`
3. if the local branch is ahead of the remote PR head, preserve it as active local follow-up work, not stale residue
4. only consider deletion after the PR is merged/closed and a refreshed snapshot shows upstream gone plus a clean worktree

Practical interpretation:
- `open PR + local ahead-of-remote state` is not a cleanup target
- this state often means there is an unpublished follow-up commit waiting to be pushed, even if `git status` is clean
- on a later cleanup pass, the same branch can become safely removable once the PR merges and the upstream disappears

### Additional practical case: after a burst of merges, the right cleanup is often a bulk sweep of merged clean PR worktrees before updating main

A common repo-local cleanup snapshot is:
- `git fetch --prune` shows local `main` is behind `origin/main`
- several branch-backed worktrees are still present
- most of those branches now show upstream `[gone]`
- `gh pr list --state open` returns only a much smaller active set than the number of local worktrees
- per-worktree inspection shows many of the non-open-PR worktrees are completely clean
- `gh pr list --state all --head <branch>` confirms those branches' PRs are already `MERGED`

Recommended handling:
1. inspect each non-open-PR worktree for real dirt first
2. classify `merged PR + clean worktree + upstream gone` as safe stale residue
3. if those stale merged worktrees still show diffs for files the user just requested for a new PR, do not trust that stale worktree view yet; first fast-forward root `main` (after preserving unrelated root dirt) and re-check the requested files against fresh latest `origin/main`
4. if the requested-file diff disappears on fresh latest main and survives only inside merged stale worktrees, treat it as historical residue rather than as current PR payload
5. remove those clean merged worktrees in one batch
6. delete the corresponding local branches immediately after the worktrees are gone
7. only then fast-forward root `main` to `origin/main` when needed
8. after any PR creation or cleanup batch, take one more live root snapshot; if root `main` unexpectedly picked up new tracked residue during the operation, preserve that residue onto a fresh local-only branch/worktree and restore root clean instead of declaring cleanup complete with a dirty `main`
9. re-check that any remaining non-main worktree is either:
   - an open PR head branch, or
   - a dirty local line that still needs preservation

Practical interpretation:
- do not leave many clean merged PR worktrees around just because they are branch-backed
- when the only survivor after the sweep is an open-PR worktree with meaningful local edits, that is the intended minimum-safe end state
- this batch-remove-then-fast-forward order works well because it avoids reporting stale merged lines as if they were still active local context

## Practical lessons

- In a large multi-worktree repo, most safe wins come from removing clean detached review/rebase/squash worktrees first.
- Dirty worktrees often contain half-finished or forgotten work; preserve them by default.
- `git fetch --prune` can make many upstreams appear "gone"; do not treat that alone as permission to delete local branches.
- If the workspace root is not a repo, repository discovery is a prerequisite, not an optional convenience.
