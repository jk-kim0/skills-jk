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
- Important Next.js App Router nuance for route-file cleanup reviews: a file under `src/app/**/page.tsx` can still be live even when there are zero import references to it. Treat file-system-routed pages as runtime entrypoints first, not as ordinary modules. When reviewing a PR that removes logic from or deletes such a file, check four things separately on latest main: (1) whether the route file still exists as a public or legacy entrypoint, (2) whether any internal links still point at that route family, (3) whether sitemap/canonical helpers or route registries still emit that route or a replacement canonical route, and (4) whether tests still assert the route file's metadata/behavior. Zero imports alone is not evidence that the route is unused.
- If only part of a stale PR remains valid on latest main, salvage it by narrowing scope instead of forcing the original broader thesis. Reconstruct the still-valid subset on top of latest main, update the PR title/body to match the reduced scope, and treat the result as a rewritten PR rather than a mechanical rebase.
- When a PR claims live/parity compatibility by changing an internal route-local data contract (for example replacing semantic keyword filter keys with upstream numeric query IDs), validate whether the issue/user intended that internal contract to remain stable. Separate external URL/query compatibility from the internal source-of-truth model: a compatibility layer may normalize legacy/live query values, but that does not justify rewriting meaningful local identifiers into opaque numeric IDs unless explicitly requested.
- When the PR changes repo-local skills, guidance docs, or AGENTS-style instructions, do not review those files only as prose. Validate every path/file-pattern claim against the real repository tree on the PR head and latest `origin/main`.
- Important merge-readiness nuance: if GitHub shows `mergeStateStatus=BEHIND`, separate that from content validity. A PR can still be conceptually correct against latest main while not being merge-ready yet. In that case, inspect whether latest `origin/main` actually changed the same touched files or contract since the PR merge-base. If not, classify it as `content still valid, but branch refresh/rebase required` rather than stale/contradictory.
- Similar nuance for `mergeStateStatus=DIRTY`: do not stop at `not mergeable`. Fetch the PR head into a disposable local branch/worktree, actually rebase onto latest `origin/main`, and inspect the conflict class. If the only conflict is in a regression test that evolved on main while the PR merely removes an implementation branch, preserve the latest-main test additions and re-apply only the PR's intended deletion/update. If the rebased diff remains narrow and verification still passes, classify the PR as `content still valid, but branch refresh/conflict resolution required` rather than stale.
- Practical signal for that case: after rebase, search the tree for the supposedly removed branch/component/type markers and also search the content corpus or runtime data markers that would activate that branch. If both are absent on latest main, treat the conflict as integration churn unless latest main introduced a replacement contract.
- Practical contract checks for doc/skill reviews:
  - search the live tree for the claimed file paths
  - verify whether filename conventions in the docs still match the actual corpus (for example `<id>-<slug>.mdx` vs `<id>.mdx`)
  - verify whether moved helper modules actually exist at the new documented paths
  - after a path-refactor PR, grep the PR head for old path strings to catch partial updates where one section was fixed but workflow/examples or companion skills still point at removed files
  - when one repo-local skill is updated for a moved path, inspect sibling/companion skills for the same stale references instead of assuming the update was applied consistently everywhere
  - flag any doc/skill change that silently turns a path-only refactor PR into a false source-of-truth change for content naming or architecture contracts
  - if the PR renames or mirrors test files, also inspect repo-local skills and guidance that cite those exact test paths; stale test-path examples are a real regression in repos that rely on checked-in skills as operational guidance
- Treat this as a real PR-validity issue, not a minor doc nit, when the changed skill/doc would teach future agents to use nonexistent paths or regressed conventions.
- Important stacked-PR / CI-gating check for taxonomy and test-path refactors:
  - when a PR renames, mirrors, or deletes test files, do not validate it in isolation
  - inspect still-open or recently merged follow-up PRs that implement changed-file CI gating, path filters, or test-group membership
  - grep those branches/files for the old test paths
  - if downstream CI scope rules still reference only the pre-rename paths, classify the PR as at least partially incomplete even if the moved tests themselves pass
  - separate `the moved tests are correct` from `the repository's automation and guidance now point at the new locations`; both must be true for a clean validity verdict
- Practical PR-head file inspection rule:
  - when validating a PR, do not assume every changed file exists in the current root checkout on `main`
  - this commonly fails for new files added only on the PR head (for example new `scripts/ci/*.mjs` helpers) if you try to inspect them with a plain repo-root `read_file`
  - if a target file is missing on the current checkout, inspect it from the PR head explicitly with `git show origin/<pr-branch>:<path>` or create a fresh worktree directly from the PR branch before concluding the file is absent
  - use this especially for PRs that add new scripts, workflows, helper modules, or moved files not yet present on latest `main`
- Preview-deployment validation rule for implementation-vs-doc PRs:
  - do not assume a green Vercel Preview means the PR actually implements the route or page the user wants reviewed
  - first compare the PR diff against the claimed review target and confirm the branch changes runtime files for that route (`src/app/**`, `src/components/**`, `public/**`, tests as supporting evidence)
  - if the PR only changes docs/skills/guidance files, classify it as a docs PR even if Vercel produced a preview deployment URL
  - when the user asks for visual parity on a specific migrated route, open the exact preview route URL itself, not just the preview site root
  - if that exact route returns 404 / deployment-not-found / missing page, treat that as evidence that the PR is not a valid visual-implementation PR for the requested target
  - separate `preview exists` from `requested route is implemented in preview`; they are not the same thing
- Important "check not completed yet" investigation pattern for PRs with deploy checks:
  - do not conclude too early from a `pending` PR check; first inspect whether the PR head was just updated and a replacement run has only just started
  - compare PR `updatedAt`, head SHA, and the current workflow run `createdAt`/`status` before calling the check stuck
  - if the new run is genuinely active, poll once briefly and then inspect the failing step instead of reporting only `still pending`
  - for GitHub Actions jobs that succeed through `actions/checkout` but fail inside an external deploy step, separately verify whether the downstream deploy system expects a live remote branch ref rather than the PR merge ref
  - concrete failure signature: Actions checks out `pull/<number>/merge` successfully, but the deploy step retries after a deleted/cancelled preview deployment and then fails with Vercel `incorrect_git_source_info` saying the requested branch or commit reference does not exist
  - in that case, verify the remote branch directly with `git ls-remote origin refs/heads/<head-branch>`; an empty result means the PR can still exist while the branch ref required by the deploy system is gone
  - classify that as an external preview-deploy input/reference failure, not as a repository checkout or test failure

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
