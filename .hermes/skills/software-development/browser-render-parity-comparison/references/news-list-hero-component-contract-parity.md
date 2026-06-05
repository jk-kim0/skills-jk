# News/list hero component-contract parity

Use this when a collection/list page hero (title + lead/description + first content block) must match a source site such as querypie.ai, especially for `/{locale}/news`-style pages.

## Lesson

Do not compare only text content or top-level page routes. For list heroes, identify the source component contract and measure the live rendered geometry together:

1. In the source repo/page, map the exact component stack that renders the title and lead.
   - Example source: `corp-web-japan/src/app/news/page.tsx`.
   - Source stack observed for querypie.ai `/news`:
     - `CompanyPageSection`
     - `CompanyPageIntro`
     - `CompanyPageTitle`
     - `CompanyPageLead`
     - `CompanyPageLayout`
     - `NewsListSection`
2. Measure the live page at the target viewport before editing.
   - Title rect, font-size, font-weight, line-height, letter-spacing, x/y.
   - Lead rect, font-size, font-weight, line-height, letter-spacing, x/y.
   - Wrapper padding and intro gap.
   - Header position/height if the requested alignment is relative to GNB.
3. Port the contract as a coherent wrapper/title/lead/list-start set instead of approximating individual properties.

## querypie.ai `/news` contract captured at 1440px

Source files:

- `corp-web-japan/src/app/news/page.tsx`
- `corp-web-japan/src/components/sections/company/page-primitives.tsx`
- `corp-web-japan/src/components/ui/text-tokens.ts`
- `corp-web-japan/src/components/sections/news/page-section.tsx`

Rendered/source-equivalent classes:

- Section (`CompanyPageSection`):
  - `mx-auto w-full max-w-[1920px] bg-white px-[30px] pb-[50px] pt-[100px] lg:pb-[72px] lg:pt-[120px]`
- Inner container:
  - `mx-auto w-full max-w-[1200px]`
- Intro (`CompanyPageIntro`):
  - `flex flex-col gap-10 pt-[10px] text-left lg:gap-[50px] lg:pt-0`
- Title (`CompanyPageTitle`):
  - `text-[40px] font-medium leading-[1.2] tracking-[-0.03em] text-slate-950 sm:text-[48px] lg:text-[52px]`
- Lead (`CompanyPageLead` via `companyBodyTextClassName`):
  - `text-base font-light leading-7 tracking-[0.02em] text-slate-600`
- List start (`NewsListSection`):
  - `mx-auto mt-[44px] max-w-[1200px] lg:mt-[80px]`

Live geometry at 1440x1200:

- Header: fixed, height 64px, bottom Y 64px.
- Section top Y: 0px, padding-top 120px.
- Title: x 120px, top Y 120px, height 62.390625px, font-size 52px, line-height 62.4px, letter-spacing -1.56px.
- Lead: x 120px, top Y 232.390625px, height 28px, font-size 16px, font-weight 300, line-height 28px, letter-spacing 0.32px.
- Title bottom to lead top: 50px.
- Header bottom to title top: 56px because the header is fixed and overlays the page flow.

## corp-web-app implementation note

For `corp-web-app` `/{locale}/news`, the target component was `NewsListPageSection` in:

- `src/components/sections/resource-list/resource-list-section.component.tsx`

When aligning to querypie.ai, update that shared news list section contract rather than changing locale page files, because `page.en.tsx`, `page.ja.tsx`, and `page.ko.tsx` all compose through `NewsListPageSection`.
