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

But do not over-preserve branch-backed worktrees just because they are not perfectly clean. Some branch worktrees are effectively stale except for disposable helper files. Check for repo-local temp artifacts such as:
- `.tmp-issue-*.md`
- `.tmp-pr-body*.md`
- other one-off scratch markdown files clearly unrelated to source changes

If those temp files are the only dirt in an otherwise stale merged/non-open-PR worktree, treat the worktree as effectively clean stale residue and remove it after confirming no tracked source changes remain.

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

### Additional practical case: a local alias branch can equal the current open-PR head while the official local PR branch is stale

Sometimes the repository ends up with both:
- the official local PR branch name (for example `docs/publication-refactor-plan`)
- a local helper/alias branch name (for example `pr287-rewrite`)

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
- a later variant showed the official branch-backed worktree itself could be behind the remote open-PR head while detached helpers held newer commits; in that case, first clear disposable temp files from the official worktree if needed, then hard-reset the official clean branch worktree to `origin/<pr-branch>`, and only after that remove the detached helper clones

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

Practical rule:
- once cleanup starts deleting stale worktrees/branches, re-run `git fetch --prune`, re-check open PR heads, and re-check `git worktree list` before each new deletion batch if the repo is actively changing
- this matters in fast-moving repos where `origin/main` or PR heads can advance during the cleanup session itself
- after the cleanup batch, fast-forward the root `main` worktree to the latest `origin/main` when the root checkout is clean so the workspace ends in a refreshed baseline

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
