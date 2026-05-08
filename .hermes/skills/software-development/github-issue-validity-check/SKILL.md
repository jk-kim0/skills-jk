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

When the user asks not just whether an issue is valid, but to rewrite the issue so it reflects the current state of the latest `main` branch:

1. Read the current issue body with `gh issue view <number> --json title,body,state,url`.
2. Inspect `origin/main`, not the current feature branch.
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
- For SEO/readiness issues specifically, verify both the existence of metadata route files (`src/app/robots.ts`, `src/app/sitemap.ts`) and whether related PRs are still open before calling the work missing or in-flight.
- For route-specific SEO activation issues (for example a newly public `/news` surface), do not stop after confirming the list/index route exists. Check all three layers separately for both the list page and representative detail pages: (1) page metadata/canonical, (2) robots index/follow behavior, and (3) sitemap inclusion. Then, if a hosted stage/prod target is available, confirm the raw HTML and `sitemap.xml` with `curl` so you can distinguish "list page launched" from "detail pages still noindex" and report a precise partial-validity verdict.
- When reviewing all open issues in a repo, first fetch a single latest `origin/main` baseline and reuse it for the whole pass. Then classify each issue into: still valid, partially valid / body stale, or effectively fixed / stale. This is especially useful for long-lived cleanup issues whose body names old file paths. Verify the exact cited paths still exist before trusting the issue scope; if the files are gone or moved but the underlying problem remains, recommend rewriting the issue body instead of simply closing it.
- For content/link-audit follow-up issues, re-check whether the underlying implementation model still exists on latest `main` before doing deep URL triage. A common stale pattern is that an issue still talks about broken `redirectUrl` targets, but the current main branch has already switched those items to fully local detail pages with source links in-body. In that case, the issue is often effectively fixed or obsolete even if the old body still lists bad external URLs.

## Output Style

Keep the conclusion concise and explicit:
- "Valid on latest main"
- "Fixed on latest main"
- "Partially valid"

Then include short evidence bullets.
