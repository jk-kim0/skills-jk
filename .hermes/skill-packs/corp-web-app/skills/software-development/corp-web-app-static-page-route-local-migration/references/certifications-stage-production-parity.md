# Certifications stage ↔ production parity audit (session 2026-05-16)

## URLs compared
- Production: https://www.querypie.com/ko/company/certifications
- Stage: https://stage.querypie.com/ko/company/certifications

## Viewport / capture state
- Desktop viewport ~1470 px wide
- Critical: full-page screenshot must be captured at `scrollY === 0`. If scrollY > 0, the sticky header renders with `box-shadow` and appears mid-page in the screenshot, creating a false layout mismatch.

## Verified as identical (computed style probes)
| Element | Property | Value (both) |
|---------|----------|--------------|
| cert grid | `gap` | `40px 30px` |
| cert grid | `grid-template-columns` | `380px 380px 380px` |
| card | `background-color` | `rgb(246, 248, 250)` |
| card | `padding-bottom` | `60px` |
| header (scrollY=0) | `box-shadow` | `none` |

## Actual bugs found

### 1. Page title mismatch
- Prod: `QueryPie AI Certifications`
- Stage: `Certifications`
- **Root cause**: route-local `metadata.title` in `page.ko.tsx` / `page.en.tsx` / `page.ja.tsx` was written as bare `Certifications`; production previously appended `QueryPie AI` via a hierarchy of `meta.json` files that no longer apply to the route-local path.
- **Fix**: update `title` and `openGraph.title` on all three locale pages.

### 2. ISMS-P description duplication
- In `certification-items.ts`, ISMS-P had `description: ['Business Continuity', 'Management']` — identical to ISO 22301.
- **Fix**: change ISMS-P description to `['Information Security Management', 'System for Privacy']`.

## Automated probes used
```js
// Run on both tabs beforescreenshotting
{
  title: document.title,
  ogTitle: document.querySelector('meta[property="og:title"]')?.content,
  h1: document.querySelector('h1')?.textContent,
  scrollY: window.scrollY,
  viewport: window.innerWidth,
}
```

## Evidence files
- `/tmp/certifications-stage-top.png` — stage full-page (scrollY=0)
- `/tmp/certifications-prod-reloaded.png` — prod full-page (scrollY=0)

## Related files in repo
- `src/app/[locale]/company/certifications/page.{en,ko,ja}.tsx` — locale pages + metadata
- `src/app/[locale]/company/certifications/certification-items.ts` — card data
- `src/components/widget/certifications/certifications.component.tsx` — shared card component
