# Recover local uncommitted content after its PR branch was merged/deleted

Use this when a local checkout is still on a feature/content branch with uncommitted edits, but `git fetch --prune` shows the upstream head branch is gone and `gh pr list/view` shows the associated PR is already merged.

## Why this matters

Do not revive the deleted merged PR branch as the review target. The old branch may contain pre-merge commits that are no longer useful by SHA, while the uncommitted local diff may still represent new content that should become a fresh PR on latest `origin/main`.

## Safe sequence

1. Fetch and classify the old branch/PR:
   - `git fetch origin --prune`
   - `git status -sb`
   - `env -u GITHUB_TOKEN gh pr list --head <branch> --state all --json number,state,mergedAt,headRefName,baseRefName,url,title`
2. Save the uncommitted local diff outside the repository:
   - `git diff -- <touched-files> > /tmp/<topic>.patch`
   - Run `git diff --check` and note whitespace issues before rewriting the worktree.
3. Preserve the old local branch tip before destructive cleanup:
   - `git branch backup/<old-branch>-before-main-refresh-$(date +%Y%m%d%H%M%S) HEAD`
4. Reset the old checkout and create a fresh branch from current main:
   - `git reset --hard HEAD`
   - `git switch -C <new-branch> origin/main`
5. Reapply only the saved local diff:
   - `git apply --3way /tmp/<topic>.patch`
   - Resolve conflicts by treating latest `origin/main` as the base and applying only the still-intended content updates.
6. Verify before commit:
   - `git diff --check`
   - Narrow conflict-marker grep on the touched files: `git grep -n -E '^(<<<<<<<|=======|>>>>>>>)' -- <touched-files> || true`
   - Compare the final diff against `origin/main` to confirm only intended files remain.
7. Commit, push, create/update a new PR from the fresh branch.

## Content localization follow-up

For MDX content repos with mirrored `src/content/{ko,en,ja}/...` files, if the local KO change comes from Confluence Space synchronization and the user asks for a PR, check sibling EN/JA files before finalizing. Apply equivalent build-tag/date/product-name changes and translate short list labels consistently rather than opening a KO-only PR.
