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
   - If the user asked about "latest main", inspect `origin/main`, not the
     current worktree branch.
   - Read the latest `origin/main` commit hash and recent commit log first.
     An issue body may already contain a prior re-audit that is stale by a few
     commits, so do not assume the current issue text is still accurate.
   - When you need to run tests or inspect files exactly as they exist on latest
     `main`, create a temporary worktree at `origin/main` instead of relying on
     the current checkout.

3. Inspect the code paths implicated by the issue.
   - Search for relevant components, styles, helpers, routes, and tests.
   - Read the files that likely control the behavior.
   - Compare the relevant files to `origin/main` when needed.
   - Check whether tests are encoding the old behavior as the expected outcome.
     For launch-readiness and regression issues, this often determines whether
     the issue is still truly open or whether the issue text is just outdated.

4. Reconcile the issue text with current `origin/main`.
   - If the issue body cites a specific commit, branch, staging-only fix, or
     prior audit date, verify each claim against the actual latest `origin/main`
     snapshot.
- If `main` has partially advanced, update the issue to reflect the new
  narrower scope rather than repeating the previous verdict.
- Call out mixed states explicitly, e.g. when `/contact-us` now exists and
  some CTA surfaces already use it, but other visible CTAs still point to
  `#contact` / `/#contact`.
- Do not assume every `#contact` is a defect. For long-form landing pages,
  verify whether the anchor intentionally scrolls to a designed bottom CTA /
  consultation section. If needed, click the CTA in a live local build and
  confirm the destination section, title, and surrounding design before
  treating the anchor as inconsistent.
- Verify each public surface separately. A repo may intentionally use
  different patterns by surface:
  - landing-page hero / floating CTA -> `#contact`
  - final CTA section -> `/contact-us?...`
  - sidebars on article/detail pages -> direct handoff or a local anchor only
    if the page actually contains that anchor target
- If a page uses `#contact`, confirm the target really exists on that page.
  A string-level grep is not enough; inspect the rendered route or DOM.
- If the destination section also contains a separate partner / transition CTA
  card to another page, record that separately instead of misclassifying the
  page's primary `#contact` flow as broken.
- When runtime verification is needed, prefer a local production-style check
  (`npm run build` + `npm run start`) if `next dev` or Turbopack shows cache /
  database instability in a temporary worktree.

5. Verify runtime behavior when the issue is visual or interactive.
   - Start or reuse the local app if necessary.
   - Use the browser to inspect the live page.
   - Check computed styles or DOM behavior when the issue is about cursor,
     hover, visibility, layout, interaction, or text rendering.

6. Decide validity.

3. Inspect the code paths implicated by the issue.
   - Search for relevant components, styles, helpers, and routes.
   - Read the files that likely control the behavior.
   - Compare the relevant files to `origin/main` when needed.

4. Verify runtime behavior when the issue is visual or interactive.
   - Start or reuse the local app if necessary.
   - Use the browser to inspect the live page.
   - Check computed styles or DOM behavior when the issue is about cursor,
     hover, visibility, layout, interaction, or text rendering.

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

## Output Style

Keep the conclusion concise and explicit:
- "Valid on latest main"
- "Fixed on latest main"
- "Partially valid"

Then include short evidence bullets.
