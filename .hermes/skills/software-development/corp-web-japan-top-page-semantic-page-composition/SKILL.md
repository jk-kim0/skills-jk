---
name: corp-web-japan-top-page-semantic-page-composition
description: Refactor corp-web-japan top-page code so page.tsx directly carries marketing copy while extracted components provide slot-style semantic layout shells rather than giant content-object props.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, nextjs, static-page, refactor, semantic-composition, slots]
---

# corp-web-japan top page: semantic page composition

Use this when the user wants the top page (or similar static marketing pages) written so that `page.tsx` is readable as page content, not as a thin wrapper around a giant data prop.

## When to use
- The user says `page.tsx` should show the marketing copy directly.
- The current code passes a large content object into section components like `TopPageSolutionOverviewSection({ solutionBranch })`.
- The user wants extracted components to express UX semantics such as container / intro / group / title / body / action while keeping copy in `page.tsx`.

## Core rule
Do **not** replace one giant data blob with one giant section prop.

Bad:
- `TopPageSolutionOverviewSection solutionBranch={topPageSolutionBranch}`
- `TopPageCoreValueSection coreValue={topPageCoreValue}`
- `TopPageFinalCtaSection finalCta={topPageFinalCta}`

Preferred:
- `page.tsx` contains the copy and JSX composition
- extracted components are slot-like layout shells with semantic names
- content constants may remain for URLs or truly shared metadata, but not as the primary way the page text is authored

## Desired outcome shape
Aim for `page.tsx` to read like this:

```tsx
<TopPageSolutionOverviewSection>
  <TopPageSolutionOverviewIntro title={<>...</>}>
    <TopPageSolutionOverviewLead>...</TopPageSolutionOverviewLead>
    <TopPageSolutionOverviewLead>...</TopPageSolutionOverviewLead>
  </TopPageSolutionOverviewIntro>

  <TopPageSolutionChoiceGroup>
    <SolutionChoiceCard href="/solutions/ai-crew" tone="crew">
      <SolutionChoiceHeader>
        <SolutionChoiceBadge>AI Crew</SolutionChoiceBadge>
      </SolutionChoiceHeader>
      <TopPageSolutionChoiceContent>
        <TopPageSolutionChoiceHeading>
          <SolutionChoiceTitle>...</SolutionChoiceTitle>
          <SolutionChoiceSubtitle>...</SolutionChoiceSubtitle>
        </TopPageSolutionChoiceHeading>
        <SolutionChoiceDescription>...</SolutionChoiceDescription>
        <SolutionChoiceAction>...</SolutionChoiceAction>
      </TopPageSolutionChoiceContent>
    </SolutionChoiceCard>
  </TopPageSolutionChoiceGroup>
</TopPageSolutionOverviewSection>
```

The exact names can vary, but the important property is:
- **copy lives in `page.tsx`**
- **components provide semantic structure**

## Good semantic extraction targets
For top-page style sections, prefer extracting components such as:
- `TopPageSolutionOverviewSection`
- `TopPageSolutionOverviewIntro`
- `TopPageSolutionOverviewLead`
- `TopPageSolutionChoiceGroup`
- `TopPageSolutionChoiceContent`
- `TopPageSolutionChoiceHeading`
- `TopPageCoreValueSection`
- `TopPageCoreValueGrid`
- `TopPageCoreValueCard`
- `TopPageCoreValueCardHeader`
- `TopPageCoreValueCardBadge`
- `TopPageCoreValueCardIcon`
- `TopPageCoreValueCardHeading`
- `TopPageCoreValueBulletList`
- `TopPageCoreValueBullet`
- `TopPagePlatformRequirementsSection`
- `TopPagePlatformRequirementsBlock`
- `TopPagePlatformRequirementsBlockContent`
- `TopPagePlatformRequirementsBlockLabel`
- `TopPagePlatformRequirementsBlockTitle`
- `TopPagePlatformRequirementsBlockBody`
- `TopPagePlatformRequirementsBlockImage`
- `TopPageSecuritySection`
- `TopPageSecurityCertificationGrid`
- `TopPageSecurityCertificationCard`
- `TopPageWhitepaperDownloadSection`
- `TopPageWhitepaperGrid`
- `TopPageWhitepaperCard`
- `TopPageWhitepaperTag`
- `TopPageWhitepaperToc`
- `TopPageFinalCtaSection`
- `TopPageFinalCtaTitle`
- `TopPageFinalCtaBody`
- `TopPageFinalCtaActionGroup`
- `TopPageFinalCtaActionLink`

## Keep these in content files only if truly appropriate
Still okay to keep in `src/content/top-page.ts`:
- metadata strings used by `metadata`
- shared URLs such as `topPageFloatingCtaUrl`, `topPageDownloadUrl`, `topPageFinalDemoUrl`, `topPageFinalConsultUrl`
- large structured interactive datasets that are not the page's authored marketing copy, if the user agrees

But if the user explicitly asks for copy in `page.tsx`, move section copy out of giant objects and into the page.

## Practical implementation steps
1. Inspect current `page.tsx`, `src/content/top-page.ts`, and any extracted section files.
2. Identify which giant props are only carrying page copy.
3. Replace those APIs with slot-like semantic shells.
4. Move actual text, headings, bullets, and CTA labels into `page.tsx`.
5. Keep only URL constants / metadata constants external if useful.
6. Update tests/helpers that assumed structure lived only in `top-page-sections.tsx` or only in `page.tsx`.
   - In this repo, `tests/helpers/static-marketing-page-sources.mjs` may need to aggregate multiple top-page structure files.
   - Structure tests may need to accept either direct variable references or literal hrefs when slot composition changes the exact source location.
7. Run:
   - `npm run test:ci`
   - `npm run build`

## Known pitfalls
- Do not stop after moving from `TopPageSections` to several giant section props; that still fails the user's intended authoring model.
- Tests in this repo can fail because they grep source strings rather than executing runtime behavior. Update those tests carefully when source layout changes.
- If a client component uses `createContext` / `useContext`, ensure it is marked with `"use client"`.
- Avoid passing component functions from server `page.tsx` into client components. Prefer serializable props or let the client component select its own icon/variant from context.

## Success criteria
- `page.tsx` is readable as a page document with real copy visible inline.
- Extracted components express UX semantics and layout roles.
- Giant content-object props for page copy are gone.
- `npm run test:ci` passes.
- `npm run build` passes.
