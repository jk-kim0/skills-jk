# FDE hero lead width parity note

Session context: `/t/services/fde` stage page looked inconsistent after PR #542 and PR #544 aligned related AIP hero layouts.

Useful reference commits/PRs:
- PR #542 / commit `3a3a1b1`: AIP usage-based LLM widened hero lead to `max-w-[1000px]`, used `mt-[20px]`, and aligned hero visual spacing around `80px`.
- PR #544 / commit `2bc8826`: MCP Gateway copied the same hero lead pattern: `max-w-[1000px]`, `mt-[20px]`, `mt-[68px] lg:mt-[80px]` for the visual.
- PR #551 / commit `4c39b5d`: FDE adopted the same lead width contract.

Observed FDE browser measurements before the fix:
- Stage `https://stage.querypie.ai/t/services/fde`, desktop `1440x900`:
  - h1: `60px / 72px`, 144px tall
  - title-to-lead gap: `20px`
  - lead: `746px` wide, `112px` tall
  - lead-to-visual gap: `80px`
- Live `https://www.querypie.com/ja/solutions/aip/fde-services`, desktop `1440x900`:
  - h1: `60px / 72px`, 144px tall
  - title-to-lead gap: `20px`
  - lead: about `795.5px` wide, `84px` tall
  - lead-to-visual gap: `80px`

Conclusion:
- The mismatch was not hero title typography or vertical spacing; those already matched the live rhythm.
- The material defect was only the FDE lead max-width being too narrow (`746px`), causing extra wrapping.
- Minimal fix: update `ServiceFdeHeroLead` in `src/components/sections/fde/service-page.tsx` to `max-w-[1000px]` and pin that in `tests/src/app/t/services/fde/page.test.mjs`.

Verification used:
- `node --test tests/src/app/t/services/fde/page.test.mjs`
- `node scripts/ci/assert-test-groups.mjs`

Tooling note:
- If local Playwright exists but browser binaries are missing, do not spend time installing browsers for this small parity check. Use the Chrome DevTools MCP/browser session to collect `getBoundingClientRect()` and `getComputedStyle()` measurements on the exact stage/live URLs.
