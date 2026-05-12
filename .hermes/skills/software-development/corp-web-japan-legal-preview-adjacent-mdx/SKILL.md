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

## Testing strategy
Add or update a narrow source-structure test such as `tests/legal-terms-of-service-preview.test.mjs`.

Verify:
1. `page.tsx` reads the adjacent MDX file under the same route directory
2. `generateMetadata()` derives title/description from frontmatter
3. `parseFrontmatter: true` is enabled
4. the hero reads `frontmatter.date`, `frontmatter.title`, and `frontmatter.description`
5. the MDX file contains frontmatter with `title`, `description`, `date`
6. the MDX file no longer contains wrapper-only layout markup such as `<Box ...>` or `<CenterSection ...>`
7. if the MDX body was reflowed, long prose follows the requested wrap width without splitting words and without accidentally absorbing a following plain paragraph into the previous bullet/list item
8. preview-aware footer links still point through the preview toggle helper if applicable

Useful assertions:
- `assert.match(source, /export async function generateMetadata\(\): Promise<Metadata>/)`
- `assert.match(source, /description: frontmatter\.description,/)`
- `assert.match(source, /parseFrontmatter: true,/)`
- `assert.doesNotMatch(contentSource, /<Box direction="column"/)`
- `assert.doesNotMatch(contentSource, /<CenterSection/)`

## Exception: versioned legal document collections
Not every legal preview route should be forced into a single route-adjacent `content.mdx` shape.

If the route is actually a versioned legal document collection, such as a privacy-policy surface with:
- a latest-version alias route
- per-version detail routes
- many historical MDX files
- version discovery from filenames

then a different structure can be preferable and should not automatically be judged as a failed route-local refactor.

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
- Also keep the route-local refactoring boundary clean: for a versioned legal route, `page.tsx` should normally stay thin and hold only route-entry responsibilities such as params, `generateStaticParams()`, `generateMetadata()`, and the final call into a route-local renderer.
- If the implementation needs many helper components or MDX rendering helpers, prefer sibling route-local files such as `document-renderer.tsx`, `version-selector.tsx`, or a route-local source helper under the same `src/app/t/<route>/` directory, rather than putting those definitions inline inside `page.tsx`.
- Avoid pushing that renderer back under shared `src/components/sections/**` when it is only used by one legal route family; the preferred direction is thin `page.tsx` + route-local support files, not thin `page.tsx` + shared section pseudo-singleton.

Practical implication learned from `/t/privacy-policy` review:
- A privacy-policy implementation with `src/app/t/privacy-policy/page.tsx`, `src/app/t/privacy-policy/[slug]/page.tsx`, route-local helper modules under `src/app/t/privacy-policy/`, and versioned files under `src/content/privacy-policy/*.mdx` is not a strong example of static-page route-local authoring, but it can still be an appropriate and well-factored implementation for a versioned legal document collection.
- Prefer the versioned detail route `src/app/t/privacy-policy/[slug]/page.tsx` to be the primary rendering owner. Do not leave it as a pure thin wrapper around a renderer living under `src/components/sections/**` when that renderer is effectively route-specific. If the rendering logic is specific to the privacy-policy route, move it into the route tree or route-local helper modules.
- If the user objects that `src/app/t/privacy-policy/[slug]/page.tsx` is only a thin wrapper, prefer moving the actual renderer and metadata logic into `src/app/t/privacy-policy/[slug]/page.tsx` itself, while keeping `src/app/t/privacy-policy/page.tsx` as the latest-version alias wrapper that resolves the newest slug and delegates to the `[slug]` route renderer.
- It is acceptable for the collection root `src/app/t/privacy-policy/page.tsx` to remain a thin wrapper whose job is only to resolve the latest version and delegate to the versioned detail renderer. Treat that route as a latest-version alias rather than a full page-authoring surface.
- For latest-version resolution, a filename-based sortable slug contract such as `YYYY-MM-DD.mdx` is sufficient when the corpus is intentionally file-system-driven. Do not add a duplicate hardcoded latest-version registry unless there is a concrete need.
- In that refactor, keep route-specific UI helpers such as the version selector under the same route directory (for example `src/app/t/privacy-policy/version-selector.tsx`) rather than under `src/components/sections/**`, because they are route-owned document-navigation primitives rather than reusable shared sections.
- When the route renders versioned legal MDX through `buildPublicationMdxComponents()` or another local MDX adapter, compare the adapter against the upstream/source-site table component contract before assuming the MDX content is wrong. In the privacy-policy investigation, the source MDX and migrated MDX both preserved `rowSpan`, `colSpan`, and `width`, but the local MDX adapter dropped those props because `Table.Td`/`Table.Th` only accepted `children` and `cellBackgroundColor` and did not forward the remaining DOM props to `<td>` / `<th>`. That causes merged cells and column widths to disappear at render time even though the MDX source is correct.

## Pitfalls
- Moving legal preview MDX to `src/content/**` when the user prefers route-local adjacency for a single-document legal page
- Incorrectly forcing a multi-version legal document collection into a single adjacent `content.mdx` pattern when the route really behaves like a document-rendering feature
- Leaving the page title duplicated both in frontmatter hero and inside the MDX body
- Keeping wrapper-only MDX components that force `page.tsx` to inject unnecessary custom components
- Forgetting to switch from static `metadata` to frontmatter-driven `generateMetadata()`
- Forgetting to update the source-structure tests when changing the route-local pattern

## Done criteria
- The legal document body lives in `src/app/.../content.mdx`
- Frontmatter defines `title`, `description`, and `date`
- `page.tsx` reads and evaluates that file with `parseFrontmatter: true`
- `generateMetadata()` is driven by frontmatter
- The hero uses frontmatter values
- MDX no longer depends on layout wrapper components that `page.tsx` can own instead
- Narrow tests pass
