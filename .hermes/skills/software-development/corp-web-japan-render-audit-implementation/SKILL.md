---
name: corp-web-japan-render-audit-implementation
version: 1.0.0
description: Convert corp-web-japan browser-render parity audit findings into a fresh implementation PR, especially when the audit covers multiple sibling preview/static pages.
---

# corp-web-japan render-audit implementation workflow

Use this when a prior browser-render audit PR, README, or report already documents stage/live gaps and the user asks to implement the fixes in a new PR.

## Workflow

1. Treat the audit as evidence, not as the implementation branch.
   - Inspect the audit PR body/files to identify affected routes and repeated gap classes.
   - Start from latest `origin/main` in a fresh repo-root `.worktrees/<topic>` worktree.
   - If the audit PR is merged, do not continue on its old docs/audit branch.

2. Classify gaps before editing.
   - Shared primitive-level gaps: hero background, common FAQ section, shared CTA treatment, typography scale, card primitive semantics.
   - Route-local gaps: page-specific copy, section order, page-specific assets, unique feature bands.
   - Browser/chrome gaps: header/footer, cookie/language banner, production nested wrapper counts.

3. Implement repeated sibling-page gaps in shared section primitives first.
   - Keep route files as the authoring surface for page-specific copy and composition.
   - Avoid one-off route-level classes when the audit points to a shared family contract.

4. Verify live details directly when the audit summarized rather than quoted them.
   - Extract live headings, section geometry, background layers, FAQ text, and CTA styles with browser DOM/computed-style probes.
   - On this Mac setup, if Playwright's bundled browser is unavailable, a read-only extraction fallback is launching installed Chrome with:
     `executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`.

5. Add or update source-level tests that pin the converted contract.
   - Assert the shared primitive exports/classes/tokens.
   - Assert each affected route opts into the new contract and still owns its authored copy.
   - Run the narrow mirrored test, the relevant test group, typecheck, and lint.

## ACP child page example

When converting the ACP child render audit for DAC/SAC/KAC/WAC into PR #562:

- A single combined PR was correct because the user explicitly requested all four pages together and most gaps were shared primitive-level defects.
- Shared implementation target: `src/components/sections/acp/static-page.tsx`.
- Route-local implementation targets:
  - `src/app/t/platforms/acp/database-access-controller/page.tsx`
  - `src/app/t/platforms/acp/system-access-controller/page.tsx`
  - `src/app/t/platforms/acp/kubernetes-access-controller/page.tsx`
  - `src/app/t/platforms/acp/web-access-controller/page.tsx`
- Test target: `tests/src/app/t/platforms/acp/static-routes.test.mjs`.

Observed live contracts:

- Hero section uses product-specific vertical gradients:
  - DAC `#dfe8f2`
  - SAC `#e2e9e1`
  - KAC `#e8eaf4`
  - WAC `#dfeff2`
- Live FAQ appears before final CTA on all four pages.
- Shared FAQ questions:
  - `QueryPie はSaaS サービスですか？`
  - `QueryPie はユーザー認証をどのように処理しますか？`
  - `QueryPie はどのようなセキュリティ標準を遵守していますか？`
  - `QueryPie は既存のセキュリティソリューションと互換性がありますか？`
- Mobile split-feature heading should use the live smaller scale, about `20px/28px`, not the larger local rebuild value.
- Feature-card titles should follow the smaller H6-like live card title contract rather than oversized local H3 styling.
- CTA uses a blue-purple-pink gradient; keep the existing destination unless the task changes CTA behavior.

## Pitfalls

- Do not over-read live `section` counts; production nesting inflates them. Convert meaningful body differences instead.
- Do not start a local dev server by default. Prefer direct live extraction, source tests, CI, and preview deployment.
- Do not split a repeated shared primitive fix into multiple PRs when the user explicitly asks for one combined PR.
- Do not create issue-closing PR language for audit follow-ups; reference the prior PR/issue without auto-close keywords.
