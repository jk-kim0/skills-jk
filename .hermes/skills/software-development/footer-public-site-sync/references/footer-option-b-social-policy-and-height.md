# Footer Option B social policy + height measurement

Session-derived pattern from corp-web-app #865 / PR #884.

## Context

When Footer parity is framed as Option B, the intended source of truth is the newer Tailwind Footer social-link policy, and the legacy Footer should be brought forward to match it instead of trimming Tailwind back to legacy.

Observed Tailwind social set:

- LinkedIn: `https://www.linkedin.com/company/querypie-01/`
- Youtube: `https://www.youtube.com/@querypie`
- X: `https://x.com/querypie`
- Facebook: `https://www.facebook.com/querypie`
- Instagram: `https://www.instagram.com/querypie.ai/`

## Implementation pattern

1. Inspect all locale footer TSX modules before editing.
   - In the observed case, English and Japanese legacy footer modules already had the new set.
   - Korean legacy footer was the only stale locale: it still used `https://www.twitter.com/querypie` and lacked Facebook/Instagram.
2. Patch only the stale locale module when other locales are already aligned.
3. Add a source-level regression test that loops all supported locales and asserts:
   - `label="X" href="https://x.com/querypie"`
   - no `twitter.com/querypie`
   - Facebook link/icon present
   - Instagram link/icon present
4. Keep the PR issue reference non-closing (`Related issue - #...`), not `Closes`/`Fixes`.

## Height remeasurement lesson

For desktop Footer social links, do not assume increasing the number of social links necessarily explains a footer-height delta. In the observed implementation:

- legacy stage baseline: Footer height `842px`, social links `3`, footer link count `21`
- Tailwind stage baseline: Footer height `856px`, social links `5`, footer link count `23`
- the social-link area rendered as a single horizontal 32px flex row, so adding Facebook/Instagram did not by itself require extra vertical height on desktop

When reporting Option B, state this distinction explicitly: the social policy mismatch is fixed by adding links/updating X, while any remaining height delta is probably due to footer primitive typography/layout/padding differences and needs separate follow-up judgment.

## Browser/tooling pitfall

Fresh git worktrees may not have Playwright resolvable from that worktree even when the root checkout has dependencies. If a quick Node `require('playwright')` measurement fails with `MODULE_NOT_FOUND`, avoid installing dependencies just for a small PR unless asked. Use an available browser tool/MCP for live stage measurements, or report the local dependency-resolution limitation and rely on CI for broad validation.
