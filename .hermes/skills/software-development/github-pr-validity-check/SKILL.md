---
name: github-pr-validity-check
description: Validate whether an open GitHub PR is still a clean, reviewable, merge-worthy PR against the latest base branch, especially when scope drift or stale approvals may exist.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, pull-request, review, validation, scope, stale-approval]
    related_skills: [github-code-review, github-issue-validity-check]
---

# GitHub PR Validity Check

Use this when the user asks questions like:
- "Is this PR still valid?"
- "Can this PR be merged as-is?"
- "Please review whether this PR still makes sense"

This is not a full code-quality review only. It is a PR-level validity audit against the latest base branch.

## Goal

Answer one of these with evidence:
- valid and mergeable as-is
- partially valid, but should be updated or split
- not valid in its current form

## Workflow

1. Read PR metadata first.
   Prefer `gh pr view <number> --repo <owner/repo> --json ...` and capture:
   - title
   - body
   - head branch
   - base branch
   - state / draft state
   - mergeStateStatus
   - reviewDecision
   - commits
   - changedFiles / additions / deletions
   - URL

2. Check checks and review state.
   - Run `gh pr checks <number> --repo <owner/repo>`.
   - Inspect reviews with `gh api repos/<owner>/<repo>/pulls/<number>/reviews`.
   - Compare the approved review commit SHA against the current PR head SHA.
   - If approval was given on an older commit and the head advanced afterward, treat that approval as stale for reasoning purposes even if GitHub still shows an approved state.

3. Compare the PR scope against its stated purpose.
   - Get changed file names with `gh pr diff <number> --name-only`.
   - Ask whether the actual files match the PR title/body.
   - Flag scope drift when a PR titled as one concern (for example image optimization) also contains unrelated concerns (for example font-system rewrites, infra changes, or refactors).

4. Evaluate latest-base compatibility.
   - Fetch latest remote base branch.
   - Check whether the PR is cleanly mergeable against the current base, not against stale local state.
   - Prefer fetching the PR branch locally:
     ```bash
     git fetch origin pull/<number>/head:pr-<number>
     ```
   - Compute merge-base against latest base and inspect:
     - `git merge-base pr-<number> origin/main`
     - `git diff --stat <merge-base>..pr-<number>`
     - `git merge-tree <merge-base> origin/main pr-<number>`
   - If `mergeStateStatus` is dirty or merge-tree shows conflicts, do not treat the PR as merge-ready.

5. Check whether latest main already changed the same contract.
   This is especially important for layout, fonts, routes, metadata, tests, and shared infra.
   - Read the latest files from the repo on current `origin/main`.
   - Inspect commits on `origin/main` since the PR branch diverged for the touched files.
   - If latest main already landed a different fix for the same area, treat the PR as potentially stale or contradictory even when some parts remain useful.

6. Separate "idea validity" from "PR validity".
   A PR can contain a good idea but still be invalid as a merge target.
   Distinguish between:
   - the underlying improvement is sound
   - the current PR branch is stale, conflicted, over-scoped, or misleadingly described

7. Produce a crisp verdict.
   Use one of:
   - Valid as-is
   - Partially valid
   - Not valid as-is

## Evidence checklist

For the verdict, gather several of:
- PR metadata from `gh pr view`
- check status from `gh pr checks`
- reviews from GitHub API or gh
- changed-file list / diff summary
- mergeability evidence vs latest base
- current-base file contents and relevant recent commits

## Practical patterns learned

- A PR can show `APPROVED` while the approval is effectively stale if it was submitted on an older commit and additional commits were pushed later.
- If the PR title/body claims one narrow purpose but the diff includes a second concern, call out the mismatch explicitly.
- When a newer main-branch fix already defines the current contract for shared files, a PR that reworks the same area under a different approach should not be treated as straightforwardly valid.
- "The idea is good" is not enough. Separate whether the proposed improvement should exist from whether this specific PR should merge.
- For asset optimization PRs, it is common for the optimization itself to be valid while the branch becomes invalid because unrelated changes were bundled later.
- For dead-code-removal PRs, do not trust old assumptions about "unused" branches. Re-validate both runtime references and real content/data markers on latest main. Example pattern: search the current source tree for imports/usages, then search the real content corpus for markers that activate the branch (for example HTML wrapper markers). A branch is only a good removal target when both the code references and the activating data markers are absent or can be safely narrowed.
- If only part of a stale PR remains valid on latest main, salvage it by narrowing scope instead of forcing the original broader thesis. Reconstruct the still-valid subset on top of latest main, update the PR title/body to match the reduced scope, and treat the result as a rewritten PR rather than a mechanical rebase.
- When the PR changes repo-local skills, guidance docs, or AGENTS-style instructions, do not review those files only as prose. Validate every path/file-pattern claim against the real repository tree on the PR head and latest `origin/main`.
- Practical contract checks for doc/skill reviews:
  - search the live tree for the claimed file paths
  - verify whether filename conventions in the docs still match the actual corpus (for example `<id>-<slug>.mdx` vs `<id>.mdx`)
  - verify whether moved helper modules actually exist at the new documented paths
  - after a path-refactor PR, grep the PR head for old path strings to catch partial updates where one section was fixed but workflow/examples or companion skills still point at removed files
  - when one repo-local skill is updated for a moved path, inspect sibling/companion skills for the same stale references instead of assuming the update was applied consistently everywhere
  - flag any doc/skill change that silently turns a path-only refactor PR into a false source-of-truth change for content naming or architecture contracts
- Treat this as a real PR-validity issue, not a minor doc nit, when the changed skill/doc would teach future agents to use nonexistent paths or regressed conventions.

## Output style

Keep the answer concise and decisive:
- overall verdict
- 3 to 6 evidence bullets
- recommended next action

Example structure:

```text
Verdict: Partially valid

Evidence:
- PR head is not cleanly mergeable against latest main
- approval was left on an older commit; two newer commits changed the PR scope
- title/body describe image optimization, but the diff also rewrites the font pipeline
- latest main already landed a different font-contract fix in the same files
- the image optimization itself still looks beneficial

Recommended action:
- rebase or recreate from latest main
- keep only the image-related changes
- open a fresh PR for the narrowed scope
```
