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
- prefer extending `src/components/sections/legal/document.tsx` with a common vocabulary such as `LegalDocumentHero` rather than creating one wrapper per route
- `LegalDocumentHero` can safely absorb family differences through props/children, for example:
  - `title`
  - optional `meta` / effective date
  - optional `description`
  - optional selector controls as children for versioned pages
  - optional `divider`
  - optional `titleVariant="compact"`
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
- Avoid hiding the full page composition in `src/components/sections/privacy-policy/document-page.tsx`, a route-local `document-renderer.tsx`, or another helper that turns `src/app/t/privacy-policy/[slug]/page.tsx` back into a thin caller. The route file should still show how the page is assembled.
- When the route renders versioned legal MDX through `buildPublicationMdxComponents()` or another local MDX adapter, compare the adapter against the upstream/source-site table component contract before assuming the MDX content is wrong. In the privacy-policy investigation, the source MDX and migrated MDX both preserved `rowSpan`, `colSpan`, and `width`, but the local MDX adapter dropped those props because `Table.Td`/`Table.Th` only accepted `children` and `cellBackgroundColor` and did not forward the remaining DOM props to `<td>` / `<th>`. That causes merged cells and column widths to disappear at render time even though the MDX source is correct.

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
