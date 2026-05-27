# FDE hero render parity note

Session reference: corp-web-japan PR #551, informed by PR #542, #544, and #548.

Use this when `/t/services/fde` or a sibling AIP detail/service preview page has a hero title/lead layout that looks inconsistent with the recently aligned AIP pages.

## Reference PR pattern

- PR #542 (`usage-based-llm`) established the key hero lead contract:
  - lead `max-w-[1000px]`
  - title-to-lead gap about `20px`
  - lead-to-visual gap about `80px`
  - feature/hero source tests should pin the layout tokens that were changed
- PR #544 applied the same `max-w-[1000px]` lead pattern to MCP Gateway and adjusted mobile/visual spacing.
- PR #548 further aligned MCP Gateway with the published usage-based LLM shell:
  - use `PlatformPageShell`
  - use `PlatformContentSection` with `pb-[120px] pt-[134px] lg:pt-[144px]`
  - title/heading `max-w-[800px]`
  - visual wrapper `mx-auto mt-[80px] flex max-w-[1200px] justify-center`
  - keep source tests in sync with the exact hero contract

## FDE finding

For `/t/services/fde`, stage already had the same title size and vertical rhythm as live, but the lead was too narrow.

Measured before fix at desktop `1440 x 900`:
- stage lead: `746px` wide / `112px` tall
- live lead: about `795.5px` wide / `84px` tall
- title-to-lead gap: `20px` on both
- lead-to-image gap: `80px` on both

Root cause:
- `ServiceFdeHeroLead` used `max-w-[746px]`, forcing an extra wrap compared with the live page and the newer AIP page pattern.

Applied fix:
- `ServiceFdeHeroLead`: `max-w-[1000px]`
- `ServiceFdeHeroTitle`: `mx-auto max-w-[800px]`
- update `tests/src/app/t/services/fde/page.test.mjs` to pin both title and lead contracts.

## Pitfall

Do not blindly change all hero spacing just because a user says the title/lead layout looks off. First measure title-to-lead and lead-to-visual gaps on stage/live. In PR #551 those gaps were already correct; only the width contract needed changing.
