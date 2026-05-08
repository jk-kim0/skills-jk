---
name: corp-web-japan-preview-route-rollout-to-canonical
description: Promote a corp-web-japan preview route under /t/* to the canonical public route, then either remove the old preview path entirely or keep it as a redirect only when that old path truly needs compatibility; also remove preview-only navigation switching for that surface.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# corp-web-japan: promote /t preview route to canonical public route

Use this when a corp-web-japan content surface currently has:
- a public route that still uses older or externalized behavior, and
- a preview route under `/t/*` that already contains the desired local implementation.

Example pattern:
- current public route: `/whitepapers`
- current preview route: `/t/whitepapers`
- desired end state when the preview path was never a public compatibility surface: `/whitepapers` uses the preview implementation and `/t/whitepapers` is removed entirely
- desired end state when compatibility is actually needed: `/whitepapers` uses the preview implementation and `/t/whitepapers` redirects to `/whitepapers`

## When to use

Use this workflow when the user asks to:
- move a preview list page into the real public route
- replace the current public route with the `/t/*` implementation
- remove header/footer preview switching for that specific route
- keep the old `/t/*` path from rendering duplicate content

## Core idea

Do not duplicate the preview implementation in two places long-term.

Preferred rollout:
1. move or copy the desired implementation into the canonical public route
2. decide explicitly whether the old `/t/*` path deserves compatibility at all
3. if the old preview path was never a public endpoint the user cares to preserve, delete that route instead of adding a redirect
4. only if the old preview path truly needs compatibility, turn it into a redirect to the canonical route
5. remove preview-navigation helper usage for that route in header/footer
6. update tests and delete preview-only helper/data files that existed only for the old `/t/*` behavior

## Safe repo workflow

1. Start from latest `origin/main` in a fresh worktree.
2. Re-read the current public route, preview route, and nav files from that worktree before editing.
3. Confirm whether the public route already has canonical metadata that should be preserved.

## Files to inspect first

Typical files for this rollout:
- `src/app/<public-route>/page.tsx`
- or, for still-externalized public endpoints, `src/app/<public-route>/route.ts`
- `src/app/t/<route>/page.tsx`
- `src/components/layout/site-header-client.tsx`
- `src/components/layout/site-footer.tsx`
- `src/lib/preview-navigation.ts`
- route/detail href helpers such as `src/lib/publications/get-publication-href.ts`
- related tests under `tests/`

For whitepaper rollout specifically, also inspect:
- `src/lib/publications/whitepaper-publication-records.ts`
- any tests covering list item source or route metadata

## Implementation pattern

### 1. Replace the public route with the local preview-backed implementation

Typical change:
- public route currently imports an externalized item list, or is still only a `route.ts` redirect to `querypie.com/ja`
- preview route currently imports the local loader

If the current public endpoint is a redirect-only `route.ts`, the rollout usually means:
- delete `src/app/<public-route>/route.ts`
- create `src/app/<public-route>/page.tsx` using the former `/t/*` implementation
- keep the new page metadata canonical on the non-`/t` route

Example target pattern:

```tsx
import { listWhitepaperPublicationItems } from "@/lib/publications/whitepaper-publication-records";

export default async function WhitepaperPage() {
  const whitepaperItems = await listWhitepaperPublicationItems();
  return <ResourceListPage items={whitepaperItems} ... />;
}
```

Preserve public metadata like:
- `title`
- `description`
- canonical `/whitepapers`

Do not accidentally carry over preview-only `noindex,nofollow` metadata into the canonical public route.

### 2. Decide whether the old `/t/*` page should be deleted or redirected

Important corp-web-japan default:
- unless the user explicitly asks to preserve a specific `/t/*` path, do **not** keep the old preview endpoint
- do **not** add a redirect just because compatibility is theoretically possible
- treat `/t/*` as internal preview-only by default

Ask this before preserving any compatibility endpoint:
- did the user explicitly request that exact `/t/*` path remain reachable?
- if not, remove it entirely

If it was only an internal preview surface, delete the route file entirely.

Typical deletion outcome:
- remove `src/app/t/<route>/page.tsx`
- remove tests that expect a rendered preview page and replace them with existence checks that confirm the file is gone
- remove any preview-only datasets or helper modules that existed only to feed that `/t/*` page

Only use a redirect when there is an explicit user request for that exact compatibility need.

### 3. If compatibility is needed, turn the old `/t/*` page into a redirect

Preferred minimal form:

```tsx
import { redirect } from "next/navigation";

export default function PreviewPage() {
  redirect("/whitepapers");
}
```

This avoids duplicate list implementations and keeps old preview links functional.

### 4. Remove preview-nav switching for that route in header/footer

If nav currently does this:

```tsx
href: t("/whitepapers", previewModeEnabled)
```

and the user wants `/t/whitepapers` removed from navigation, replace it with:

```tsx
href: "/whitepapers"
```

Important:
- only remove `t(...)` for the requested route
- keep preview-navigation behavior for other routes unless the user asked for a broader cleanup

### 5. Update tests and remove preview-only data/helpers

Typical affected tests:
- route-specific preview page test
- list-page source/loader test
- header/footer link integrity tests
- SEO/canonical tests if route metadata changed
- redirect-endpoint tests when the canonical public path used to be a `route.ts`

For the whitepaper rollout, useful updates were:
- if `/t/whitepapers` is removed, change `tests/t-whitepapers-page.test.mjs` to assert the preview route file no longer exists
- `tests/whitepaper-canonical-slug-routing.test.mjs`
  - assert `src/app/whitepapers/page.tsx` uses the local loader
  - assert the old preview route file and old external-link dataset file no longer exist
- `tests/link-and-metadata-integrity.test.mjs`
  - assert header/footer use `"/whitepapers"` directly instead of `t("/whitepapers", previewModeEnabled)`

For resource-family rollouts like `/resources`, `/introduction-deck`, `/glossary`, and `/manuals`, also update:
- tests that previously expected `src/app/<route>/route.ts` redirect files to exist
- tests that previously expected `/t/*` pages to render full content instead of redirecting
- sitemap tests so released public routes are included
- detail-route tests so the canonical family moves from `/t/<route>/**` to `/<route>/**`
- brittle string-matching tests may be safer with plain `source.includes(...)` assertions rather than hand-escaped regexes when verifying literal route snippets
- do not assume every resource family keeps the same `/t/*` compatibility policy; the user can want one family removed entirely while others still redirect
- if the user says a preview family such as `/t/glossary` will not be kept, remove the entire preview route family (`page.tsx`, `[id]/page.tsx`, `[id]/[slug]/page.tsx`) instead of converting it to redirects
- when doing that, update the route-family test so it asserts canonical public files exist and the whole `/t/<family>` tree is absent

Also check whether the old public-route implementation relied on a preview-only or external-link dataset.
In the whitepaper case, `src/lib/publications/querypie-ja-whitepaper-links.ts` was only a derived array that reused local whitepaper records but swapped each `href` to the upstream `querypie.com/ja` detail URL.
After promoting the local MDX-backed list to canonical, that module became dead code and should be deleted together with any now-stale imports in `src/content/resources.ts`, `src/lib/resource-posts.ts`, and related tests.

## Verification

At minimum run:

```bash
node --test tests/<route-test>.test.mjs tests/<list-test>.test.mjs tests/link-and-metadata-integrity.test.mjs tests/seo-metadata.test.mjs
npm run typecheck
```

Use targeted tests first when the change is narrowly scoped.

Also search for preview-route leftovers outside `src/app/` before finishing, especially:
- `docs/local-e2e.md`
- `tests-local/helpers/*`
- `tests-local/src/app/**`
- `package.json` local E2E scripts

If the promoted route already has local Playwright coverage under both `/t/*` and the canonical path, consolidate that coverage so the canonical path becomes the only maintained list-entry target.
For the news rollout, that meant:
- updating the shared fixture path from `/t/news` to `/news`
- moving the list-page assertions into `tests-local/src/app/news/page.e2e.mjs`
- deleting `tests-local/src/app/t/news/page.e2e.mjs`
- repointing `e2e:local:news-list:stage` to the canonical-file test target

## PR guidance

Recommended PR summary structure:
- replace public route with the local MDX-backed or local preview-backed implementation
- keep `/t/*` only as a redirect
- remove header/footer preview switching for that route

## Pitfalls

- Leaving the canonical public route on the old externalized list while only changing nav links
- Keeping both public and preview pages rendering the same list content independently
- In corp-web-japan, automatically leaving a redirect behind for a `/t/*` path without an explicit user request
- Forgetting to delete preview-only route/data modules after the canonical route stops using them
- Accidentally applying preview `robots: noindex,nofollow` to the canonical public page
- Removing `t(...)` preview switching from unrelated nav items
- Forgetting to update tests that still expect `/t/*` to render a full page

## Whitepaper-specific lesson learned

In corp-web-japan, `/whitepapers` and `/t/whitepapers` originally had intentionally different behaviors:
- `/whitepapers` used external `querypie.com/ja` links in the list
- `/t/whitepapers` used local MDX-derived list items

When promoting `/t/whitepapers` to canonical, first check whether `/t/whitepapers` actually needs compatibility.
If it was only an internal preview endpoint, the preferred outcome is:
- switch `src/app/whitepapers/page.tsx` to `listWhitepaperPublicationItems()`
- delete `src/app/t/whitepapers/page.tsx` instead of adding a redirect
- change header/footer whitepaper links to plain `"/whitepapers"`
- delete `src/lib/publications/querypie-ja-whitepaper-links.ts` if nothing else still needs the old external-link list
- remove any now-stale imports/usages in `src/content/resources.ts`, `src/lib/resource-posts.ts`, and related tests
- do not change other preview-switched nav entries unless explicitly requested

## Events-specific lesson learned

In corp-web-japan, promoting `/t/events` to canonical `/events` was not just a matter of removing the old launch gate from `src/app/events/page.tsx`.

Latest-main-safe rollout pattern:
- first compare the current public `/events` implementation against `src/app/t/events/page.tsx`
- if `/t/events` already contains the richer real list UX (for example upcoming featured event hero + past-events section), prefer promoting that implementation to `/events` instead of only ungating the old public shell
- after promotion, delete `src/app/t/events/page.tsx` entirely unless the user explicitly asks to preserve that preview endpoint
- update `src/app/sitemap.ts` to include `/events`
- update header/footer links and `ResourceCategorySidebar` event links to point directly at `/events` rather than using preview-only switching or `/t/events`
- rewrite source-based tests so they assert the canonical `/events` behavior and separately assert that `src/app/t/events/page.tsx` no longer exists

Practical heuristic:
- if the old public route only contains temporary readiness logic or a thinner shell, while the preview route contains the real canonical-ready UX, treat the task as a canonical promotion of the preview implementation, not as a one-line gate removal.
- this keeps the final route architecture cleaner and avoids leaving a duplicate preview list implementation behind.
