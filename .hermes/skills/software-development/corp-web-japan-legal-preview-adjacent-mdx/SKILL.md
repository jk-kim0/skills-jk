---
name: corp-web-japan-legal-preview-adjacent-mdx
description: Implement or refactor a corp-web-japan legal preview page so page.tsx renders a route-adjacent MDX file, with frontmatter driving metadata and hero copy, and without MDX wrapper-component dependencies.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Corp-web-japan legal preview with adjacent MDX

Use this when working on corp-web-japan legal/policy preview routes such as `/t/terms-of-service` or similar static legal pages.

## When to use
- A legal preview page currently hardcodes long document content inside `page.tsx`
- The user wants the legal body moved into MDX
- The user prefers the MDX file to live next to the route, not under `src/content/**`
- The user wants title/description/date managed in frontmatter
- The user wants `page.tsx` to own hero/layout/CTA while MDX stays as document body only

## Preferred file layout
For a route like `src/app/t/terms-of-service/page.tsx`:

- Keep the route file:
  - `src/app/t/terms-of-service/page.tsx`
- Add an adjacent MDX file:
  - `src/app/t/terms-of-service/content.mdx`

Do not move this kind of legal preview body to `src/content/**` when the user prefers route-local clarity.

## Final architecture

### `content.mdx`
- Put legal document metadata in frontmatter:
  - `title`
  - `description`
  - `date`
- Keep the MDX body as pure document content
- For long legal prose, keep the source readable as well as the rendered output:
  - wrap prose at a target width such as 80 or 120 characters depending on the requested contract
  - break lines only at word boundaries; do not split words just to satisfy the width target
  - preserve valid MDX structure while reflowing, including frontmatter, headings, numbered lists, bullets, indentation, and inline MDX/JSX tags
- Do **not** keep wrapper-only layout components in the MDX when they are unnecessary, such as:
  - `<Box direction="column" ...>`
  - `<CenterSection ...>`
  - route-title wrappers already rendered by `page.tsx`
- Start the actual body content directly after frontmatter
- Let the first body heading be the first article/section heading, not the page title repeated again

Example shape:

```mdx
---
title: "QueryPie Terms of Service"
description: "Terms of service for QueryPie AIP covering service use, member obligations, privacy, AI output limitations, and governing law."
date: "2025-06-05"
---

# Article 1 (Purpose)
...
```

### `page.tsx`
- Read the adjacent MDX file with:
  - `readFile` from `node:fs/promises`
  - `join` from `node:path`
- Evaluate the MDX with `parseFrontmatter: true`
- Define a frontmatter type in `page.tsx`
- Use `generateMetadata()` so metadata is derived from MDX frontmatter
- Render a route-owned hero/header block from frontmatter values:
  - date
  - title
  - description
- Render the MDX body below the hero
- Keep shared site chrome and CTA in `page.tsx`

Preferred pattern:

```ts
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Metadata } from "next";
import { evaluate } from "next-mdx-remote-client/rsc";

type Frontmatter = {
  title: string;
  description: string;
  date: string;
};

async function renderContent() {
  const sourcePath = join(process.cwd(), "src/app/t/terms-of-service/content.mdx");
  const source = await readFile(sourcePath, "utf8");

  return evaluate<Frontmatter>({
    source,
    components: {
      ...buildPublicationMdxComponents(),
      h1: LegalBodyH1,
      Link: TermsMdxLink,
    },
    options: {
      parseFrontmatter: true,
      mdxOptions: {
        remarkPlugins: [remarkGfm],
      },
    },
  });
}

export async function generateMetadata(): Promise<Metadata> {
  const { frontmatter } = await renderContent();

  return {
    title: `${frontmatter.title} | QueryPie AI`,
    description: frontmatter.description,
    alternates: { canonical: "/t/terms-of-service" },
    robots: { index: false, follow: false },
  };
}
```

## CTA/layout pattern
If the page already uses the modern shared CTA pattern, prefer:
- `SimpleCtaSection`
- `CtaContent`
- `CtaCopy`
- `CtaTitle`
- `CtaDescription`
- `CtaActions`
- `BrandGradientCtaButton`

This keeps legal preview pages aligned with the newer preview-page composition pattern.

## What to remove during refactor
When converting from inline-content or wrapper-heavy MDX:
- remove giant inlined `String.raw` MDX blobs from `page.tsx`
- remove route-title markup duplicated inside MDX if frontmatter now drives the hero
- remove unnecessary wrapper components from MDX
- remove custom MDX component injections that only existed for those wrappers

## Commonizing existing legal page families

When the user asks to apply a PR #461-style commonization to legal pages, treat it as a page-family primitive cleanup:
- compare the current legal pages first: single-document routes such as EULA / Terms of Service and multi-version routes such as Privacy Policy
- preserve `page.tsx` as the visible page-composition owner, but remove page-specific wrappers whose only job is to assemble the same legal header/body shape
- prefer extending `src/components/sections/legal/document.tsx` with shared legal-family primitives rather than creating one wrapper per route
- for Issue-449-style work, align legal vocabulary to the Company-family authoring shape without importing Company primitives directly:
  - `LegalDocumentSection` corresponds to `CompanyPageSection` and owns the outer legal shell
  - `LegalDocumentIntro` corresponds to `CompanyPageIntro` and owns legal header vertical rhythm
  - `LegalDocumentTitle` corresponds to `CompanyPageTitle`
  - `LegalDocumentLead` corresponds to `CompanyPageLead` / the old legal description text
  - `LegalDocumentLayout` corresponds to `CompanyPageLayout` and wraps the document body area
  - `LegalDocumentBody` and `legalDocumentBodyClassName` remain legal-specific body/MDX primitives
- when the user says legal pages still look different or asks to unify UI/className settings, treat route-local legal className props as suspect even if the markup names already match:
  - compare legal primitives against `src/components/sections/company/page-primitives.tsx`
  - align the shared legal primitive className contract with the company family where requested, especially section padding/width, intro gap/pt/text alignment, title typography, and lead text token usage
  - remove route-local differences such as `<LegalDocumentIntro divider>`, `<LegalDocumentIntro className="...">`, `<LegalDocumentTitle variant="compact">`, and `<LegalDocumentBody className="[&_h1:first-child]:mt-0">` / `[&_h2:first-child]:mt-0` when the goal is family-wide UI consistency
  - remove compatibility-wrapper spacing that bypasses the shared intro contract, such as `LegalDocumentHero` wrapping title/lead in a nested `<div className="flex flex-col gap-3">` or adding `className={cn(children && "flex flex-col gap-4", className)}`; if the request is to match company-family spacing, let `LegalDocumentHero` render meta/title/lead/children directly under `LegalDocumentIntro` so `gap-10` / `lg:gap-[50px]` remains the source of truth
  - if a legal page needs a title-adjacent control row (for example privacy-policy title + version selector), do not keep route-local wrapper divs like `<div className="flex flex-col gap-3">` or `<div className="flex flex-wrap items-center gap-4">`; introduce or use a shared legal primitive such as `LegalDocumentTitleActions` in `src/components/sections/legal/document.tsx`, then render `<LegalDocumentTitleActions><LegalDocumentTitle>...</LegalDocumentTitle><...Selector /></LegalDocumentTitleActions>` from the route
  - move first-body-heading normalization into `legalDocumentBodyClassName` instead of keeping per-route `LegalDocumentBody className` overrides
  - if `LegalDocumentLead` is meant to match the company family, reuse `companyBodyTextClassName` from `@/components/ui/text-tokens` rather than duplicating a nearby text class
  - update both mirrored route tests (`tests/src/app/t/...`) and older top-level legal tests (`tests/legal-*.test.mjs`) so they assert the shared primitive className contract and assert route-local overrides are absent; privacy-policy currently has both `tests/legal-privacy-policy-preview.test.mjs` and `tests/src/app/t/privacy-policy/page.test.mjs`, and both must be updated when replacing title/selector wrapper markup
- route authoring should migrate to the new visible composition shape, for example:
  - `<LegalDocumentSection>`
  - `<LegalDocumentIntro>`
  - `<LegalDocumentTitle>{frontmatter.title}</LegalDocumentTitle>`
  - optional `<LegalDocumentMeta>` / `<LegalDocumentLead>` / selector controls
  - `<LegalDocumentLayout><LegalDocumentBody>...</LegalDocumentBody></LegalDocumentLayout>`
- keep compatibility aliases during a refactor-only PR unless the user explicitly asks for a hard breaking rename:
  - `LegalDocumentPageSection` delegates to `LegalDocumentSection`
  - `LegalDocumentHeader` delegates to `LegalDocumentIntro`
  - `LegalDocumentDescription` delegates to `LegalDocumentLead`
  - `LegalDocumentHero` may remain as a compatibility wrapper implemented with `Intro` + `Meta` + `Title` + `Lead`
- do not keep using compatibility names in the migrated route authoring surface; the aliases are for older imports and staged migration safety, not the preferred vocabulary
- `LegalDocumentHero` can safely absorb family differences while it remains as a compatibility wrapper, for example:
  - `title`
  - optional `meta` / effective date
  - optional `description`
  - optional selector controls as children
  - optional `divider`
- Do not reintroduce title variants such as `titleVariant="compact"` when the goal is company-family typography parity. In the shared legal typography contract, `LegalDocumentTitle` should match `CompanyPageTitle`, and route-specific title sizing belongs behind an explicit new product decision rather than a compatibility prop.
- centralize repeated MDX evaluation in `src/lib/legal-mdx-source.ts`; keep the cached source reader, and add a helper such as `renderLegalMdx<Frontmatter extends Record<string, unknown>>({ sourcePath, components })` so pages do not each import `evaluate`, `remarkGfm`, or repeat `parseFrontmatter: true`
- keep route-specific content source path and custom MDX component adapter choices in the route or route-family owner; for example privacy policy may still pass `components: buildPrivacyPolicyDocumentComponents()` while EULA and Terms use the default legal document MDX components
- remove now-redundant route-specific wrapper modules when their responsibilities have moved into the common legal vocabulary, e.g. a `terms-of-service/section.tsx` that only exported `TermsOfServiceHero`, `TermsOfServiceBody`, and an MDX render helper

This is analogous to the company-page PR #461 pattern: move repeated header/body shell language into shared primitives, then express each page's actual composition with those primitives directly in the route file.

## Testing strategy
Add or update narrow source-structure tests such as `tests/legal-terms-of-service-preview.test.mjs` and mirrored route tests under `tests/src/app/t/<route>/page.test.mjs`.

Verify:
1. `page.tsx` reads the adjacent MDX file under the same route directory, or the versioned content root for multi-version routes
2. `generateMetadata()` derives title/description from frontmatter
3. `parseFrontmatter: true` is enabled in the shared legal MDX helper when evaluation is centralized
4. the hero reads `frontmatter.date`, `frontmatter.title`, and `frontmatter.description` directly or through `LegalDocumentHero` props
5. the MDX file contains frontmatter with `title`, `description`, and `date` where applicable
6. the MDX file no longer contains wrapper-only layout markup such as `<Box ...>` or `<CenterSection ...>`
7. if the MDX body was reflowed, long prose follows the requested wrap width without splitting words and without accidentally absorbing a following plain paragraph into the previous bullet/list item
8. preview-aware footer links still point through the preview toggle helper if applicable
9. deleted route-specific wrapper files are asserted absent, and no tests still read those deleted files
10. every duplicate legal structure test is updated: this repo can have both top-level tests such as `tests/legal-mdx-cache.test.mjs` / `tests/legal-privacy-policy-preview.test.mjs` and mirrored route tests under `tests/src/**`
11. when the user asks whether privacy-policy/legal MDX reads are cached like blog/whitepaper, compare the legal cache contract against the actual publication loaders in the same source-structure test:
    - `src/lib/publications/create-standard-publication-post-loader.ts` has `bodySourceCache = new Map<string, string>()`, `bodySourceCache.get(sourcePath)`, and `bodySourceCache.set(sourcePath, source)`
    - `src/lib/publications/create-gated-publication-post-loader.ts` has the same body-source cache pattern for gated whitepapers
    - `src/lib/legal-mdx-source.ts` has `legalMdxSourceCache = new Map<string, Promise<string>>()`, `readCachedLegalMdxSource(sourcePath)`, `legalMdxSourceCache.get(sourcePath)`, and `legalMdxSourceCache.set(sourcePath, sourcePromise)`
    - privacy policy version pages route `src/content/privacy-policy/${slug}.mdx` through `renderLegalMdx<PrivacyPolicyFrontmatter>({ sourcePath, ... })`
    - single-version legal pages such as EULA and Terms call the same `renderLegalMdx` helper from a route-level `cache(async function ...)`

If the implementation is already correct, keep the PR minimal and test-only: strengthen `tests/legal-mdx-cache.test.mjs` to pin the cache contract rather than making unnecessary product-code changes.

12. when the user reports that changing the privacy-policy version selector looks like the whole page reloads, inspect the selector before blaming MDX/cache performance:
    - `window.location.assign(`/privacy-policy/${nextSlug}`)` is document-level navigation and will look like a full page reload
    - prefer App Router client navigation in `src/components/sections/privacy-policy/version-selector.tsx`: import `useRouter` from `next/navigation`, initialize `const router = useRouter()`, and call `router.push(`/privacy-policy/${nextSlug}`)` from `onChange`
    - keep the guard against empty/current slug, but remove browser-only `typeof window` checks that only existed for `window.location`
    - update both `tests/legal-privacy-policy-preview.test.mjs` and `tests/src/app/privacy-policy/page.test.mjs` to assert `useRouter`, `router.push(...)`, and absence of `window.location.assign`; this repo has duplicate privacy-policy structure tests and CI static-pages will fail if the mirrored test is missed
    - run `npm run test:static-pages`, not just the narrow top-level legal test, after changing privacy-policy selector contracts
    - explain clearly that this reduces document-level reload behavior, while the server-rendered RSC payload for the selected legal version may still be fetched

## Legal MDX performance-delay triage

When the user asks why privacy-policy or another legal MDX page is slow, do not stop at checking whether the MDX file read is cached. Separate these layers explicitly:
1. Route/full-page caching: inspect live response headers with `curl -L -s -D - -o /dev/null <url>` and check `cache-control` plus `x-vercel-cache`.
2. Dynamic rendering triggers: search for `cookies()`, `headers()`, `draftMode()`, `connection()`, `force-dynamic`, and `noStore` in route chrome and shared components. In this repo, `SiteHeader` and `SiteFooter` can make otherwise-static public pages dynamic because they read the preview-navigation cookie server-side.
3. MDX source-read cache: verify `src/lib/legal-mdx-source.ts` has `legalMdxSourceCache`, `readCachedLegalMdxSource`, and that legal routes call `renderLegalMdx`.
4. Request-local memoization: verify route-level `cache(async function ...)` around privacy/terms/eula render helpers, but remember React `cache()` is not a CDN or cross-request rendered-output cache.
5. Render weight: measure source and rendered output size, not just file-read behavior. Privacy policy can be much heavier than EULA/Terms because of large table-heavy MDX.

Useful probes:
```bash
curl -L -o /dev/null -s -w 'code=%{http_code} ttfb=%{time_starttransfer} total=%{time_total} size=%{size_download}\n' https://stage.querypie.ai/privacy-policy
curl -L -s -D - -o /dev/null https://stage.querypie.ai/privacy-policy | sed -n '1,40p'
python3 - <<'PY'
from pathlib import Path
for p in ['src/content/privacy-policy/2026-01-15.mdx','src/app/terms-of-service/content.mdx','src/app/eula/content.mdx']:
    path = Path(p)
    text = path.read_text()
    print(p, 'bytes=', path.stat().st_size, 'lines=', text.count('\n') + 1, 'tables=', text.count('<Table'), 'td=', text.count('<Table.Td'), 'th=', text.count('<Table.Th'))
PY
```

Interpretation rule:
- If live headers show `cache-control: private, no-cache, no-store` and `x-vercel-cache: MISS`, the user-visible delay is likely not a missing MDX source-read cache. It is more likely full-route dynamic rendering plus MDX evaluation / large HTML generation.
- If `cookies()` in shared chrome is the dynamic trigger, the biggest optimization is usually to split preview-cookie behavior out of the server-rendered public chrome or move it to a client-side mechanism, not to add another raw file-read cache.
- For `/privacy-policy`, also check whether the latest-version alias directly renders the latest document instead of redirecting to `/privacy-policy/<slug>`; that can be a design/performance tradeoff but is separate from source-read caching.

See `references/legal-mdx-cache-and-performance.md` for a concrete investigation snapshot and measured timings.

Useful assertions:
- `assert.match(source, /export async function generateMetadata\(\): Promise<Metadata>/)`
- `assert.match(source, /description: frontmatter\.description,/)`
- `assert.match(source, /parseFrontmatter: true,/)`
- `assert.doesNotMatch(contentSource, /<Box direction="column"/)`
- `assert.doesNotMatch(contentSource, /<CenterSection/)`

## Variation: versioned legal document collections
Not every legal preview route should be forced into a single route-adjacent `content.mdx` shape.

If the route is actually a versioned legal document collection, such as a privacy-policy surface with:
- a latest-version alias route
- per-version detail routes
- many historical MDX files
- version discovery from filenames

then a different structure can be preferable and should not automatically be judged as a failed route-local refactor.

Important classification rule from corp-web-japan follow-up:
- do **not** describe a versioned legal route like privacy-policy as a family-level exception
- treat it as the normal `multi-version legal MDX` variant of the same legal/document family
- the corresponding `single-version legal MDX` variant is what routes like EULA or Terms of Service use when only one current document version is published
- if EULA or Terms of Service later need to expose historical versions, they may legitimately evolve toward the same multi-version route shape as privacy-policy

In that case, an acceptable implementation is:
- thin route files under `src/app/t/<route>/page.tsx` and optionally `src/app/t/<route>/[slug]/page.tsx`
- a route-scoped renderer/helper module under the same route directory
- a route-scoped source-discovery module under the same route directory
- the actual versioned MDX corpus under a shared content root such as `src/content/<route>/*.mdx`

How to evaluate that structure:
- Do not grade it by the static-marketing rule that `page.tsx` must be the primary copy/composition authoring surface.
- Instead, treat it as a document-rendering feature route.
- Check whether the route-specific renderer, source-discovery logic, metadata wiring, and version selector behavior are coherently scoped to the route directory.
- Check whether the file system is the source of truth for versions, rather than a duplicated hardcoded registry.
- Check whether frontmatter still drives metadata and hero text.
- Also keep the route-local refactoring boundary clean: for a versioned legal route, `page.tsx` should normally stay thin and hold only route-entry responsibilities such as params, `generateStaticParams()`, `generateMetadata()`, and the final call into the renderer.

Practical implication learned from `/t/privacy-policy` review:
- A privacy-policy implementation with `src/app/t/privacy-policy/page.tsx`, `src/app/t/privacy-policy/[slug]/page.tsx`, version discovery under `src/lib/privacy-policy/records.ts`, page-part rendering under `src/components/sections/privacy-policy/`, and versioned files under `src/content/privacy-policy/*.mdx` is an appropriate structure for a versioned legal document collection.
- Prefer the versioned detail route `src/app/t/privacy-policy/[slug]/page.tsx` to be the primary rendering owner, but keep it thin: it should own route-entry concerns and call into the privacy-policy renderer rather than defining many helper components inline.
- If the user objects that `src/app/t/privacy-policy/[slug]/page.tsx` is only a thin wrapper, the fix is usually to move the rendering ownership out of generic shared locations and into a route-specific family module, not to pack all helper components back into `page.tsx`.
- For this repo and user, do not create many non-route files under `src/app/t/privacy-policy/` just to satisfy route-locality. If a file is not an actual route entry file such as `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, or `route.ts`, first ask whether it is really route-only glue or whether it belongs under `src/components/sections/privacy-policy/` or `src/lib/privacy-policy/` instead.
- Correct privacy-policy split learned from PR #422 follow-up:
  - `src/app/t/privacy-policy/page.tsx` -> latest-version alias wrapper; it may stay thin and may derive the latest document date for the alias page
  - `src/app/t/privacy-policy/[slug]/page.tsx` -> version-detail page-composition owner
  - `src/components/sections/privacy-policy/**` -> only extracted UI primitives and implementation details, not the whole page assembly
- A privacy-policy implementation with `src/app/t/privacy-policy/page.tsx`, `src/app/t/privacy-policy/[slug]/page.tsx`, version discovery in `src/lib/privacy-policy/records.ts`, and versioned files under `src/content/privacy-policy/*.mdx` can still be an appropriate structure for a versioned legal document collection.
- However, for this user, do **not** over-correct into a `page.tsx` that is only a thin wrapper around a route-local or section-level `document-page.tsx` / `document-renderer.tsx` helper. Even for a versioned legal route, `src/app/t/privacy-policy/[slug]/page.tsx` should remain the page-composition owner: the file should visibly contain the caller/layout composition that places the header, effective date, title, description, selector area, MDX body, CTA, and footer.
- What may be extracted from `page.tsx` is the component implementation detail, not the page composition itself. Good extraction targets are things like a version selector component, language selector component, selector wrapper component, or MDX heading/link components under `src/components/sections/privacy-policy/**`.
- However, do not preserve selector components just because privacy-policy is a multi-version legal route. If the user says the language switcher or change-history control is unnecessary on `/t/privacy-policy`, remove those controls from `src/app/t/privacy-policy/[slug]/page.tsx` entirely instead of keeping dead UI around as a reusable abstraction.
- Practical follow-up from the `/t/privacy-policy` header-controls cleanup: when removing those controls, also delete the now-unused files under `src/components/sections/privacy-policy/` rather than leaving orphaned `document-header-controls.tsx` or `version-selector.tsx` modules behind, and update the privacy-policy structure tests to assert that the route no longer renders `PrivacyPolicyLanguageSelector`, `PrivacyPolicyVersionSelector`, or `PrivacySelectorBox`.
- Avoid hiding the full page composition in `src/components/sections/privacy-policy/document-page.tsx`, a route-local `document-renderer.tsx`, or another helper that turns `src/app/t/privacy-policy/[slug]/page.tsx` back into a thin caller. The route file should still show how the page is assembled.
- When the route renders versioned legal MDX through `buildPublicationMdxComponents()` or another local MDX adapter, compare the adapter against the upstream/source-site table component contract before assuming the MDX content is wrong. In the privacy-policy investigation, the source MDX and migrated MDX both preserved `rowSpan`, `colSpan`, and `width`, but the local MDX adapter dropped those props because `Table.Td`/`Table.Th` only accepted `children` and `cellBackgroundColor` and did not forward the remaining DOM props to `<td>` / `<th>`. That causes merged cells and column widths to disappear at render time even though the MDX source is correct.
- For `/t/privacy-policy` follow-up cleanup, treat header controls as two separate responsibilities:
  - language selector (`Korean / English`)
  - version selector (`Change history` / version dropdown)
  If the user says the language selector is unnecessary, do **not** infer that the version selector should also be removed. Privacy policy is the normal multi-version legal variant, so preserving version-history navigation can still be required even when cross-language links are removed.
- Also treat the intro block itself as separable responsibilities. In privacy-policy follow-up work, the user may ask to remove only one top-of-page line at a time:
  - the pre-title meta line such as `Effective date: 2026-01-15`
  - the post-title lead/description line such as `QueryPie Privacy Policy effective Jan 15, 2026.`
  - the version selector row
  Do **not** collapse these into one bulk "header cleanup" unless the user explicitly asks for all of them. Remove exactly the requested line(s), keep the remaining intro pieces intact, and update route-structure tests to assert the removed JSX is absent while preserved intro controls still remain.

## Legal effective-date body placement

For current corp-web-japan public legal pages, the single-version routes are under `src/app/eula/` and `src/app/terms-of-service/` (not the old preview-only `src/app/t/...` paths). If a legal source-structure test still points at `src/app/t/eula/content.mdx` or `src/app/t/terms-of-service/content.mdx`, update the test path to the current public route location instead of recreating old `/t` route files.

Use the EULA body-line format as the canonical legal effective-date display style in MDX bodies:
- place the line after the opening preamble/frontmatter gap and before the first article/section heading
- render it as a bold standalone paragraph, e.g. `**Effective from Jul 17, 2025**`
## Legal effective-date provenance and body placement

When the user asks to expose an effective date for legal MDX (EULA, Terms of Service, Privacy Policy, or similar), do not invent a legal date from the current local file or from the assistant's guess. Use `../corp-web-contents` source content and git history as the source of truth unless the user gives a stronger legal source.

General audit sequence:
1. Search historical source paths in `../corp-web-contents`, including route/language/version families such as `pages/eula/**`, `pages/terms-of-service-*/**`, and `pages/privacy-policy-{en,ko}/<version>/**`.
2. Inspect the source body for an explicit effective-date line first. Preserve the source date text when present; only change the local Markdown shape if requested (for example from a bullet item to an EULA-style bold body line).
3. If the source body has no explicit effective-date line, inspect source metadata/title/version path for a clear document date, especially versioned privacy-policy paths and meta titles such as `QueryPie Privacy Policy (Nov 29, 2019)`.
4. If there is still no explicit date information, use the date the source file first entered git history as the effective-date fallback. Use `git log --all --follow --diff-filter=A --date=short --format='%ad %h %s' -- <path>` and take the oldest add record.
5. Document the provenance in the PR body when the date is inferred rather than copied from a body line.

Preferred local display format for legal body effective dates is the EULA-style bold line placed after the opening preamble and before the first document heading, e.g. `**Effective from Jul 17, 2025**`. Avoid rendering effective dates as bullet-list items unless the user explicitly asks for source-exact Markdown.

### EULA effective-date notes

Recommended EULA audit sequence:
1. Search historical EULA paths in `../corp-web-contents`, especially `pages/eula/en/content.mdx` and `pages/eula/*/meta.json`.
2. Inspect EULA history with date-aware logs, for example:
   - `git -C ../corp-web-contents log --all --date=short --format='%h %ad %an %s' -- pages/eula/en/content.mdx pages/eula/en/meta.json`
   - `git -C ../corp-web-contents show --stat --date=short --format=fuller <commit> -- pages/eula/en/content.mdx pages/eula/en/meta.json`
3. Classify the latest substantive EULA content update as the effective-date candidate.
   - Ignore branch-preview/testing-only metadata commits, such as title-prefix test commits, when they do not change the legal body.
   - In the observed corpus, the latest substantive EULA body update was `451247f1` on `2025-07-17` with message `EULA 버전 업데이트 등 (#614)`; use this only as an example and re-check current history before future edits.
4. Store the machine-readable value in EULA frontmatter, e.g. `effectiveDate: "2025-07-17"`.
5. Display the human-readable line in the MDX body immediately after the opening EULA preamble and before `# PART I: GENERAL TERMS`, e.g. `**Effective from Jul 17, 2025**`.
6. Update the EULA frontmatter type in `src/app/t/eula/page.tsx` so `effectiveDate` remains part of the route's metadata contract even if the display line is authored in MDX.
7. Add or update `tests/src/app/t/eula/page.test.mjs` assertions for:
   - the frontmatter field
   - the exact visible line
   - the visible line appearing after the preamble and before `# PART I: GENERAL TERMS`

Pitfall: do not use `작성일` / authored date for EULA display by default. For legal documents, prefer an effective-date label; if only a publication date is available, state that separately instead of implying legal effect.

## Legal MDX source-formatting cleanup

When the user asks to refactor legal MDX source rather than change legal meaning or visual design, first classify the legal corpus and write/refine a small docs page with the rules before doing broad mechanical rewrites.

Current legal MDX corpus patterns to inspect:
- single-version adjacent legal pages such as `src/app/t/eula/content.mdx` and `src/app/t/terms-of-service/content.mdx`
- multi-version legal collections such as `src/content/privacy-policy/*.mdx`
- upstream/source comparisons under `../corp-web-contents/pages/eula`, `../corp-web-contents/pages/terms-of-service-*`, and `../corp-web-contents/pages/privacy-policy-{en,ko}`

Cleanup rules learned from the legal MDX refactor:
- remove wrapper-only MDX layout components inherited from the old source stack, especially `Box` and `CenterSection`; the route/shared legal primitives own page layout
- headings must start at column 1; remove wrapper-era indentation before `#` headings
- replace paragraph-spacing `<br />` outside table cells with normal Markdown blank lines
- preserve `<br />` inside `Table.Td` / `Table.Th` only when it represents intentional cell-internal line breaks and replacing it risks changing rendering
- minimize unnecessary JSX string expressions in MDX component children; plain text such as `{'Purpose of collection'}` should become ordinary text where syntax allows
- preserve `Table` / `Table.*` components when they are needed for legal table semantics, cell styling, spans, or structured rendering; do not remove them just because they are components
- wrap long prose at word boundaries, including JSX table-cell text nodes; JSX collapses whitespace in text nodes, so wrapped text children are safe when no syntax-sensitive characters are introduced
- keep nested list indentation valid; do not flatten nested bullets/numbered subitems during mechanical cleanup

Recommended verification:
- add or update a source-structure test that iterates every legal MDX file and asserts the rules above
- use `[ \t]` rather than `\s` when testing same-line indentation; a regex like `/^\s+#{1,6}\s/m` can cross a newline and falsely flag a normal heading after a blank line
- run the static legal/page test group plus `git diff --check` after broad rewrites

See `references/legal-mdx-source-formatting.md` for condensed session details and example assertions.

## Legal MDX body typography normalization audit

When the user asks whether privacy-policy / terms-of-service / EULA body rendering changes the default font size, audit the shared legal MDX rendering path first rather than the individual route files only.

Current route pattern to inspect:
- single-version routes like `src/app/t/terms-of-service/page.tsx` and `src/app/t/eula/page.tsx`
- multi-version privacy route `src/app/t/privacy-policy/[slug]/page.tsx`
- shared body primitive `src/components/sections/legal/document.tsx`
- shared MDX component mapper `src/components/sections/legal/mdx.tsx`
- privacy wrapper adapter `src/components/sections/privacy-policy/document-body-components.tsx`
- evaluator `src/lib/legal-mdx-source.ts`

Key diagnostic rule:
- if all three legal documents render via `<LegalDocumentBody>{evaluation.content}</LegalDocumentBody>`, then default-body typography issues usually live in `legalDocumentBodyClassName`, not in each route.

Non-standard legal body font-size settings to remove by default:
- body wrapper classes like `text-[16px] leading-[26px] text-slate-600` when they explicitly reset the default body size
- paragraph overrides like `[&_p]:text-[16px]` / `[&_p]:leading-[26px]`
- blockquote paragraph overrides like `[&_blockquote_p]:text-[16px]` / `[&_blockquote_p]:leading-[26px]`
- list overrides that shrink body text, such as `[&_li]:text-[15px]` or `[&_blockquote_li]:text-[15px]`
- component-local MDX mapper styles such as `LegalBodyH3` returning `<h4 className="mt-6 text-[15px] ...">`; MDX mappers should own semantic remapping and ids, while shared body classes own presentation

Preferred cleanup shape:
- let legal body text inherit/default font size
- keep line-height on standard Tailwind tokens such as `leading-6` where the body class still needs rhythm control
- keep legal document heading hierarchy, table styling, link styling, and first-child margin normalization in the shared legal body class; those are document-rendering styles, not default body font-size overrides
- keep top-level `ul` / `ol` margins for document block rhythm, but do not let the same wide block margin apply unchanged to nested `li > ul` / `li > ol`
- normalize nested bullet and nested numbered list rhythm explicitly, e.g. `"[&_li>ul]:mt-2 [&_li>ol]:mt-2"` plus `"[&_li>ul>li:last-child]:mb-0 [&_li>ol>li:last-child]:mb-0"`, so the parent list item, nested list items, and following sibling list item have visually consistent spacing
- keep `parseFrontmatter: true`, `remarkGfm`, and the shared legal/publication MDX component-map pattern as standard rendering, not as suspicious custom styling

Nested-list spacing pitfall:
- A broad selector like `[&_ul]:mt-[1.3125rem]` / `[&_ol]:mt-[1.3125rem]` also matches nested lists inside list items.
- If every `li` also has a bottom margin, the nested list's top margin and the nested list's last item margin can combine to make the parent list item gap look much larger than ordinary sibling gaps.
- Fix the nested-list container spacing separately from top-level list spacing; do not globally shrink all list margins just to solve nested lists.

Regression-test pattern:
- update both top-level legal tests and mirrored route tests when they exist
- assert the desired inherited/default body contract, for example `"leading-6 text-slate-600"`
- assert the nested-list spacing contract, for example:
  - `\[&_li>ul\]:mt-2 \[&_li>ol\]:mt-2`
  - `\[&_li>ul>li:last-child\]:mb-0 \[&_li>ol>li:last-child\]:mb-0`
- add negative assertions for the removed typography and spacing overrides, for example:
  - `text-\[16px\] leading-\[26px\] text-slate-600`
  - `\[&_p\]:text-\[16px\]`
  - `\[&_blockquote_p\]:mt-0 \[&_blockquote_p\]:text-\[16px\]`
  - `\[&_li\]:mb-2 \[&_li\]:text-\[15px\]`
  - `\[&_li>ul\]:mt-\[1\.3125rem\]`
  - `\[&_li>ol\]:mt-\[1\.3125rem\]`
  - `className="mt-6 text-\[15px\]`

Patch safety pitfall:
- When patching long class arrays, use a proper patch block or a small script with exact string slicing. Do not paste analysis/prose into `new_string`; malformed replacement text can pollute tracked source and must be immediately detected with a focused read, grep for stray text, and `git diff --check` before committing.

Report classification clearly in the PR body:
- list what non-standard settings were found and removed
- list what was inspected and intentionally kept as standard MDX rendering
- state that the effective affected pages are privacy-policy, terms-of-service, and EULA because they share the legal MDX body primitive

## Legal-adjacent cookie preference typography and rhythm audit

When the user asks about legal page typography and includes `/t/cookie-preference` / Cookie設定 copy, inspect both the route-specific components and the shared legal primitives before answering. This page has migrated over time, so do not answer from memory.

Historical implementation to recognize when reviewing older branches:
- `src/app/t/cookie-preference/page.tsx` rendered the hero title with `CookiePreferenceHeroTitle` and the intro prose with `CookiePreferenceHeroDescription`.
- `src/components/sections/cookie-preference/page.tsx` defined those primitives separately from `src/components/sections/legal/document.tsx`.
- `CookiePreferenceHeroTitle` rendered an `h1` with `text-[56.25px] font-normal leading-[67.5px] text-[#24292F]`.
- `CookiePreferenceHeroDescription` rendered a wrapper `div` with `text-[15px] font-light leading-[24.375px] tracking-[0.3375px] text-[#57606A]`; the nested `<p>` had no class and inherited those values.

Current/refactored implementation to verify on the active branch:
- cookie preference may now render `LegalDocumentSection`, `LegalDocumentIntro`, `LegalDocumentTitle`, and `LegalDocumentLead` directly from `src/components/sections/legal/document.tsx`.
- `LegalDocumentTitle` may be identical across cookie/privacy/eula/terms pages, but title-to-first-text spacing can still differ if the next rendered node differs.
- `LegalDocumentLead` commonly reuses `companyBodyTextClassName`; verify `src/components/ui/text-tokens.ts` for the actual body size/line-height/weight/tracking before reporting exact typography.

Important diagnostic learned from legal-family typography follow-up:
- do not equate "uses the same legal primitive names" with "has the same visual rhythm".
- Compare the rendered tree around the title, not just the imported component names:
  - cookie preference can place `<LegalDocumentTitle>` and `<LegalDocumentLead>` as siblings inside `<LegalDocumentIntro>`, so the title/lead gap is controlled by `LegalDocumentIntro`'s flex gap such as `gap-10` / `lg:gap-[50px]`.
  - privacy/eula/terms can place only the title inside `<LegalDocumentIntro>`, then render `<LegalDocumentLayout><LegalDocumentBody>...</LegalDocumentBody></LegalDocumentLayout>` after the header; their title/body gap is therefore controlled by the body/layout boundary and by the first MDX node's margins.
  - if the first MDX node is a paragraph, `legalDocumentBodyClassName` paragraph margin/line-height controls the apparent gap and prose size.
  - if the first MDX node is a heading, the legal MDX adapter may map MDX `#` to DOM `h2`; first-child heading margin normalization can make the first section heading sit much closer to the page title than a lead paragraph does.
- When explaining a perceived mismatch, report these three layers separately:
  1. hero title typography (`LegalDocumentTitle` class)
  2. intro/lead typography (`LegalDocumentLead` / text-token class)
  3. title-to-first-body spacing (`LegalDocumentIntro` gap vs `LegalDocumentBody` first-child margins)
- If the user asks to make the post-intro gap consistent whether `LegalDocumentLead` exists or not, make `LegalDocumentIntro` own the bottom rhythm, not each following body/list component:
  - add a shared bottom margin to `LegalDocumentIntro` such as `mb-10 ... lg:mb-[50px]` alongside the existing internal `gap-10` / `lg:gap-[50px]`
  - normalize first-child margins inside `legalDocumentBodyClassName` for `h1`, `h2`, `h3`, `h4`, `p`, `ul`, and `ol` so the first MDX node does not add a second, content-type-dependent top margin
  - remove route-specific follow-up margins such as `CookiePreferenceSettingsSection`'s `mt-[52.5px]`; otherwise cookie preference keeps a different gap even after the shared legal intro changes
  - update structure tests to assert the shared intro bottom margin, first-child body-margin normalization, and absence of route-specific margins

When the user explicitly asks to replace cookie preference's legal-page-specific hero wrappers with shared legal primitives:
- update `src/app/t/cookie-preference/page.tsx` to render `LegalDocumentSection`, `LegalDocumentIntro`, `LegalDocumentTitle`, and `LegalDocumentLead`
- keep `CookiePreferenceList` and the cookie toggle/list primitives; the request is about legal intro/body typography, not removing the actual cookie controls
- delete unused `CookiePreferenceHeroSection`, `CookiePreferenceHeroContent`, `CookiePreferenceHeroTitle`, and `CookiePreferenceHeroDescription` exports from `src/components/sections/cookie-preference/page.tsx`
- preserve and update the existing mirrored test `tests/src/app/t/cookie-preference/page.test.mjs`; do not overwrite it with a narrower new test because it already covers metadata, route-local copy, shell separation, and toggle/client boundaries
- add assertions that the route imports `@/components/sections/legal/document`, renders legal title/lead primitives, no longer references the cookie hero wrappers, and that the cookie page section file no longer exports those wrappers

When the user clarifies that the goal is to remove every incorrect implementation that blocks UI commonization, do not stop at swapping names:
- treat remaining cookie-preference-only wrappers as suspect, even if they are thin; if a wrapper only repeats the shared legal shell such as `max-w-[1200px]`, delete it and render the shared `LegalDocumentLayout` directly from the route
- delete `src/components/sections/cookie-preference/page.tsx` if it only contains dead hero/CTA wrappers or a redundant `CookiePreferenceSettingsSection`
- normalize cookie-list spacing away from arbitrary one-off values such as `gap-[40px]`, `gap-[20px]`, and `gap-[15px]`; prefer shared/Tailwind-scale spacing such as `gap-10`, `gap-5`, and `gap-4`
- connect cookie preference descriptive prose to the shared legal/company body text token, e.g. `companyBodyTextClassName`, rather than leaving it as browser default text or page-local px typography
- keep control-label emphasis minimal and semantic, such as `font-medium text-slate-950`, without reintroducing page-local font-size/line-height/tracking values
- update source-structure tests to assert the bad implementation is absent, not merely unused: no import from `@/components/sections/cookie-preference/page`, no `CookiePreferenceSettingsSection`, no cookie hero/CTA wrappers, no `gap-[...]`/`text-[#...]`/route-local typography in the cookie list, and `sourceExists("src/components/sections/cookie-preference/page.tsx") === false` when the file is deleted

Compatibility-prop / dead-contract pitfall:
- if `LegalDocumentIntroProps` or compatibility wrappers such as `LegalDocumentHero` / `LegalDocumentHeader` expose a `divider` prop, verify the implementation actually uses it before describing it as behavior.
- A prop can be TypeScript-valid because it appears in the props type, while still being a dead/no-op API if the component implementation ignores it. Call this out as "valid but misleading" and either remove the prop or implement the divider behavior when cleaning the primitive contract.
- When the user asks whether a legal primitive is an actual contract, do a source-wide usage audit before preserving it. Search both `src/` and `tests/`, but classify `tests/` matches as contract assertions rather than production usage.
- If a compatibility alias or helper is not used in `src/`, prefer removing it from `src/components/sections/legal/document.tsx` instead of keeping it for hypothetical staged migration safety. Update structure tests to assert absence with `assert.doesNotMatch(...)` so the dead contract is not reintroduced.
- In the current legal-family primitive shape, keep only actually used exports such as `LegalDocumentSection`, `LegalDocumentIntro`, `LegalDocumentLayout`, `LegalDocumentTitleActions`, `LegalDocumentTitle`, `LegalDocumentLead`, `LegalDocumentBody`, and `legalDocumentBodyClassName`; remove unused wrappers such as `LegalDocumentPageSection`, `LegalDocumentHeader`, `LegalDocumentHero`, `LegalDocumentMeta`, and `LegalDocumentDescription` unless a current route imports them.

## Width / shell provenance audit for legal pages

Before normalizing a legal preview route's document width, verify the source of that width instead of assuming a carried-over local value is correct.

Practical lesson from `/t/privacy-policy`, `/t/terms-of-service`, and `/t/eula` review:
- a local preview implementation used `max-w-[920px]` for the legal document wrapper
- but direct browser inspection of the live targets on `querypie.com/ja` showed the main legal content span rendering at about `1200px`
- the upstream `corp-web-app` `CenterSection` contract also resolves to `--content-max-width: 1200px`
- git history showed the `920px` wrapper was introduced in the initial preview-page PRs, but the PR bodies did not document a source-based reason for narrowing from the live/upstream width

Use this audit sequence before preserving or reusing a legal width token:
1. inspect the exact live legal page in the browser (`/ja/privacy-policy`, `/ja/terms-of-service`, `/ja/eula` as applicable)
2. measure the real rendered content span, not just the page shell
3. inspect upstream layout primitives such as `CenterSection` / shared content-width tokens in `corp-web-app`
4. inspect the original content source in `corp-web-contents`
5. inspect the preview-route introduction PRs to see whether the narrower width was an intentional documented readability choice or an undocumented local migration decision

Default interpretation for this repo/user:
- do **not** assume `max-w-[920px]` is authoritative for legal pages merely because it already exists in preview code
- if live and upstream both point to `1200px`, treat `920px` as a width-policy question that must be justified explicitly before being kept as a legal-family primitive
- separate these concerns during analysis:
  - outer page shell width
  - readable text measure / body typography
  - selector/header layout for versioned routes like privacy-policy

This matters because `privacy-policy` may be a structural exception due to version/language selectors while still not justifying a different width policy.

- When a legal preview page is meant to visually track the current `querypie.com/ja` legal surface, do not assume a narrow special-case document shell such as `max-w-[920px]` without evidence.
- Practical follow-up from the legal family audit: live `querypie.com/ja` legal pages (`/terms-of-service`, `/eula`, `/privacy-policy`) render their main legal content at about `1200px`, matching the upstream `corp-web-app` `CenterSection` contract via `--content-max-width: 1200px`.
- Therefore, treat an unexplained local `max-w-[920px]` legal shell as suspect by default. Do not preserve or primitive-ize that width unless you can point to current live rendering or an explicit source-of-truth that requires it.
- Separate these concerns explicitly:
  - outer legal shell width
  - inner readable prose measure
  - single-version vs multi-version page composition
  A legal page may share the same outer shell as the live site while still needing route-specific typography or selector-row variation.

## Reference notes
- `references/legal-family-width-audit.md` — evidence summary for why `max-w-[920px]` is incorrect for current legal preview shells, plus the rule that privacy-policy is the normal multi-version legal variant rather than a family-level exception.
- `references/legal-effective-date-provenance.md` — source-priority and fallback rules for deriving legal effective dates from `../corp-web-contents`, including Terms of Service and Privacy Policy examples.

## Pitfalls
- Moving legal preview MDX to `src/content/**` when the user prefers route-local adjacency for a single-document legal page
- Incorrectly forcing a multi-version legal document collection into a single adjacent `content.mdx` pattern when the route really behaves like a document-rendering feature
- Assuming an existing preview-only narrow width like `max-w-[920px]` is source-faithful without checking the live legal target, upstream `CenterSection` width contract, and preview-route introduction PR history
- Leaving the page title duplicated both in frontmatter hero and inside the MDX body
- Keeping wrapper-only MDX components that force `page.tsx` to inject unnecessary custom components
- Forgetting to switch from static `metadata` to frontmatter-driven `generateMetadata()`
- Forgetting to update the source-structure tests when changing the route-local pattern
- Centralizing MDX evaluation without preserving the TypeScript constraint expected by `evaluate`; use a generic such as `Frontmatter extends Record<string, unknown>` if needed
- Updating only the route-specific tests and missing older/top-level duplicate legal tests that still assert the previous structure or still read a deleted wrapper module
- Letting a commonization PR hide the route's page composition in a new helper; the goal is shared vocabulary, not making `page.tsx` opaque

## Done criteria
- The legal document body lives in `src/app/.../content.mdx`
- Frontmatter defines `title`, `description`, and `date`
- `page.tsx` reads and evaluates that file with `parseFrontmatter: true`
- `generateMetadata()` is driven by frontmatter
- The hero uses frontmatter values
- MDX no longer depends on layout wrapper components that `page.tsx` can own instead
- Narrow tests pass
