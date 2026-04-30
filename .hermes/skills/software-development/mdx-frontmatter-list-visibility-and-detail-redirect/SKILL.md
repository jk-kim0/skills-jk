---
name: mdx-frontmatter-list-visibility-and-detail-redirect
description: Add MDX frontmatter fields that hide entries from list pages without breaking detail routes, and optionally redirect detail requests to an external URL.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [mdx, frontmatter, nextjs, app-router, publications, redirect, list-filtering]
---

# MDX frontmatter: list visibility + detail redirect

Use this when a Next.js/MDX publication system needs two behaviors:
- a frontmatter flag that hides a post from the collection/list page
- a frontmatter URL that redirects detail-page requests elsewhere

Typical example:
- `hidden: true` means “do not show in `/blog` list”
- `redirectUrl: "https://..."` means `/blog/:id` and `/blog/:id/:slug` should redirect there

## Core rule

Do NOT remove hidden entries from the canonical record set.

Hidden entries should usually remain:
- resolvable by id
- included in `recordsById`
- available to detail-page loaders
- available to static params if the route should remain valid

Only the list-page derivation should filter them out.

This prevents accidental 404s for existing public detail URLs.

## Recommended data-model shape

Add optional fields to the frontmatter/record type:

```ts
export type PostFrontmatter = {
  id: string;
  slug: string;
  title: string;
  description: string;
  hidden?: boolean;
  redirectUrl?: string;
};
```

Normalize conservatively:

```ts
hidden: frontmatter.hidden === true,
redirectUrl: typeof redirectUrlValue === "string" ? redirectUrlValue : undefined,
```

## Correct cache / loader pattern

Keep all scanned records intact:

```ts
const records = loadPostRecords();
const recordsById = new Map(records.map((post) => [post.id, post]));
```

Filter only when producing list items:

```ts
const visibleRecords = records.filter((record) => !record.hidden);
const listItems = visibleRecords.map(toListItem);
```

Keep params derived from the full record set when the detail route must keep working:

```ts
export function listPublicationParams() {
  return records.map(({ id, slug }) => ({ id, slug }));
}
```

## Detail-route behavior

If the app has both:
- `/section/[id]/page.tsx`
- `/section/[id]/[slug]/page.tsx`

then check `redirectUrl` in BOTH routes.

### id-only route

Order:
1. load record by id
2. `notFound()` if missing
3. if `record.redirectUrl`, redirect there
4. otherwise redirect to canonical local slug URL

```ts
if (!record) {
  notFound();
}

if (record.redirectUrl) {
  redirect(record.redirectUrl);
}

redirect(getPublicationHref(id, record.slug));
```

### slug route

Order:
1. load record by id
2. `notFound()` if missing
3. if `record.redirectUrl`, redirect there
4. if incoming slug mismatches, redirect to canonical local slug URL
5. otherwise render local content

```ts
if (!record) {
  notFound();
}

if (record.redirectUrl) {
  redirect(record.redirectUrl);
}

if (record.slug !== slug) {
  redirect(getPublicationHref(id, record.slug));
}

const post = await getPublicationPost(id);
```

## Metadata behavior

If a detail route redirects externally, avoid generating misleading local canonical metadata.

Safe minimal pattern:

```ts
if (record.redirectUrl) {
  return {
    robots: {
      index: false,
      follow: false,
    },
  };
}
```

This avoids advertising the local detail route as canonical when it is only a redirect surface.

## TDD approach that worked well

Write source-structure regression tests first for:
- frontmatter type includes `hidden?` and `redirectUrl?`
- list derivation filters `records.filter((record) => !record.hidden)`
- `recordsById` still uses the full `records`
- params/static ids still derive from full `records`
- `/[id]` route redirects to `record.redirectUrl` before local canonical redirect
- `/[id]/[slug]` route redirects to `record.redirectUrl` before local render
- detail loader still resolves by id only

This is especially useful when repo tests are architecture/source-pattern based rather than full runtime integration tests.

## Common pitfall

Wrong approach:

```ts
const records = loadPostRecords().filter((record) => !record.hidden);
```

Why it is wrong:
- hidden posts disappear from `recordsById`
- hidden posts disappear from static params
- detail routes may 404 even though the requirement was “hide only from list”

## Optional hardening

If the codebase prefers stricter validation, consider validating `redirectUrl` format or allowed schemes during frontmatter normalization so invalid values fail fast.

## Verification

At minimum:
- targeted regression tests for list/detail behavior
- build verification for static route generation

For Next.js repos, a good lightweight combo is:

```bash
node --test tests/<feature-test>.test.mjs
npm run build
```

## Done criteria

- `hidden: true` removes the item from the list page only
- hidden posts still resolve on their existing detail URLs
- `redirectUrl` takes precedence on both `/section/:id` and `/section/:id/:slug`
- slug canonicalization still works for non-redirect posts
- tests lock in the non-404 contract for hidden posts
