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
- After repairing a PR branch by rebase/conflict resolution/force-push, perform a final remote sanity check before reporting done: compare `gh pr view --json headRefOid,mergeStateStatus,statusCheckRollup,state,closed`, `git ls-remote origin refs/heads/<head-branch>`, local `git rev-parse HEAD`, `git merge-base HEAD origin/main`, `git rev-parse origin/main`, and `git rev-list --oneline origin/main..HEAD`. Report whether any `BLOCKED` state is due to pending checks rather than remaining conflicts.
- No-op rebase/open-PR guard: if conflict resolution determines every PR delta is stale, duplicate, or invalid and the resolved branch becomes identical to the base branch, do **not** force-push a head equal to base when the user did not explicitly ask to close the PR. GitHub can auto-close a PR whose head and base become the same, and may refuse to reopen it while there is no head/base difference. To preserve the open review thread, create a code-change-free empty commit on top of the latest base before pushing (for example `git commit --allow-empty -m "chore: keep PR branch open after rebase"`), then push, update the PR body to state `changedFiles/additions/deletions = 0/0/0`, and explain that the original code delta was dropped as duplicate or invalid. See `references/no-op-rebase-pr-auto-close.md`.
- If latest `origin/main` already contains the original PR's main change because a sibling/replacement PR merged first, classify the original PR as `not valid as-is` even if the idea was valid. When the user asks to keep using the PR, do not close it by default; reset/rebase the existing PR branch onto latest `origin/main`, implement only a true follow-up delta, force-push with lease, and rewrite the title/body around the new scope. Verify the new branch has `merge-base == origin/main` and only the intended commit(s) via `git rev-list --oneline origin/main..HEAD` before pushing.
- When a PR claims live/parity compatibility by changing an internal route-local data contract (for example replacing semantic keyword filter keys with upstream numeric query IDs), validate whether the issue/user intended that internal contract to remain stable. Separate external URL/query compatibility from the internal source-of-truth model: a compatibility layer may normalize legacy/live query values, but that does not justify rewriting meaningful local identifiers into opaque numeric IDs unless explicitly requested.
- When a narrow PR touches a shared component or shared data contract to make one page/route work, treat that as a scope-validity checkpoint rather than a harmless implementation detail. Verify whether the route can handle the behavior locally instead; if the shared change is genuinely the desired new contract, require the PR title/body and tests to state that broader contract explicitly. Example pattern: a route-local MDX migration that changes a shared `ArticleFileImage` fallback for `public/*` assets may be technically correct for hero rendering, but it is over-scoped unless the PR is intentionally also adding local-public-image support to shared article rendering.
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
  - when a repo-local skill index exists (for example `.agents/skills/README.md`), compare it against the actual skill directories after any skill add/rename; adding a new skill must not accidentally remove an existing sibling skill from the index
  - flag any doc/skill change that silently turns a path-only refactor PR into a false source-of-truth change for content naming or architecture contracts
  - if docs say a route shape such as `/:id/:slug`, verify it against the actual route file path and route helper output; category-subcollection routes commonly require `/:category/:id/:slug`
  - if migration/status docs say `In PR`, `Current PR`, `until this PR merges`, or mention the PR number as the current state, decide whether that text will become stale immediately after merge; prefer merge-stable phrasing like `Implemented by PR <n>` or `implemented in this migration` unless the document is intentionally a temporary review note
  - if the PR body claims an internal implementation detail (for example recursive scanning or routeSegments support), check the actual diff for that module; flag misleading PR descriptions separately from implementation correctness
  - if the PR renames or mirrors test files, also inspect repo-local skills and guidance that cite those exact test paths; stale test-path examples are a real regression in repos that rely on checked-in skills as operational guidance
- Treat this as a real PR-validity issue, not a minor doc nit, when the changed skill/doc would teach future agents to use nonexistent paths or regressed conventions.
- When reviewing or fixing docs/skill index changes, separate an index omission from a conceptual contract replacement. If a concrete file such as `.agents/skills/manuals-posting/SKILL.md` still exists while README now lists only a newly added sibling such as `tutorials-posting`, say the existing family was omitted from the index and restore both entries; do not describe the new family as replacing the old one unless the implementation actually removed or remapped the old family.
- When PR follow-up feedback challenges a shared component or layout change, treat that as a scope-validity signal, not just an implementation nit. First look for a content/frontmatter/route-local fix that removes the shared diff entirely. Example pattern: for a repo-local MDX sample article whose shared ArticleLayout hero image would require changing ArticleMain or ArticleFileImage, prefer hiding the shared hero and rendering the local public image inside the route-local MDX body, then verify the shared component files disappear from `gh pr diff --name-only`.
- For follow-up fixes on an open PR after review, verify whether the PR branch is already checked out in another worktree. If Git rejects checkout with `fatal: '<branch>' is already used by worktree ...`, switch to that worktree instead of creating a detached/parallel branch. If it is in an accidental merge/conflict state, preserve intended edits externally, abort/reset the merge state, rebase onto latest `origin/main`, resolve conflicts, and force-push with lease so the PR remains linear.
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
- Reference-implementation port completeness rule:
  - when a PR claims to port or align with another repository/component implementation, do not audit only top-level markup or style/class names
  - compare the full implementation contract: runtime interactions, client components/hooks, nested helper components, required public assets, icon dependencies, scroll/focus/active states, share/copy behavior, and data-model adaptations
  - if only className/style structure was copied while interactive components or assets were left behind, classify the PR as incomplete even if the visual shell superficially matches
  - when fixing an existing PR after this finding, update the same PR branch and PR body to state exactly which reference files/contracts were ported
- Shared-component scope-drift repair rule:
  - when a follow-up fix changes a shared component only to make one migrated page or content item work, first ask whether the data/frontmatter value or the nearest route/layout seam is the real bug
  - for repo-local `public/**` assets referenced from MDX frontmatter, prefer storing the browser-facing public URL form such as `/family/id/image.png` in fields that render directly, rather than widening a remote/blob-oriented image component to understand `public/...`
  - verify which render path owns the failing surface: MDX body component overrides may not affect frontmatter-driven hero/og images rendered by article/layout components
  - if a shared component change is not required after narrowing the fix, remove it from the PR diff and update the PR body so it does not claim a broader contract change
- Metadata/content parity PR review rule:
  - verify metadata claims against the live rendered HTML, not only route-local source. Extract `document.title`, `meta[property="og:title"]`, and `meta[name="description"]` for each affected locale.
  - compare exact strings, including punctuation and separators. Example pitfall: Japanese title `QueryPie AI: 認証` is not equivalent to `QueryPie AI 認証`.
  - separate production-parity fixes from independent content corrections. If production has the same bad visible copy as stage, do not describe the change as parity; classify it as a content correction and update the PR body accordingly.
  - when latest `origin/main` already contains part of the PR's claimed fix, reset/rebase the PR branch onto latest main and keep only the remaining true delta. Refresh tests, title, and body so the PR does not keep claiming already-merged EN/KO or unrelated changes.
  - for card/list content fixes, update the relevant test mock so it renders the changed fields (not only labels). A test that mocks cards as labels-only cannot catch description regressions such as an ISMS-P card accidentally duplicating ISO 22301 copy.
- CTA/chrome text-style PR review rule:
  - when a PR claims it aligns header, GNB, drawer, or marketing CTA text, do not accept source class changes or screenshots alone
  - measure the live/reference and PR Preview computed styles for both the clickable wrapper and the visible text span at the same viewport; compare exact `font-size`, `font-weight`, `line-height`, `color`, wrapper dimensions, padding, gap, and mobile drawer height
  - check whether latest `main` moved the owning header/chrome primitive; if the PR edits stale pre-refactor clone files, classify it as not valid as-is even if the old Preview still deploys
  - treat changes such as reference `font-weight: 400` / `#f6f6f6` to PR `font-weight: 500` / `#fff` as a regression unless the reference computed values prove that is the desired contract
  - prefer preserving/reusing the shared CTA primitive (`ButtonLink`, `StaticButton`, or header-specific primitives) over one-off Tailwind utility edits like `font-medium text-white`
- Sibling-repo reference / Tailwind migration PR review rule:
  - when a PR claims it copied or aligned with a sibling repository implementation, inspect the exact referenced source file and compare it against the PR head, not only the PR description.
  - then compare the PR head against the target repository's pre-existing UI contract: design tokens, CSS variables, global resets, asset paths, component primitives, interaction behavior, and route/link conventions.
  - flag mechanical className copying as a validity risk when it replaces target-repo semantic tokens with sibling-repo hardcoded colors, Tailwind default palettes, or spacing assumptions.
  - check copied asset references explicitly in the target repository's `public/` tree. A source-repo asset path that does not exist in the target repo is evidence that the implementation was not properly ported.
  - distinguish `source was referenced` from `source was properly adapted`. A PR can truthfully mirror many classes from the source repo while still being invalid because it changes target-repo UI behavior or breaks target assets.
- Important "check not completed yet" investigation pattern for PRs with deploy checks:
  - do not conclude too early from a `pending` PR check; first inspect whether the PR head was just updated and a replacement run has only just started
  - compare PR `updatedAt`, head SHA, and the current workflow run `createdAt`/`status` before calling the check stuck
  - if the new run is genuinely active, poll once briefly and then inspect the failing step instead of reporting only `still pending`
  - for GitHub Actions jobs that succeed through `actions/checkout` but fail inside an external deploy step, separately verify whether the downstream deploy system expects a live remote branch ref rather than the PR merge ref
  - concrete failure signature: Actions checks out `pull/<number>/merge` successfully, but the deploy step retries after a deleted/cancelled preview deployment and then fails with Vercel `incorrect_git_source_info` saying the requested branch or commit reference does not exist
  - in that case, verify the remote branch directly with `git ls-remote origin refs/heads/<head-branch>`; an empty result means the PR can still exist while the branch ref required by the deploy system is gone
  - classify that as an external preview-deploy input/reference failure, not as a repository checkout or test failure
- Metadata / live-parity PR review pattern:
  - when a PR claims to align page metadata with production, verify the exact rendered `<title>` and `og:title` on the live production URL, not only the PR body or source title strings
  - punctuation and separators matter: examples like `QueryPie AI: 認証` vs `QueryPie AI 認証` are not equivalent for parity
  - compare current stage, latest `origin/main`, and the PR head separately; if stage/main already contain part of the fix, classify that part as duplicate/stale rather than treating the whole PR as newly valuable
  - distinguish `production parity` changes from independent content corrections. If production has the same wrong body/card text, do not cite production parity as evidence; frame the change as a content bug fix and seek/source a canonical wording
  - inspect the matching route-local/source tests. A metadata PR that updates title strings but leaves tests expecting old titles is not valid as-is even when the runtime change is conceptually right
  - session detail: see `references/metadata-parity-pr-review.md`

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
