# News list hero parity: querypie.ai → corp-web-app

Use this reference when matching `/{locale}/news` list-page hero title/lead rendering against `https://querypie.ai/news`.

## Source component contract

Reference repo: `/Users/jk/workspace/corp-web-japan`

`src/app/news/page.tsx` renders the hero through:

- `CompanyPageSection`
- `CompanyPageIntro`
- `CompanyPageTitle`
- `CompanyPageLead`

Source files:

- `src/components/sections/company/page-primitives.tsx`
- `src/components/ui/text-tokens.ts`

Key class contracts:

```tsx
<CompanyPageSection>
  className="mx-auto w-full max-w-[1920px] bg-white px-[30px] pb-[50px] pt-[100px] lg:pb-[72px] lg:pt-[120px]"

<CompanyPageIntro>
  className="flex flex-col gap-10 pt-[10px] text-left lg:gap-[50px] lg:pt-0"

<CompanyPageTitle>
  className="text-[40px] font-medium leading-[1.2] tracking-[-0.03em] text-slate-950 sm:text-[48px] lg:text-[52px]"

<CompanyPageLead>
  className={companyBodyTextClassName}

companyBodyTextClassName =
  "text-base font-light leading-7 tracking-[0.02em] text-slate-600"
```

## Rendered metrics to preserve

Measured on `https://querypie.ai/news` with Chrome/CDP, scrollY=0.

### 1440 × 1200

- Header: fixed, height 64px, bottom Y 64px.
- Hero section: top Y 0px, padding-top 120px, padding-left/right 30px.
- Intro container: x 120px, y 120px, width 1200px, height 140.390625px, gap 50px.
- Title `ニュース`:
  - top Y 120px, bottom Y 182.390625px, height 62.390625px.
  - font-size 52px, font-weight 500, line-height 62.4px, letter-spacing -1.56px.
- Lead text:
  - top Y 232.390625px, bottom Y 260.390625px, height 28px.
  - font-size 16px, font-weight 300, line-height 28px, letter-spacing 0.32px.
- Title bottom → lead top gap: 50px.
- Header bottom → title top: 56px, because the header is fixed and overlays the flow.

### 768 × 1200

- Hero section padding-top 100px.
- Intro container padding-top 10px, gap 40px.
- Title top Y 110px, font-size 48px, line-height 57.6px.
- Lead top Y 207.59375px.
- Title bottom → lead top gap: 40px.

### 390 × 1200

- Hero section padding-top 100px.
- Intro container padding-top 10px, gap 40px.
- Title top Y 110px, font-size 40px, line-height 48px.
- Lead top Y 198px.
- Title bottom → lead top gap: 40px.

## corp-web-app target mapping

Current corp-web-app `/{locale}/news` composes:

- `src/app/(tailwind)/[locale]/news/page.{en,ja,ko}.tsx`
- `NewsListPageSection` from `src/components/sections/resource-list/resource-list-section.component.tsx`

If aligning the news list hero to querypie.ai, update `NewsListPageSection` or split it into primitives whose contract matches the four source primitives above. Do not infer parity from copy equality alone: measure title/lead top Y, title font metrics, lead font metrics, and the title-to-lead gap in the browser.

## Pitfall

For top-of-page hero spacing, distinguish fixed overlay headers from in-flow/sticky headers. On querypie.ai the header is fixed at 64px, so a section title at Y=120px appears 56px below the GNB bottom. A target site with an in-flow header may need different section padding to produce the same visible GNB-to-title gap.

When reviewing or fixing a PR that already changed the hero, compare against current production/main as well as querypie.ai. In PR 935, the Preview did contain and compute the copied querypie.ai classes (`pt-[100px] lg:pt-[120px]`), but corp-web-app's sticky/in-flow header occupied document height first. The result was a regression versus existing production: at 1440px the production H1 top was 226px, while the PR Preview H1 top became 282px. The useful contract was not "copy `CompanyPageSection` classes"; it was the rendered visible gap from header bottom to title.

Concrete correction pattern from that case:

- Measure `header.getBoundingClientRect().bottom`, H1 top/bottom, lead top/bottom, and list/content top on production, Preview, and querypie.ai.
- If the target header is in-flow and the reference header is fixed/overlay, subtract the target header's occupied document-space effect from the copied section top padding.
- For PR 935's `/ja/news` surface, replacing `pt-[100px] lg:pt-[120px]` with `pt-[36px] lg:pt-[56px]` restored the intended visible gap target: about 46px on tablet/mobile and 56px on desktop from header bottom to H1 top.
- Update tests so they do not only bless copied reference class strings. Source assertions may pin the chosen target padding, but the review must still use browser geometry evidence before visual sign-off.
