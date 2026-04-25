---
name: corp-web-japan-cta-link-constants
description: Refactor corp-web-japan CTA URLs into top-of-file or page-level constants so repeated contact/demo/download links stay consistent and tests verify the indirection.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# corp-web-japan CTA link constants

Use when a user asks to reduce CTA link mistakes by replacing repeated inline href strings with named constants.

## Goal

Make CTA-heavy surfaces safer to maintain by:
- defining repeated CTA URLs once near the top of the owning file, or in a tiny page-specific content/link module
- reusing those constants across page wrappers, content objects, and nearby section components
- updating tests so they verify the intended constant wiring instead of only matching raw literals everywhere

## When to use
- repeated `/contact-us?...` URLs appear multiple times in one page flow
- repeated `/demo/use-cases` or whitepaper/download URLs appear across one page and its helper sections
- the user explicitly says CTA links should be defined as constants at the top of each page

## Proven patterns

### 1. Keep constants close to the owning page surface

Good placements found in this repo:
- top-page content-owned links: define exported constants at the top of `src/content/top-page.ts`
- AI Crew content-owned links: define exported constants at the top of `src/content/home.ts`
- AI Dashi page-owned links shared by multiple files: create a tiny page-specific module such as `src/content/ai-dashi-links.ts`
- one-off local CTA inside a single component: define a small local const near the top of that component file

Practical rule:
- if the links are used only inside one content file, keep them in that content file
- if the links are used by both the page file and sibling components, extract a small page-specific links file rather than duplicating strings

### 2. Prefer semantic names over label-based names

Good examples:
- `topPageFloatingCtaUrl`
- `topPageHeroContactUrl`
- `topPageDownloadUrl`
- `topPageFinalDemoUrl`
- `topPageFinalConsultUrl`
- `aiCrewFloatingCtaUrl`
- `aiCrewConsultUrl`
- `demoUseCasesUrl`
- `aiDashiFloatingUrl`
- `aiDashiConsultUrl`
- `aiDashiWhitepaperUrl`

Avoid vague names like:
- `ctaUrl`
- `buttonLink`
- `url1`

### 3. Export shared constants when multiple files need them

Examples that worked:
- `src/content/home.ts` exports:
  - `demoUseCasesUrl`
  - `aiCrewWhitepaperUrl`
  - `aiCrewFloatingCtaUrl`
  - `aiCrewConsultUrl`
- `src/content/top-page.ts` exports:
  - `topPageFloatingCtaUrl`
  - `topPageHeroContactUrl`
  - `topPageDownloadUrl`
  - `topPageFinalDemoUrl`
  - `topPageFinalConsultUrl`
- `src/content/ai-dashi-links.ts` exports:
  - `aiDashiFloatingUrl`
  - `aiDashiConsultUrl`
  - `aiDashiWhitepaperUrl`

Then import them into:
- page wrappers using `FloatingConversionCta`
- helper components like `ai-crew-floating-guide.tsx`
- FAQ or other section components that otherwise repeat the same `/contact-us?...` string

### 4. Do not over-extract unrelated shared navigation in the same pass

If the user asked specifically about CTA links on the active PR surface:
- refactor the CTA-bearing page/content files first
- leave unrelated shared header/footer navigation alone unless the user also asked for those

This keeps the change reviewable and aligned with user intent.

## Test update pattern

When constants replace inline literals, update tests to verify the indirection deliberately.

Examples:
- literal checks may become:
  - `primaryCta ... href: aiCrewConsultUrl`
  - `floatingCta ... href: aiCrewFloatingCtaUrl`
  - `href={aiDashiConsultUrl}`
  - `href={aiDashiWhitepaperUrl}`
  - `href={resourcePostContactUrl}`
- if constants moved into a separate file, read that file in the test too
  - for AI Dashi, read `src/content/ai-dashi-links.ts`
  - verify exported constants there, then verify the page imports and uses them

Useful test adjustments:
- `launch-readiness-coverage.test.mjs`
- page-specific CTA tests like:
  - `tests/ai-crew-cta-links.test.mjs`
  - `tests/ai-dashi-cta-links.test.mjs`

## Verification

Run targeted CTA tests after refactor:

```bash
npm test -- --test-name-pattern='AI Crew CTA links match the intended targets|AI Dashi CTA links match the intended targets|launch-risk CTA targets resolve to explicit anchors or real destinations'
```

If the refactor touched broader shared surfaces, re-run the closest affected CTA/link integrity tests too.

## Pitfalls

1. Do not replace a repeated literal with multiple different constants for the same semantic destination.
   - One semantic destination should usually map to one named constant.

2. Do not move everything into one giant global links file.
   - This repo works better with page-local or surface-local constants.

3. When patching tests, avoid keeping stale expectations for removed local consts.
   - Example: once AI Dashi link constants moved into `src/content/ai-dashi-links.ts`, tests should stop expecting `const aiDashiWhitepaperUrl = ...` inside `page.tsx`.

4. Keep contact/demo/download semantics grounded in the repo's AGENTS contract.
   - Refactoring should preserve the existing intended CTA destinations, not reinterpret them.
