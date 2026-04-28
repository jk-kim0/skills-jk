---
name: nextjs-id-slug-canonical-route
description: Implement Next.js App Router detail pages that resolve content by id only, treat slug as canonical URL decoration, and redirect /[id] or mismatched slugs to /[id]/[slug].
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, app-router, routing, canonical, redirect, seo]
---

# Next.js id/slug canonical route pattern

Use this when a detail page URL has the form `/<section>/<id>/<slug>`, but the product requirement is:
- the content lookup should depend only on `id`
- `slug` exists only for canonical/readable URLs
- `/<section>/<id>` and `/<section>/<id>/` should still work
- a wrong slug should redirect to the canonical slug for that id

## Why this skill exists

A common failure mode is to implement redirect logic in the route page, but keep the data loader enforcing both `id` and `slug`. That means the page appears to support slug correction, yet the loader still returns `null` unless the incoming slug matches exactly.

If the requirement is “lookup by id, canonicalize slug separately”, then the loader must stop validating slug.

## Implementation steps

1. Keep the canonical detail route at `src/app/<section>/[id]/[slug]/page.tsx`.
2. In that route:
   - load the record metadata by `id`
   - `notFound()` if the id does not exist
   - compare `record.slug` with the incoming `slug`
   - `redirect()` to the canonical URL when mismatched
   - load the full post/content by `id` only
3. Add a sibling route at `src/app/<section>/[id]/page.tsx`.
   - load the record by `id`
   - `notFound()` if missing
   - `redirect()` to `/<section>/<id>/<canonical-slug>`
4. Update any content loader/helper that currently takes `(id, slug)` so it loads by `id` only.
5. Add a regression test that verifies:
   - `/<section>/[id]/page.tsx` exists and redirects canonically
   - `/<section>/[id]/[slug]/page.tsx` only uses slug for redirect comparison
   - the loader no longer rejects content when `slug` differs

## Recommended code shape

### Canonical route

```ts
import { notFound, redirect } from "next/navigation";

type PageProps = {
  params: Promise<{
    id: string;
    slug: string;
  }>;
};

export default async function DetailPage({ params }: PageProps) {
  const { id, slug } = await params;
  const record = getRecordById(id);

  if (!record) {
    notFound();
  }

  if (record.slug !== slug) {
    redirect(getCanonicalHref(id, record.slug));
  }

  const post = await getPostById(id);

  if (!post) {
    notFound();
  }

  return <PostView post={post} />;
}
```

### id-only redirect route

```ts
import { notFound, redirect } from "next/navigation";

type PageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function DetailIdRedirectPage({ params }: PageProps) {
  const { id } = await params;
  const record = getRecordById(id);

  if (!record) {
    notFound();
  }

  redirect(getCanonicalHref(id, record.slug));
}
```

### Loader change

Before:

```ts
export async function getPost(id: string, slug: string) {
  const post = getRecordById(id);
  if (!post || post.slug !== slug) {
    return null;
  }
  ...
}
```

After:

```ts
export async function getPost(id: string) {
  const post = getRecordById(id);
  if (!post) {
    return null;
  }
  ...
}
```

## Static params

If the canonical route is statically generated, keep `generateStaticParams()` on `[id]/[slug]` returning `{ id, slug }` pairs.

For the new `[id]` route, add a separate helper that returns `{ id }` only, for example:

```ts
export function listPublicationIds() {
  return records.map(({ id }) => ({ id }));
}
```

Then use it in `src/app/<section>/[id]/page.tsx`.

## Testing strategy

When full local runtime verification is expensive or dependencies are unavailable in a fresh worktree, a lightweight repository regression test can still lock in the contract by checking source patterns.

Useful assertions:
- `[id]/page.tsx` imports the id-only params helper and redirects with the canonical slug
- `[id]/[slug]/page.tsx` redirects on `record.slug !== slug`
- `[id]/[slug]/page.tsx` calls `getPost(id)` rather than `getPost(id, slug)`
- the loader no longer contains `post.slug !== slug`

## Pitfalls

- Only changing the page route and forgetting to relax the loader
- Assuming `/[id]/[slug]` automatically covers `/[id]` — it does not; add a sibling route
- Forgetting to add static params for the new `[id]` route when static generation is expected
- Returning content before redirecting mismatched slugs, which can create duplicate URLs

## Done criteria

- `/<section>/<id>` redirects to `/<section>/<id>/<canonical-slug>`
- `/<section>/<id>/wrong-slug` redirects to the canonical slug URL
- `/<section>/<id>/<canonical-slug>` renders successfully
- content lookup depends only on id
- tests lock in the canonicalization contract
