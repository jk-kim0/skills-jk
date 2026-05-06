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

Important scope guard learned from demo preview rollout follow-up work:
- Removing or promoting a specific preview route family such as `/t/use-cases`, `/t/demo/aip`, or `/t/demo/acp` does **not** by itself authorize removing the repository's broader Preview Toggle UI, preview-navigation API route, preview cookie flow, or other unrelated preview-only footer/header structures.
- Treat those as separate concerns unless the user explicitly says the global preview-toggle behavior itself should be removed.
- Safe default: keep the shared preview-navigation mechanism intact, and only remove the exact route entrypoints and the route-specific `/t/...` destinations that are no longer supposed to exist.
- In practice, if header/footer/resource sidebars still use Preview Toggle for other route families, preserve:
  - `src/components/layout/preview-mode-toggle.tsx`
  - `src/app/api/preview-navigation/route.ts`
  - server/client header glue such as `showPreviewModeToggle`
  - preview-only footer/internal sections that are controlled by the same toggle
- Only change those if the user explicitly expands scope beyond the rolled-out route family.

Preferred rollout:
1. move or copy the desired implementation into the canonical public route
2. decide explicitly whether the old `/t/*` path deserves compatibility at all
3. if the old preview path was never a public endpoint the user cares to preserve, delete that route instead of adding a redirect
4. only if the old preview path truly needs compatibility, turn it into a redirect to the canonical route
5. remove preview-navigation helper usage for that route in header/footer only when the user explicitly wants those navigation links made canonical for that surface
6. keep the global Preview Toggle / preview-navigation API / other preview-only footer or internal navigation intact unless the user explicitly asks to remove those broader preview features
7. update tests and delete only the preview-only helper/data files that existed solely for the removed `/t/*` route behavior

## Safe repo workflow

1. Start from latest `origin/main` in a fresh worktree.
2. Re-read the current public route, preview route, and nav files from that worktree before editing.
3. Confirm whether the public route already has canonical metadata that should be preserved.

## Files to inspect first

Typical files for this rollout:
- `src/app/<public-route>/page.tsx`
- `src/app/t/<route>/page.tsx`
- `src/components/layout/site-header-client.tsx`
- `src/components/layout/site-footer.tsx`
- `src/lib/preview-navigation.ts`
- related tests under `tests/`

For whitepaper rollout specifically, also inspect:
- `src/lib/publications/whitepaper-publication-records.ts`
- any tests covering list item source or route metadata

## Implementation pattern

### 1. Replace the public route with the local preview-backed implementation

Typical change:
- public route currently imports an externalized item list
- preview route currently imports the local loader

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

Ask this before preserving any compatibility endpoint:
- was the old `/t/*` path ever a public/external endpoint the user wants to preserve?
- or was it only an internal preview surface?

If it was only an internal preview surface, prefer deleting the route file entirely.

Typical deletion outcome:
- remove `src/app/t/<route>/page.tsx`
- remove tests that expect a rendered preview page and replace them with existence checks that confirm the file is gone
- remove any preview-only datasets or helper modules that existed only to feed that `/t/*` page

Only use a redirect when there is an actual compatibility need.

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

For the whitepaper rollout, useful updates were:
- if `/t/whitepapers` is removed, change `tests/t-whitepapers-page.test.mjs` to assert the preview route file no longer exists
- `tests/whitepaper-canonical-slug-routing.test.mjs`
  - assert `src/app/whitepapers/page.tsx` uses the local loader
  - assert the old preview route file and old external-link dataset file no longer exist
- `tests/link-and-metadata-integrity.test.mjs`
  - assert header/footer use `"/whitepapers"` directly instead of `t("/whitepapers", previewModeEnabled)`

Also check whether the old public-route implementation relied on a preview-only or external-link dataset.
In the whitepaper case, `src/lib/publications/querypie-ja-whitepaper-links.ts` was only a derived array that reused local whitepaper records but swapped each `href` to the upstream `querypie.com/ja` detail URL.
After promoting the local MDX-backed list to canonical, that module became dead code and should be deleted together with any now-stale imports in `src/content/resources.ts`, `src/lib/resource-posts.ts`, and related tests.

## Verification

At minimum run:

```bash
node --test tests/<route-test>.test.mjs tests/<list-test>.test.mjs tests/link-and-metadata-integrity.test.mjs tests/seo-metadata.test.mjs
npm run typecheck
```

Additional rollout lesson from the demo list public-route replacement work:
- when promoting a preview/demo list route to a canonical public endpoint, do not stop at the obvious route files, nav, sidebar, and sitemap.
- also search for downstream CTA constants and structure tests that may still encode the old redirect-style public path.
- in `corp-web-japan`, a concrete example was `src/content/home.ts` plus `tests/ai-crew-cta-links.test.mjs`, where the shared `demoUseCasesUrl` expectation still pointed at `/demo/use-cases` after the public list moved to `/use-cases`.
- practical rule: after changing a canonical list route, search both `src/` and `tests/` for the old path string and update route-authored CTA constants / source-based tests in the same PR.

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
- Automatically leaving a redirect behind for a `/t/*` path that was never a public endpoint the user cared about
- Forgetting to delete preview-only route/data modules after the canonical route stops using them
- Accidentally applying preview `robots: noindex,nofollow` to the canonical public page
- Removing `t(...)` preview switching from unrelated nav items
- Forgetting to update tests that still expect `/t/*` to render a full page
- Misreading a request to remove specific demo preview entrypoints as permission to remove the repo's broader Preview Toggle system
- Deleting global preview plumbing such as `src/components/layout/preview-mode-toggle.tsx`, `src/app/api/preview-navigation/route.ts`, preview-only footer Internal links, or other non-demo preview navigation behavior when the user only asked to roll out a narrow `/t/...` demo family

## PR 253 lesson: narrow demo preview rollout does not imply global preview-toggle removal

A concrete corp-web-japan lesson from PR 253 follow-up work:
- removing `/t/use-cases`, `/t/demo/aip`, and `/t/demo/acp` as list entrypoints did **not** mean the general Preview Toggle UI should be removed
- the correct scope was:
  - promote the demo list pages to their canonical public routes
  - delete only those specific `/t/...` demo list pages
  - keep the broader preview-navigation system intact for other preview surfaces unless the user explicitly asks to remove it

What to preserve unless explicitly told otherwise:
- `src/components/layout/preview-mode-toggle.tsx`
- `src/app/api/preview-navigation/route.ts`
- header wiring that passes and renders `showPreviewModeToggle`
- preview-only footer/internal navigation that depends on the general preview mode

Heuristic:
- if the user says to replace or remove a few `/t/...` routes, treat that as route-local rollout work first
- only remove global preview infrastructure when the user explicitly names the Preview Toggle or asks for broader preview-mode cleanup

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
