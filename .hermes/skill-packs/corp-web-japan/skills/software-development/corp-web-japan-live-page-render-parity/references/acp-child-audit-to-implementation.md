# ACP child render audit to implementation follow-up

Use this note when a prior PR or README audit already documents live-vs-stage render gaps for several ACP child pages and the user asks for a new implementation PR.

## Pattern

1. Treat the audit PR as evidence, not as the implementation branch.
   - Inspect the PR files/body to identify the affected routes and gap taxonomy.
   - Create a fresh latest-`origin/main` worktree and a new implementation branch.
   - If the audit PR has already merged, branch from the merged latest main; do not continue on the old docs/audit branch.

2. Convert repeated findings into shared ACP primitives first.
   - For the four ACP child pages (`database-access-controller`, `system-access-controller`, `kubernetes-access-controller`, `web-access-controller`), repeated gaps such as hero background, FAQ placement, mobile heading scale, and CTA treatment belong in `src/components/sections/acp/static-page.tsx`.
   - Keep page-specific copy and section composition route-authored in each `src/app/t/platforms/acp/<route>/page.tsx`.

3. Verify live details directly before coding when the audit only summarized them.
   - Browser-extract the live pages for headings, section top/height, background-image/background-gradient, FAQ text, and CTA styles.
   - If Playwright's bundled browser is missing, launching the installed system Chrome with `executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"` is a practical read-only extraction fallback on this Mac setup.

4. ACP child live-page contracts observed in PR #562 work:
   - Hero section uses product-specific vertical gradients: DAC `#dfe8f2`, SAC `#e2e9e1`, KAC `#e8eaf4`, WAC `#dfeff2` around the 84% stop.
   - Live FAQ block appears before the final CTA and is shared across all four pages.
   - FAQ questions:
     - `QueryPie はSaaS サービスですか？`
     - `QueryPie はユーザー認証をどのように処理しますか？`
     - `QueryPie はどのようなセキュリティ標準を遵守していますか？`
     - `QueryPie は既存のセキュリティソリューションと互換性がありますか？`
   - Desktop H2/H4 sizes already matched in the local rebuild; mobile split-feature H4 needed `20px/28px` rather than the larger local value.
   - Feature-card titles should follow the live smaller H6-like card title contract rather than oversized local H3 styling.
   - CTA uses a blue-purple-pink gradient; keep the existing app link target unless the task explicitly changes CTA destination.

5. Test the contract at source level.
   - Extend `tests/src/app/t/platforms/acp/static-routes.test.mjs` to assert the shared FAQ, route-specific hero backgrounds, live-like mobile typography, CTA gradient contract, and continued route-authored JSX.
   - Run at least:
     - `node --test tests/src/app/t/platforms/acp/static-routes.test.mjs`
     - `npm run test:static-pages`
     - `npm run typecheck`
     - `npm run lint`

## Pitfalls

- Do not treat a docs-only render audit PR as a branch to continue for implementation. Use it as context and open a new implementation PR from latest main.
- Do not solve four sibling pages with four separate PRs when the user explicitly asks for one combined PR and the gaps are shared primitive-level defects.
- Do not patch each page with one-off spacing/classes when the evidence points to a shared ACP static-page primitive contract.
- Do not over-read live `section` counts; production nesting inflates counts. Convert only meaningful body differences such as missing FAQ, missing hero background, and typography/CTA contracts.
- Do not silently start a local dev server for visual checks; prefer source tests, direct live extraction, CI, and preview deployment unless explicitly requested.
