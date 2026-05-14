---
name: github-issue-validity-check
description: >
  Validate whether a GitHub issue is still valid against the latest main branch
  by reading the issue via gh, comparing the codebase against origin/main, and
  confirming runtime behavior when needed.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, issue-triage, validation, regression, main-branch, browser]
    related_skills: [requesting-code-review, systematic-debugging, github-code-review]
---

# GitHub Issue Validity Check

Use this skill when the user asks whether a GitHub issue is still valid on the
latest `main` branch, especially for UI/behavior bugs.

## Goal

Answer one of these with evidence:
- the issue is still valid on latest `main`
- the issue is already fixed on latest `main`
- the issue is partially valid / ambiguous and needs clarification

## Workflow

1. Read the issue details from GitHub.
   - Prefer `gh issue view <number> --repo <owner/repo> --json ...`.
   - If the browser page is 404, do not assume the issue is inaccessible; use `gh`.

2. Check the repo state.
   - Confirm branch and remote.
   - Compare the current code against `origin/main`.
   - Explicitly check whether the local `main` is behind `origin/main`; do not
     evaluate issue validity from a stale local branch.
   - If the user asked about "latest main", inspect `origin/main`, not the
     current worktree branch.
   - Read the latest `origin/main` commit hash and recent commit log first.
     An issue body may already contain a prior re-audit that is stale by a few
     commits, so do not assume the current issue text is still accurate.
   - When you need to run tests or inspect files exactly as they exist on latest
     `main`, create a temporary worktree at `origin/main` instead of relying on
     the current checkout.
   - If the local checkout shows the issue but `origin/main` does not, treat
     that as a stale-local-state problem first, not as fresh evidence that the
     issue is still valid.
   - When the user is working directly on the repo root `main` branch and asks
     to sync it, prefer `git pull --ff-only origin main` so local inspection and
     future edits match the already-verified latest main state.

2.5. Check for already-open PRs that may partially or fully address the issue.
   - Use `gh pr list --state open --repo <owner/repo>` and inspect any PRs with
     matching issue numbers, scope, or titles.
   - If an open PR already addresses part of the issue, distinguish between:
     - already fixed on latest `origin/main`
     - in progress on an open PR but not yet merged
     - still remaining even after those changes
   - This helps avoid reporting merged fixes as still open or treating pending PR
     work as already complete.
   - When the user asks what should happen next, explicitly exclude scope already
     covered by open PRs from the recommended action list.
   - For each remaining item, group it into:
     - blocked on a product/content decision
     - implementation-ready
     - follow-up / lower-priority cleanup
   - Prefer implementation priority based on launch/user impact:
     1. broken or fake conversion paths / core CTAs
     2. visible public navigation defects
     3. SEO/discoverability baseline
     4. regression tests / quality gates
     5. optional cleanup and dead-code removal

3. Inspect the code paths implicated by the issue.
   - Search for relevant components, styles, helpers, and routes.
   - Read the files that likely control the behavior.
   - Compare the relevant files to `origin/main` when needed.
   - If the issue names a specific file or surface and that exact file is already fixed on `origin/main`, do not stop there: search the broader repository for the same broken pattern (for example remaining `href="#"` placeholders, duplicate legal links, or equivalent UI text in another component).
   - Distinguish between:
     - the exact issue symptom already fixed in the named file
     - the broader class of problem still present elsewhere
     - a nearby remaining issue that is worth fixing in the same PR even if the original file is no longer the culprit

4. Verify runtime behavior when the issue is visual or interactive.
   - Start or reuse the local app if necessary.
   - Use the browser to inspect the live page.
   - Check computed styles or DOM behavior when the issue is about cursor,
     hover, visibility, layout, interaction, or text rendering.
   - For issues phrased as "public" or "visible" problems, confirm the affected
     surface is actually exposed on latest `origin/main`.
     - If the relevant index/page currently returns `notFound()` or is otherwise
       hidden, do not treat the problem as an active public-surface bug on main
       unless another reachable surface still exposes it.
     - Then inspect open PRs that may restore/re-expose that surface soon, and
       call out the distinction explicitly: not public on current main vs likely
       to become public if a specific PR merges.

5. Decide validity.
   - If the code clearly matches the issue and the live page reproduces it,
     mark it valid.
   - If the current `main` branch already fixes it, mark it invalid on main.
   - If one symptom is fixed and another remains, call it partially valid.

## Evidence Checklist

For a valid/invalid verdict, gather at least one of:
- issue text from `gh issue view`
- code evidence from `read_file` / `search_files`
- diff evidence against `origin/main`
- live browser evidence (DOM snapshot or computed style)

## Pitfalls

- A GitHub issue URL may show a generic page or 404 in the browser.
  Always fall back to `gh issue view`.
- The current branch may differ from `main`; do not judge validity from the
  current branch unless the user explicitly asks about it.
- In multi-worktree repos, `npm run test:ci` or `eslint` from the main checkout
  can be polluted by sibling worktree `.next` or generated files. If lint fails
  on unrelated generated artifacts outside the latest-main source snapshot, do
  not treat that as issue evidence against latest `origin/main`.
- When that pollution happens, verify latest-main validity with a cleaner split:
  source inspection against `origin/main`, `npm run test`, and `npm run build`.
  If you create a temporary worktree for isolation, remember it may not have
  dependencies installed, so missing `next`/`eslint` there is an environment
  limitation rather than product evidence.
- Issue comments may mention staging-only or branch-local fixes that have not
  landed on `origin/main`; verify those claims against the actual `origin/main`
  files and tests before narrowing or closing the issue.
- Visual issues often need live browser verification; source code alone may be
  insufficient.
- Text-cursor vs pointer behavior can be a browser default, not a code bug.
  Confirm the computed cursor on the element before concluding.

## Rewriting an issue to match latest `main`

When the user asks to "update" an existing GitHub issue, treat that as an issue-rewrite task, not as a request to add a comment or provide a chat summary. The expected action is to verify whether the issue goal is achieved on the latest `main`, identify what changed, preserve the existing issue sections as much as possible, and rewrite the actual issue body so it reflects current truth.

Language rule for issue rewrites: preserve the existing issue body's language by default unless the user explicitly asks for another language or bilingual format. If the issue is currently Korean, rewrite in Korean; if it is English, rewrite in English. Do not apply repo-internal PR/doc language rules to the issue body unless the user asks for them.

When the user asks not just whether an issue is valid, but to rewrite the issue so it reflects the current state of the latest `main` branch:

1. Read the current issue body with `gh issue view <number> --json title,body,state,url`.
2. Note the existing language and section structure before drafting; keep headings/sections where still meaningful, and only remove or reshape stale sections when latest-main evidence makes them invalid.
3. Inspect `origin/main`, not the current feature branch.
   - Prefer a detached worktree from `origin/main` if the current branch has stacked PR changes or other in-flight edits.
3. Compare the issue's original intended scope against the current implementation.
4. Split the rewrite into three buckets:
   - already completed on latest `main`
   - still remaining on latest `main`
   - notes / source-of-truth references
5. If the original issue was written as a planning document but the work is now done, rewrite it as a current-state document instead of preserving stale audit tables.
6. If part of the issue is already complete and part remains, narrow the issue to the remaining scope instead of leaving the whole original checklist intact.
7. Write the replacement body to a temporary markdown file and update with `gh issue edit <number> --body-file <file>`.
   - Prefer `--body-file` over inline shell strings for markdown issue bodies.

### Practical patterns learned

- For repo-specific documentation or issue rewrites that must match latest `main`, create a detached worktree from `origin/main` and read files from that worktree. This prevents accidentally documenting feature-branch or stacked-PR state.
- When an issue has become partially obsolete, rewrite it around the latest truth:
  - mark completed items with `[x]`
  - keep only genuinely remaining work as unchecked scope
  - explicitly state which paths, routes, or link policies are already done on latest `main`
- For rollout/status issues, do not trust the old issue body's route-state description. Verify the exact current public URLs directly (for example with `curl -L` against both production and stage) and compare that with the latest-main files. A common stale pattern is: the issue still says a preview route like `/t/...` is active and `/public-route` still redirects, while latest `main` and live deploys have already switched the final public entry and the preview route now 404s.
- If the original issue was written as an implementation tracker but the rollout is already complete, narrow it into a current-state record instead of leaving obsolete "remaining work" sections in place.
- If the issue body's acceptance criteria no longer match the intended product policy, do not treat the stale issue text as the final source of truth. First verify the latest implementation on `origin/main`, then incorporate any clarified intended behavior from the user, rewrite the issue so the acceptance criteria match that final policy, and only then decide whether to close it.
- This matters especially for rollout issues where one acceptance criterion described a temporary or earlier plan (for example direct external redirects) but the final deliberately shipped behavior changed for reliability reasons (for example preferring stable local detail pages because external links break over time).
- When the user asks for a progress comment rather than a full rewrite, structure the comment as: (1) latest-main commit checked, (2) assumptions in the original issue that are no longer true, (3) concrete implementation now present with file paths, (4) regression/live evidence, and (5) a short conclusion on whether the issue is effectively complete or should be narrowed to follow-up scope.
- For navigation/link issues, replace speculative tables with a final implemented link policy once the work is merged.
- If you are reviewing a freshly edited issue body, re-fetch `origin/main` and re-check open PRs immediately before final judgment. In fast-moving repos, a PR can merge between the rewrite and the follow-up review, which can instantly stale statements like "no robots/sitemap implementation yet" or "PR #X is still open".
- Important latest-main issue-rewrite discipline: do not stop after checking only the issue text plus `origin/main`. Before editing the issue, explicitly fast-forward local `main` (or otherwise verify the exact latest `origin/main` baseline) and inspect all currently open PRs in the repository, then distinguish three buckets in the rewritten issue body:
  - already merged into latest `main`
  - still only present on open PRs and therefore not yet on `main`
  - unrelated open PRs that should not be cited as active follow-up for this issue
- If the issue body or comments name specific follow-up PR numbers, check those PRs directly with `gh pr view <n> --json state,mergedAt,mergeCommit,title,url,closedAt,body,comments` even when they no longer appear in `gh pr list --state open`. A PR disappearing from the open list often means it merged, but it can also mean it was closed without merge.
- If a named follow-up PR is `CLOSED` with `mergedAt: null`, inspect the PR closing comment/body before deciding what remains. A closed-unmerged PR may be an abandoned/rejected/mistaken implementation rather than work that should still be carried forward. Do not treat it as completed evidence, and do not automatically treat it as still-required work; compare the final issue scope, user corrections, and latest `origin/main` code to decide whether the underlying task is still valid.
- When a user corrects you for preserving a stale or wrong-scope remaining item, update the issue around the corrected scope boundary instead of defending the old parity/audit wording. In particular, do not keep a broad phrase like “final source parity” as remaining work if the concrete behavior belongs to a later public-rollout stage or if a PR implementing it was explicitly closed as wrong-scope. Reclassify it as out of scope / not a completion condition, and state the actual durable contract that remains.
- For preview-tracking issues, distinguish body/content/UI parity from public URL/query compatibility. A live site may expose legacy query parameters or route contracts that are useful to inspect, but they are not automatically requirements for a `/t/*` preview implementation unless the issue/user explicitly includes public rollout or backward compatibility in scope. Treat public URL/query compatibility as a separate rollout concern by default.
- Practical stale-issue pattern: an issue body may say PRs like `#424` / `#425` are still open follow-ups, but after a fresh `main` update those PRs may already be merged or closed without merge and disappear from the open-PR list. Re-checking every named follow-up PR plus every currently open PR before editing prevents writing a second stale body.
- For SEO/readiness issues specifically, verify both the existence of metadata route files (`src/app/robots.ts`, `src/app/sitemap.ts`) and whether related PRs are still open before calling the work missing or in-flight.
- For route-specific SEO activation issues (for example a newly public `/news` surface), do not stop after confirming the list/index route exists. Check all three layers separately for both the list page and representative detail pages: (1) page metadata/canonical, (2) robots index/follow behavior, and (3) sitemap inclusion. Then, if a hosted stage/prod target is available, confirm the raw HTML and `sitemap.xml` with `curl` so you can distinguish "list page launched" from "detail pages still noindex" and report a precise partial-validity verdict.
- When reviewing all open issues in a repo, first fetch a single latest `origin/main` baseline and reuse it for the whole pass. Then classify each issue into: still valid, partially valid / body stale, or effectively fixed / stale. This is especially useful for long-lived cleanup issues whose body names old file paths. Verify the exact cited paths still exist before trusting the issue scope; if the files are gone or moved but the underlying problem remains, recommend rewriting the issue body instead of simply closing it.
- For content/link-audit follow-up issues, re-check whether the underlying implementation model still exists on latest `main` before doing deep URL triage. A common stale pattern is that an issue still talks about broken `redirectUrl` targets, but the current main branch has already switched those items to fully local detail pages with source links in-body. In that case, the issue is often effectively fixed or obsolete even if the old body still lists bad external URLs.
- For documentation / convention-cleanup issues, do not stop after confirming that the originally named files or paths were fixed on latest `main`. Search the broader docs tree for stale historical examples that still mention deleted paths, imports, or component names. A common stale pattern is: the main cleanup landed (`src/content/home.ts` removed, convention doc updated), but a deeper guidance doc still embeds the old path in an anti-pattern example. In that case, rewrite the issue so the resolved implementation work is marked done and the only remaining scope is clarifying those historical examples as pseudo-code or explicitly historical.
- For UI/refactor cleanup issues that ask whether a repeated wrapper/class/config is a valid target, distinguish three cases before recommending implementation:
  1. true no-op/dead setting with no rendered effect
  2. visually necessary setting that is merely overexposed or repeated at the call site
  3. genuinely conflicting wrapper responsibility that changes layout semantics across variants
  Inspect the component definition plus every usage site on latest `origin/main`; compare outer wrapper responsibilities (background/full-width section) against inner content container responsibilities (max width, horizontal padding, vertical spacing). Do not label necessary layout classes as "unnecessary" just because they repeat. If the classes affect width/padding/spacing, frame the issue as "preserve UI while moving repeated layout contract into the primitive" rather than "remove unused CSS".
- When the user asks not only whether an issue is still valid but also asks you to break down the remaining work and produce a PR immediately, do not jump straight into implementation guesses from the old issue body. First re-audit latest `origin/main`, open PRs, and any already-merged follow-up PRs; then, if the issue has become a narrowed planning/tracking issue, create a small current-state memo PR that captures the remaining work buckets before starting code changes.
- A good pattern for that memo PR is:
  1. latest-main baseline commit checked explicitly
  2. items already completed on main
  3. real remaining tracks grouped by implementation class
  4. recommended PR sequence / ordering
  5. explicit non-scope items so the old umbrella issue does not re-expand
- In repos that already use `docs/plans/` for current-state implementation memos, prefer adding the issue breakdown there rather than burying the analysis only in a PR body or chat summary. This gives later follow-up PRs a stable latest-main reference point.
- When rewriting an issue to match latest `main`, do not assume only the body is stale. Re-check whether the title's scope is now wrong too.
  - Common pattern: the old title names a narrow surface such as `/t/*` or a temporary implementation phase, but latest `main` shows the same implementation has expanded to a broader shared family or a public route.
  - In that case, search the current repo for actual usage sites, then update both the title and body so the issue describes the current class of behavior rather than preserving obsolete scope in the heading.
  - Also re-check whether the old body's "remaining cleanup candidates" still exist on latest `main`; if the named wrapper/helper files are already gone, rewrite that section as completed historical context instead of carrying stale TODOs forward.
- For long-lived architecture / refactor audit issues, explicitly distinguish between:
  - migration / broad implementation work that is already effectively complete on latest `main`
  - narrow remaining taxonomy / naming / exception-handling questions
- Additional practical pattern for taxonomy / ownership issues on latest `main`:
  - do not keep the issue body at the level of abstract principles only
  - enumerate the actual current files on `origin/main` for the target directory with `git ls-tree -r --name-only origin/main <dir>`
  - split the current files into concrete buckets such as:
    - keep at root / shared
    - move into family subdirectories
    - orphan / revalidate before moving
  - for each root-level file, inspect real import/use relationships with repository search instead of relying on the filename alone
  - when the current tree already contains many family subdirectories, rewrite the issue as a latest-main cleanup / exception-reduction plan rather than as a greenfield taxonomy proposal
  - include explicit PR sequencing in the rewritten issue body: first the least controversial route-owned files, then shared-family boundary cases, then orphan / ambiguous survivors
  - if tests read source files by exact path, call that out in the issue body as part of the required follow-up so later implementation PRs do not miss path-sensitive test updates
- Practical stale-issue pattern learned from corp-web-japan issue rewrites:
  - an issue may still read like "we need to move `/t/*` pages into route-local authoring" even though latest `origin/main` already has most `/t/*` routes in route-local `page.tsx` + section-composition form
  - in that case, do not preserve the old issue as a generic migration-plan document
  - instead, rewrite it as a current-state reference that says the migration step is largely complete and narrows the remaining scope to concrete family decisions such as hero/title/lead primitive taxonomy, legal/document exceptions, or shell-width semantics
  - if a small set of thin routes remains, verify whether they are actual unfinished debt or intentional exceptions before keeping them as open work
- For CI / workflow issues, do not treat the mere presence of `workflow_dispatch` as evidence that the issue is complete. Read the actual workflow job steps and the package scripts they invoke. A common stale pattern is: a repo has a manually triggered generic CI workflow, but it still runs only lint/typecheck/unit tests while the issue requires a dedicated manually triggered E2E workflow. Verify whether the intended test class actually runs in GitHub Actions, whether it is still local-only by design, and whether the workflow targets the current branch / PR head the way the issue expects.
- For issue rewrites about path taxonomy, test layout, or CI gating, verify the current baseline in three places before preserving old TODOs: (1) the latest `origin/main` tree, (2) open follow-up PRs, and (3) the current shipped scripts/workflows such as `package.json` and `.github/workflows/*.yml`. A common stale pattern is that broad structural work is already merged on main, only a narrower test/helper follow-up PR remains open, and the old issue body still describes the whole migration as pending. In that case, rewrite the title/body around the actual remaining scope instead of keeping the original umbrella wording.
- Additional stale-issue pattern for test-taxonomy / CI issues: do not treat a large remaining count of root-level `tests/*.test.*` files as automatic evidence that the taxonomy migration is still broadly incomplete. Recount the files on latest `origin/main`, then separate them into (a) cross-cutting repository assertions that intentionally stay near the test root and (b) genuinely route-specific/source-coupled outliers that still should be mirrored under `tests/src/**`. This prevents issue bodies from carrying forward obsolete claims like "many root tests still need migration" after the mirrored structure has already landed for most route-owned tests.
- When narrowing a CI-gating issue after recent merges, explicitly verify whether the current `main` branch still has the gating machinery at all (for example `scripts/ci/**`, grouped node-test runners, changed-file assertions, workflow path filters). If the latest `main` still runs only a monolithic workflow job, rewrite the issue around refreshing/rebasing the still-open gating PR rather than implying that the already-merged taxonomy/helper groundwork remains the main unfinished work.
- Additional PR-state pitfall for latest-main issue rewrites: do not trust an open PR body that still says it is stacked on an older parent PR. Check the PR head SHA, merge-base against `origin/main`, and current checks directly. A PR can still describe itself as stacked in its body even after being rebased into a clean one-commit diff on top of latest `main`. In that case, rewrite the issue around the actual state: the work is implemented and reviewable on the open PR, but not yet merged into `main`.
- Additional umbrella-issue rewrite pattern: when the original issue describes a broad CI / taxonomy / rollout plan that has since mostly landed on `origin/main`, rewrite it as a current-state umbrella instead of preserving stale future-tense implementation prose.
  - Explicitly separate three buckets:
    1. already merged on latest `origin/main`
    2. implemented on open follow-up PRs but not yet on `main`
    3. genuinely remaining latest-main scope
  - If needed, update the issue title too so it reads as a current-state record rather than an old implementation plan.
  - Be careful not to mark open PR work as complete just because the follow-up PR exists; for a "latest main" rewrite, open-PR work still belongs in the not-yet-complete bucket.
  - This pattern is especially useful when the old body still says things like "single verify job always runs" even though latest `main` already has `paths-ignore`, changed-scope detection, shard test scripts, and conditional build execution.
- Practical file-presence check for latest-main issue rewrites: when the issue scope depends on whether specific files still exist on latest `origin/main`, do not rely on the local checkout if `main` may be stale.
  - Use `git cat-file -e origin/main:<path>` for exact existence checks on named files.
  - Use `git ls-tree -r --name-only origin/main <dir>` to recount files such as tests on the latest-main tree without creating a worktree.
  - This is especially useful for umbrella issues about test-taxonomy cleanup, where the real question is whether root-level outlier files are still present on `origin/main` and whether mirrored replacements now exist there.
- Additional fast-moving-issue pitfall: if you rewrite an issue, then the user asks again shortly after, re-check latest `origin/main` and open PR state from scratch instead of assuming your just-written issue body is still current.
  - In active repos, a couple of follow-up PRs can merge between turns and flip the correct framing from "merge pending on open PRs" to "already complete on latest main; close candidate".
  - When that happens, update both body and title accordingly so the issue stops reading like an active implementation tracker and instead becomes a completion-state record or close candidate.
- When rewriting an issue whose remaining scope is covered by open follow-up PRs, capture each PR's current mergeability and stacking state instead of only saying "open".
  - Use `gh pr view <n> --json baseRefName,headRefName,headRefOid,mergeStateStatus,statusCheckRollup,url`.
  - If a PR is stacked on another branch, state that it is not latest-main-complete until the base PR lands or the stack is rebased.
  - If `mergeStateStatus` is `DIRTY`, explicitly frame the next action as rebase/conflict resolution on latest `origin/main`; do not present the PR as ready-to-merge.
  - If the current checkout is dirty or behind, create a temporary detached worktree at `origin/main` for file inspection, then remove that worktree after updating the issue so local user edits are not disturbed.

## Output Style

Keep the conclusion concise and explicit:
- "Valid on latest main"
- "Fixed on latest main"
- "Partially valid"

Then include short evidence bullets.
