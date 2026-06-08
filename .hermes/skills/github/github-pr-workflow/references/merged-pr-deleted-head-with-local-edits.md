# Recover local edits after a PR was merged and its head branch was deleted

Use this when you are on a local branch whose GitHub PR has already been merged, the remote head branch was deleted, and the checkout still contains uncommitted edits that must be preserved on top of the latest `origin/main`.

## Why this matters

After a PR is squash/merge-committed, the local branch can diverge from the new `origin/main` even if most content is already merged. If the remote branch is gone, do not revive the old PR branch by default. Preserve the local edits, start a fresh latest-main branch, and open a follow-up PR.

## Recipe

1. Fetch and classify the branch/PR state.

```bash
git fetch origin --prune
git status -sb
env -u GITHUB_TOKEN gh pr list --head <branch> --state all --json number,state,mergedAt,headRefName,baseRefName,url,title
```

If the PR is `MERGED` and `git fetch --prune` removed `origin/<branch>`, treat the old branch as historical context only.

2. Save the uncommitted scoped diff outside the repo and make a backup branch at the current local HEAD.

```bash
PATCH=/tmp/<repo>-local-edits-$(date +%Y%m%d%H%M%S).patch
git diff -- <paths> > "$PATCH"
git diff --check -- <paths> || true
BACKUP=backup/<old-branch>-before-main-refresh-$(date +%Y%m%d%H%M%S)
git branch "$BACKUP" HEAD
```

3. Reset the stale checkout, create a new branch from `origin/main`, and apply the patch with 3-way merge.

```bash
git reset --hard HEAD
git switch -C <new-followup-branch> origin/main
git apply --3way "$PATCH" || true
git status -sb
git grep -n -E '^(<<<<<<<|=======|>>>>>>>)' -- <touched-paths> || true
```

4. Resolve conflicts by preserving the current main intent plus only the still-needed local edit. Remove whitespace issues and stage the resolved files.

```bash
git diff --check
# edit/patch files
git add <resolved-files>
git diff --cached -- <touched-paths>
```

5. Commit, push the new branch, and create a new PR. Do not update the merged PR or resurrect the deleted head branch unless the user explicitly asks.

```bash
git commit -m "<type>: <summary>"
git push -u origin HEAD
env -u GITHUB_TOKEN gh pr create --base main --head <new-followup-branch> --title "..." --body-file /tmp/pr-body.md
```

6. Verify remote head and checks are attached to the new SHA.

```bash
git rev-parse HEAD origin/<new-followup-branch> origin/main
env -u GITHUB_TOKEN gh pr checks <number> || true
env -u GITHUB_TOKEN gh run list --branch <new-followup-branch> --limit 5 --json headSha,status,conclusion,workflowName,url
```

## Content localization follow-up

For MDX content repos with mirrored `src/content/{ko,en,ja}/...` files, if the local KO change comes from Confluence Space synchronization and the user asks for a PR, check sibling EN/JA files before finalizing. Apply equivalent build-tag/date/product-name changes and translate short list labels consistently rather than opening a KO-only PR.

## Pitfalls

- `git apply --3way` labels sides from the current branch perspective; inspect the file content before choosing `ours` or `theirs`.
- Broad conflict-marker greps can false-positive on separator lines in unrelated files. For commit safety, use anchored marker regexes and restrict the final check to touched files.
- If a diff check reports only whitespace in the patch, capture the patch anyway, then clean it after applying on the latest-main branch.
- Keep a backup branch before resetting the old local branch so the pre-refresh state remains recoverable.