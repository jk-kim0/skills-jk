---
name: merged-pr-followup-workflow
description: Handle follow-up work requested against a pull request that is already merged or otherwise closed by creating a new PR from latest main instead of reviving the old branch.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, git, pr, follow-up, worktree, docs]
---

# Merged PR Follow-up Workflow

Use this when the user asks to "supplement", "polish", "fix", or otherwise follow up on a PR that is no longer open.

Typical trigger phrases:
- "PR 473을 보완해줘"
- "add one more fix on top of that PR"
- "follow up on the merged docs PR"

## Core rule

If the referenced PR is already merged or closed, do not treat it like an existing open-PR follow-up.

Do this instead:
1. Check the PR state first.
2. If the PR is `OPEN`, use the open-PR follow-up workflow instead.
3. If the PR is `MERGED` or `CLOSED`, start from the latest `origin/main`.
4. Create a fresh worktree and fresh branch.
5. Make the narrow follow-up change.
6. Open a new PR that references the earlier PR for context.

## Why this matters

Trying to reuse a merged PR branch creates confusion:
- the old PR cannot be updated meaningfully
- the branch may already be deleted remotely
- reviving the old branch can reintroduce stale ancestry or unrelated history
- reviewers need a clean, reviewable follow-up diff against current main

## Required discovery step

Always check the PR state before choosing the workflow.

Example:
```bash
gh pr view 473 --json state,title,url,headRefName,baseRefName,mergeStateStatus
```

Interpretation:
- `state: OPEN` -> continue on the existing PR branch/worktree flow
- `state: MERGED` or `state: CLOSED` -> create a new follow-up PR from latest main

## Recommended command flow

```bash
git fetch origin --prune
git checkout main
git pull --ff-only origin main
git worktree add .worktrees/<flat-name> -b <branch-name> origin/main
```

Then verify the fresh worktree base:
```bash
git -C .worktrees/<flat-name> branch --show-current
git -C .worktrees/<flat-name> rev-parse HEAD origin/main
git -C .worktrees/<flat-name> merge-base HEAD origin/main
```

For a fresh branch with no edits yet, those SHAs should match.

## PR body guidance

The new PR should mention the old PR as context, not as an update target.

Good pattern:
```md
## Summary
- add inline source links to the route-local terminology section

## Related context
- follow-up to PR #473
```

## Scope rule

Keep merged-PR follow-ups narrow.

This class of task is usually:
- docs wording/link cleanup
- one missed edge case
- one extra test
- one small reviewability improvement
- a small reconciliation after a sibling PR merged and changed the current contract

Do not silently widen it into a broad new batch just because you are already creating a new PR.

## Sibling-PR contract reconciliation

When the follow-up is prompted by comparing two already-merged PRs, inspect the latest `origin/main` state created by both merges before changing code. Do not reason from the older PR diff alone.

Recommended checks:

```bash
gh pr view <old-pr> --json state,mergeCommit,files,title,url
gh pr view <sibling-pr> --json state,mergeCommit,files,title,url
git fetch origin --prune
git ls-tree -r --name-only origin/main -- <candidate-paths>
git grep -n '<old-path>\|<new-path>' origin/main -- <relevant-src-dirs>
```

For shared asset follow-ups, distinguish page-specific route-aligned assets from shared asset corpora. If a sibling merged PR still uses the same logo/icon files from a shared root, prefer consolidating the shared root and deleting duplicate route-local copies rather than forcing every consumer into the first PR's route-local asset path. Example: company/customer logo SVGs used by both archived customers and archived customer-success pages belong in `public/company-icon/*`, while page-specific thumbnails can remain under a route/family-specific asset directory.

## Practical example from this session

A route-local documentation PR was already merged. The user then asked for additional source links to be inserted into the terminology section. The correct response was:
- verify the earlier PR was `MERGED`
- fast-forward local `main`
- create a fresh worktree/branch from latest main
- patch the docs only
- open a new follow-up PR referencing the earlier merged PR

## Pitfalls

- assuming "follow up on PR #N" always means update the same PR branch
- forgetting to check whether the referenced PR is already merged
- branching from stale local state instead of latest main
- describing the new PR as though it updates the old PR directly

## Done criteria

- PR state was checked explicitly
- merged/closed PRs were handled via a new branch and new PR
- the follow-up branch starts from latest main
- the new PR references the old PR only as context
- the resulting diff stays narrow and reviewable
