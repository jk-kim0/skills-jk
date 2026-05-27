---
name: corp-web-v2-demo-acp-mdx-migration
description: Migrate corp-web-v2 legacy ACP demo content to short MDX-backed /demo/acp/:id/:slug routes, including redirects, asset relocation, tests, PR, and wiki updates.
---

# When to use

Use this when the user asks to migrate legacy `features/demo/acp-features/*` content in `corp-web-v2` to a shorter public route, especially when they want:

1. canonical routes like `/demo/acp/:id/:slug`
2. redirect from `/demo/acp/:id` to the canonical slug path
3. redirect from legacy `/features/demo/acp-features/:id/:slug`
4. MDX rendering similar to blog / white-paper
5. ACP thumbnail or inline asset path normalization
6. the demo migration wiki updated after implementation

# Preconditions

1. Start from fresh `origin/main` in a fresh worktree / branch.
2. Load the repo AGENTS guidance and inspect current blog / white-paper MDX route patterns.
3. Check whether the worktree has its own dependencies installed. In this repo, missing worktree-local deps can cause false failures like `Cannot find module 'mermaid'`; run `npm install` in the worktree before trusting build failures.

# Implementation pattern

## 1) Inspect existing routing and MDX conventions

Read at minimum:

- `src/app/[locale]/blog/[id]/[[...rest]]/page.tsx`
- `src/app/[locale]/white-paper/[id]/[[...rest]]/page.tsx`
- `src/features/mdx/loader.ts`
- `src/features/mdx/types.ts`
- `src/features/content/data.ts`
- `src/app/sitemap.ts`
- `src/app/[locale]/features/demo/[slug]/page.tsx`

Key conclusion from the successful approach:

- ACP should not remain under managed `features/demo/[slug]` detail routing.
- A separate MDX-backed route under `src/app/[locale]/demo/acp/[id]/[[...rest]]/page.tsx` works well and matches the existing `id + optional slug tail` blog/white-paper pattern.

## 2) Define an explicit ACP legacy-number map

Create a helper like `src/features/demo/acp.ts` containing:

- `{ id, slug }` entries for all ACP legacy rows
- `getAcpDemoEntry(id)`
- `getAcpDemoMdxSlug(id)` returning `acp/${id}`
- `getAcpDemoHref(locale, id)` returning `/demo/acp/:id/:slug`
- `resolveAcpDemoRoute(locale, id, rest)` returning `{ entry, canonicalHref, shouldRedirect }`

Important lesson:

- Do not derive canonical numbering from authored slugs alone.
- ACP legacy numbering may reuse or duplicate slugs (`review-audit-logs`, `grant-permissions-users`, etc.).
- Treat the legacy numeric ID as the public canonical key for the short route and maintain an explicit map.

## 3) Extend MDX category support

Update `src/features/mdx/types.ts` to include `"demo"` in `MdxCategory`.

Then add loader tests proving `loadMdxSource("demo", ...)` resolves the expected files and locale fallback works.

## 4) Add the new page route and redirect behavior

Create:

- `src/app/[locale]/demo/acp/[id]/[[...rest]]/page.tsx`
- `src/app/[locale]/features/demo/acp-features/[id]/[[...rest]]/page.tsx`

The canonical page should:

1. validate locale
2. resolve route via the ACP helper
3. redirect if slug is missing or wrong
4. load `demo` MDX source for `acp/:id`
5. render using the same MDX render pipeline as blog / white-paper
6. reuse `BlogLayout` unless a dedicated demo MDX layout is explicitly needed
7. set metadata canonical to the short route

The legacy route should be implemented as a redirect-only route handler, not a page component, when it does not render UI.

Create:

- `src/app/[locale]/features/demo/acp-features/[id]/[[...rest]]/route.ts`

The legacy route handler should:

- only redirect to `getAcpDemoHref(locale, id)`
- return HTTP 404 if the ID is unknown
- use `NextResponse.redirect(new URL(href, request.url))`

Do not keep a `page.tsx` for a route whose only purpose is redirecting. In this repo, redirect-only legacy demo routes were later cleaned up from `page.tsx` to `route.ts` for clearer intent.

## 5) Convert authored ACP HTML into MDX files

Store content under:

- `src/content/mdx/demo/acp/<id>/en.mdx`
- `src/content/mdx/demo/acp/<id>/ko.mdx`
- `src/content/mdx/demo/acp/<id>/ja.mdx`

Successful conversion strategy used here:

- parse existing `src/content/demo/acp-features/cnt_*/{locale}.html`
- convert `<iframe>` embeds to `<Youtube ... />`
- convert headings/paragraphs/lists/blockquote to MDX/markdown
- preserve one-sentence-per-line style where possible
- use frontmatter:
  - `layout: "Article"`
  - `category: "demo"`
  - `title`
  - `description`
  - `date`
  - `ogImage`
  - `hideHeroImage: true`

Practical finding from this migration:

- ACP authored HTML had many iframe embeds but no `<img>` tags in the audited content set.
- Thumbnail migration still mattered because thumbnails existed in `public/demo/acp-features/*` and were used for `ogImage` normalization.

## 6) Normalize asset paths

For thumbnails, copy legacy assets into:

- `public/demo/acp/<id>/thumbnail.webp`

Then set frontmatter `ogImage` to the new normalized path:

- `public/demo/acp/<id>/thumbnail.webp`

If inline images exist in future ACP content, follow the same per-entry folder rule under `public/demo/acp/<id>/` and reference them from MDX via `ArticleFileImage` using normalized per-entry paths.

## 7) Centralize public href generation for short demo routes

Do not limit the change to only the new route file.

Update the central demo detail href generation path (for example `src/features/content/data.ts` via `getPublicDetailHref(...)`) so internal links, related items, and sitemap consumers all prefer the short canonical route helper before falling back to legacy managed demo paths.

Successful follow-up pattern after the initial ACP migration:

- ACP uses an explicit helper like `getAcpDemoHrefByContentId(...)`
- AIP can follow the same pattern with `getAipDemoHrefByContentId(...)`
- use-cases can follow the same pattern with `getUseCaseDemoHrefByContentId(...)`
- the generic legacy route `src/app/[locale]/features/demo/[slug]/page.tsx` should redirect to the short canonical route whenever one of these helpers resolves

Important lesson:

- putting the short-route preference in one central href function is safer than patching many callers independently
- this keeps list pages, related-content links, canonical metadata inputs, and future consumers aligned automatically

## 8) Update sitemap

Update `src/app/sitemap.ts` to add the short canonical routes explicitly via the category helper map.

Do not rely on existing managed demo content state for these MDX-backed or remapped short routes.

## 9) Scope boundary: keep ACP MDX routes fully separate from CMS-managed demo pages

Important correction learned during PR #40 follow-up:

- Do not couple new ACP MDX routes to the existing CMS-managed demo rendering flow.
- In this repo, `src/app/[locale]/features/demo/[slug]/page.tsx` is the existing managed demo detail page backed by authored/CMS data under `src/content/demo/**`.
- That managed page may read HTML/Tiptap-derived content such as `src/content/demo/acp-features/cnt_000025/*`; when the user asks to keep CMS-managed demo rendering untouched, leave this page and its data flow unchanged.
- The ACP MDX route must remain a separate rendering path backed by `src/content/mdx/demo/acp/**` only.

Practical rule for this PR shape:

1. keep `src/app/[locale]/demo/acp/[id]/[[...rest]]/page.tsx` as the MDX-backed canonical detail page
2. keep `src/app/[locale]/features/demo/acp-features/[id]/[[...rest]]/route.ts` as a redirect-only legacy adapter
3. do not modify `src/app/[locale]/features/demo/[slug]/page.tsx` to redirect ACP/AIP/use-case/webinar content to short routes when the user wants CMS-managed demo pages preserved
4. do not change `src/features/content/data.ts` / `getPublicDetailHref(...)` to prefer short routes for CMS-managed AIP/use-case/webinar content in this ACP-only migration
5. do not add `/demo/aip`, `/demo/use-case`, or `/demo/webinar` page routes as part of this ACP-only PR unless the user explicitly asks for a separate CMS-managed short-route project

Why this matters:

- ACP MDX migration is about introducing a new authored MDX rendering path similar to blog/white-paper.
- AIP/use-case/webinar in the current repo snapshot are still CMS-managed demo entries, so moving them into short routes by reading managed content from new `page.tsx` files mixes responsibilities and violates the desired separation.
- If short-route work for CMS-managed categories is requested later, treat it as a separate task/PR with its own routing and content-source design review.

## 10) Optional follow-up pattern for other categories (only if explicitly requested)

If the user explicitly requests short public routes for CMS-managed AIP/use-case/webinar items in a separate task, first confirm that the scope allows touching CMS-managed demo routing. Only then consider patterns such as:

- AIP canonical detail route: `/demo/aip/:id/:slug`
- use-case canonical detail route: `/demo/use-case/:id/:slug`
- webinar canonical detail route: `/demo/webinar/:id/:slug`

Important route-design findings from that separate exploration:

- for use-case detail pages, singular `use-case` is preferable to plural `use-cases` because the URL represents one concrete case entry
- for webinar detail pages, singular `webinar` is preferable to plural `webinars` for the same reason
- support `/demo/<category>/:id` by redirecting it to `/demo/<category>/:id/:slug`

Important data-mapping finding from webinars:

- some legacy webinar rows can point at the same managed `contentId` multiple times under different legacy numbers
- do not assume a 1:1 relationship between legacy number and managed content entry
- for categories with duplicate legacy rows, keep an explicit `{ id, slug, contentId }` map and choose one representative legacy number as the canonical public ID
- when the user gives a preferred legacy number for a duplicated entry, treat that number as the canonical public ID if possible and redirect the other duplicate legacy numbers to it
- implement this by making the `contentId -> entry` lookup resolve to the chosen canonical entry and by having `get...Href(id)` normalize alias IDs through that canonical entry before generating the public route

Implementation pattern for those separate follow-ups:

1. create an explicit `{ id, slug, contentId }` map per category helper file
2. expose `get...Href(locale, id)`, `get...HrefByContentId(locale, contentId)`, and `resolve...Route(locale, id, rest)` helpers
3. add `src/app/[locale]/demo/<category>/[id]/[[...rest]]/page.tsx`
4. add legacy redirect routes under `src/app/[locale]/features/demo/<legacy-category>/[id]/[[...rest]]/route.ts`
5. if and only if scope allows it, extend legacy slug redirect logic or central public href generation for the newly supported category
6. add focused helper tests plus `getPublicDetailHref(...)` expectations for the new short route

## 11) Tests to add

Add pure/helper tests first. The successful minimal coverage here was:

- `src/features/demo/acp.test.ts`
  - mapping lookup
  - canonical href generation
  - redirect decision for missing/wrong slug
- `src/features/mdx/loader.test.ts`
  - demo category file loading
  - locale fallback to `en.mdx`

Then run at least:

- `npm run test:run -- src/features/demo/acp.test.ts src/features/mdx/loader.test.ts`
- `npm run build`

## 9) PR workflow

1. stage only the intended files
2. commit with a focused message like:
   - `feat: migrate acp demo content to mdx routes`
3. push branch
4. create Draft PR
5. verify PR body rendering if it contains backticks or route literals; shell quoting can strip route examples if not escaped properly

## 10) Wiki update workflow

Update the demo comparison wiki page after the implementation is pushed:

- `querypie-com-Demo-Content-Migration-Comparison-Table`

What to update:

1. top summary counts
2. ACP category completion count
3. each ACP row’s new-site path
4. note that legacy ACP paths and `/demo/acp/:id` redirect to the canonical slug path

When editing ACP rows, generate them programmatically if possible because there are many similar entries and duplicate slugs make manual editing error-prone.

# Pitfalls

- Duplicate slugs across different ACP legacy IDs are real; never assume slug uniqueness.
- Worktree-local dependency state matters in this repo; a failing build may be only a missing `npm install` in that worktree.
- `gh pr create --body "...` with unescaped backticks can let the shell eat route examples; prefer `--body-file` for safer PR bodies.
- ACP MDX routes are independent from current managed demo detail routes, so sitemap and helper logic must be wired explicitly.

# Verification checklist

- `/demo/acp/1/integrating-querypie-with-redash` renders
- `/demo/acp/1` redirects to the canonical slug path
- `/features/demo/acp-features/1/integrating-querypie-with-redash` redirects to the short route
- `npm run test:run -- src/features/demo/acp.test.ts src/features/mdx/loader.test.ts` passes
- `npm run build` passes after worktree-local deps are installed
- wiki summary reflects ACP completion and reduced unmapped count
