# Lead-description geometry audit pattern

Use this reference when a corp-web-japan preview/stage page subtly differs from the live QueryPie reference around the hero title, lead description width, or subsequent section spacing.

## Procedure

1. Open the exact preview/stage URL and the exact live/reference URL in separate Chrome DevTools pages. Do not substitute a redirected or adjacent page.
2. Set both pages to the same viewport, usually 1440px desktop unless the user specified another breakpoint.
3. Scroll both pages to the top before measuring hero geometry.
4. Measure the title, lead paragraph, hero image, first few section titles/bodies/images, and comparison/CTA blocks with:
   - `getBoundingClientRect()` for `x`, `y`, `width`, `height`, `top`, and `bottom`.
   - `rect.top + scrollY` / `rect.left + scrollX` when comparing document positions after scrolling.
   - computed styles for `max-width`, `width`, `margin`, `padding`, `gap`, `font-size`, `line-height`, `font-weight`, `letter-spacing`, and `text-align`.
   - `Range.getClientRects()` for text nodes inside lead/body copy so line wrapping differences are explicit.
5. Convert positions into local gaps: title bottom -> lead top, lead bottom -> image top, section start -> title/image top, title -> image.
6. If the page uses reveal/scroll animations, scroll through the page and wait for animations to settle before final below-the-fold measurements. Off-screen `RevealOnScroll` elements can retain `translate-y` setup transforms and make geometry look wrong.
7. Only after measurement, inspect source to map deltas to code causes such as Tailwind `max-w-*`, `mt-*`, `pb-*`, or feature-copy width constraints.

## Example findings from usage-based LLM page comparison

Viewport: 1440px.

Compared pages:
- Stage: `https://stage.querypie.ai/t/platforms/aip/usage-based-llm`
- Live: `https://www.querypie.com/ja/solutions/aip/usage-based-llm`

Key measured deltas:
- Hero lead width: stage `895px`; live `955.1px`. Stage was about `60px` narrower, or about `30px` more inset on each side.
- Hero lead height: stage `112px`; live `87px`. Stage wrapped/laid out taller.
- Title -> lead gap: stage `18px`; live about `20px`.
- Lead -> hero image gap: stage `75px`; live about `80px`.
- First feature copy width: stage `417px`; live about `445px`.
- SSO feature copy width: stage `485px`; live about `518px`; this caused the stage SSO title to wrap to two lines while live stayed one line.
- Feature row image/copy gap stayed around `80px`; many visible differences came from narrower copy blocks and accumulated section padding/height, not from flex gap itself.

Code mapping in that session:
- Stage lead width came from `src/components/sections/usage-based-llm/section.tsx` using `max-w-[895px]` on `AipUsageBasedLlmHeroDescription`.
- Stage hero/image rhythm used `mt-[75px]` where live rendered closer to `80px`.
- Narrower feature copy blocks came from route-authored classes like `max-w-[417px]` and `max-w-[485px]` in `src/app/t/platforms/aip/usage-based-llm/page.tsx`.

## Implementation follow-up pattern

If the user asks to turn this audit into a PR, apply the measured geometry as a small source-level layout contract rather than doing a broad redesign.

Observed successful patch for the usage-based LLM route:
- Honor explicit user overrides before exact live computed values. In the session above, live measured about `955px`, but the user specifically requested `lead description max-width = 1000px`; the correct implementation used `max-w-[1000px]`.
- Align local gaps that were repeatedly short by about `5px`: `mt-[75px]` -> `mt-[80px]` for hero image and comparison image spacing; title-to-lead used `mt-[20px]` instead of `18px`.
- Align accumulated section rhythm when the next section starts too low/high: for the usage-based LLM hero, `pb-[187px]` was reduced to `pb-[120px]`; the comparison block used `py-[160px]` to match the live section rhythm.
- Keep row-specific copy widths at the route callsite so reviewers can see the authored layout intent. Successful measured desktop widths were approximately `445px`, `534px`, and `518px` for the first, second, and SSO feature copy columns. This avoided the SSO title wrapping to two lines on the preview route.
- Update the mirrored source-inspection test in the same PR to pin the new spacing/width contract, then run the narrow test only unless the user asks for heavier local verification.

Typical narrow verification:

```bash
node --test tests/src/app/t/platforms/aip/usage-based-llm/page.test.mjs
```

Do not start a local dev server by default for this user's corp-web-japan visual parity PRs. Push the PR and let CI / Preview Deployment provide the reviewable rendered output unless explicit local browser verification is requested.

## Reporting style

Report measured deltas directly, not vague visual impressions. Example:

`stage lead is 895px wide vs live 955.1px, so it is about 60px narrower / 30px more inset per side.`

Then explain which component position or spacing changes this produces.