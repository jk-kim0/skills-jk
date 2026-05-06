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

This workflow is for repositories that may have many old worktrees, detached review trees, and branches whose upstream refs were pruned.

## Goals

1. Update the local default branch (usually `main`) to match the latest remote HEAD when the root worktree is clean
2. Remove only clearly safe stale worktrees
3. Remove only clearly safe stale local branches
4. Preserve dirty worktrees, active work, and unmerged branches

User-specific requirement:
- treat default-branch update as part of workspace cleanup by default
- for `main`-based repos, align local `main` with the latest `origin/main` via fetch + fast-forward when safe
- if the root worktree is dirty or the update is not a clean fast-forward, preserve and report instead of forcing

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
- the branch has a small local-only post-merge commit, but the worktree is clean and that commit is just narrow follow-up residue (for example a tiny docs/skill cleanup) with no open PR or active dirty worktree depending on it

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
3. test whether the current dirty patch still has unique value on latest `origin/main`
   - export only the dirty diff for the focused files:
     ```bash
     git -C <worktree> diff -- <paths...> > /tmp/current-dirty.patch
     ```
   - create a disposable detached worktree at `origin/main`
   - run:
     ```bash
     git -C <temp-main-worktree> apply --check --3way /tmp/current-dirty.patch
     git -C <temp-main-worktree> apply --3way /tmp/current-dirty.patch
     git -C <temp-main-worktree> status --short --branch
     git -C <temp-main-worktree> diff --stat
     ```
   Interpretation:
   - if `apply --check --3way` fails, the patch is not cleanly portable and may need manual salvage
   - if apply succeeds and the temp worktree then shows the expected modified files, the dirty patch is still a real candidate for transplant onto fresh main
   - if apply succeeds but `status` and `diff` remain empty afterward, the patch is effectively already absorbed by latest `main` (a practical no-op) and usually does **not** justify preserving the dirty worktree by itself
4. if needed, simulate `git rebase origin/main` in a disposable helper worktree to judge whether the branch history itself is salvageable or just stale
5. separate the verdict into two parts:
   - branch history stale vs not stale
   - current dirty local edits meaningful vs disposable

Practical interpretation:
- if the branch history is stale but the current dirty edits are narrow, coherent, and purposeful, preserve the worktree even if you intend to retire the branch history later
- in that situation, the best follow-up is often:
  - discard or retire the stale branch history
  - recreate a fresh latest-main branch/worktree
  - transplant only the meaningful current dirty patch onto the fresh branch
- do not classify the whole worktree as stale just because the branch/PR lineage is stale

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
- if the remaining dirt is real project files (for example tracked deletions like `D postcss.config.mjs`), preserve the worktree

Be especially careful with `.hermes/`-style directories:
- they are often safe to ignore for stale classification, but confirm they are untracked local runtime artifacts before deleting
- if you are not confident they are disposable, preserve the worktree and report it
- if `.hermes/` is the only remaining dirt and the associated remote branch/PR is already merged, treat the worktree as stale and remove it with `git worktree remove --force ...` if needed

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

Safe handling:
1. inspect the root diff directly:

```bash
git diff -- .agents/skills/... docs/...
```

2. compare that file against likely source worktrees if relevant
3. if the file is not part of any open PR worktree and the change is just local procedural residue, restore it instead of preserving it as meaningful repo work:

```bash
git restore --worktree -- <path>
```

Practical rule:
- do not let a stray local skill/doc edit block `main` fast-forward during workspace cleanup
- but only restore it when it is clearly not the active subject of an open PR or a kept dirty worktree

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
- clean detached helper clones that exactly match an open PR remote head are stale and removable
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

### Additional practical case: root staged residue copied from a merged detached helper worktree

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

## 7c. Repo-internal worktree directories can leave root `?? .worktrees/` noise

Some repositories keep linked worktrees under a repo-internal directory such as `.worktrees/<name>`.
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

## 8. Update local main safely

Important practical case: the current/root checkout itself may still be sitting on a stale merged PR branch.
In that case, workspace cleanup should not stop at pruning sibling worktrees; switch the root checkout back to `main`, fast-forward it, then delete the old current branch only after you are no longer on it.

Decision rule:
- if the current branch is already `main`, fast-forward `main` normally
- if the current branch is a stale merged/closed-PR branch or otherwise an obviously disposable branch and the root worktree is clean, first check out `main`, then fast-forward `main`, then delete the old branch
- if the current branch has real local work, preserve it and report instead of switching blindly

Typical commands:

```bash
git checkout main
git merge --ff-only origin/main
```

If `main` is not checked out in any worktree, you may also update it directly:

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

## 9. Final verification

Run:

```bash
git rev-parse main
git rev-parse origin/main
git branch --show-current
git worktree list
```

Also report remaining dirty worktrees explicitly so the user can decide on follow-up cleanup.

## Recommended reporting format

Report:
- target repo used
- whether `main` now matches `origin/main`
- number of worktrees removed
- branches deleted
- remaining dirty worktrees
- anything preserved intentionally for safety

## Practical lessons

- In a large multi-worktree repo, most safe wins come from removing clean detached review/rebase/squash worktrees first.
- Dirty worktrees often contain half-finished or forgotten work; preserve them by default.
- `git fetch --prune` can make many upstreams appear "gone"; do not treat that alone as permission to delete local branches.
- If the workspace root is not a repo, repository discovery is a prerequisite, not an optional convenience.
