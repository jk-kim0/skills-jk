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

## Do not confuse preview taxonomy rename with public rollout

A route-family rename can be a preview-only taxonomy step, not a public release.
Before applying this skill's canonical-promotion behavior, confirm whether the current task is actually public rollout.

If the user says the public release or `/t/*` removal is a final/later stage:
- do **not** create public `src/app/<route>/page.tsx` files yet
- do **not** remove the `/t/*` preview system globally
- do **not** add compatibility redirects for old preview routes unless explicitly requested
- do rename the preview route files/tests directly, e.g. `/t/services/aip` -> `/t/platforms/aip`
- update preview canonical metadata to the new `/t/...` path
- update header/footer `t("/<public-target>", previewModeEnabled)` base paths only if the user confirmed the new eventual public target
- keep existing public redirect routes unchanged when the user says public redirects are not part of the current PR

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
4. If the user explicitly asks to be questioned and confirmed before proceeding with naming/route decisions, gather all decision questions first and stop before file edits. Do not start implementing after only one confirmed item when other route-policy choices remain open.

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

### Legal-page SEO exposure parity

When publishing legal or policy pages from `/t/*` to canonical public routes, do not assume every newly public route should be added to `src/app/sitemap.ts` or removed from `robots.ts` restrictions.

First audit the current `www.querypie.com/ja` behavior and mirror it deliberately:

```bash
python3 - <<'PY'
import re, urllib.request
paths=['/ja/cookie-preference','/ja/terms-of-service','/ja/privacy-policy','/ja/eula']
base='https://www.querypie.com'

def fetch(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 Hermes SEO audit'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.geturl(), r.headers, r.read().decode('utf-8','replace')

for p in ['/robots.txt','/sitemap.xml']:
    st,u,h,body=fetch(base+p)
    print('\n==', p, st, u)
    for legal in paths:
        print(legal, legal in body or base+legal in body)
    if p == '/robots.txt':
        print('\n'.join(body.splitlines()[:80]))

for p in paths:
    st,u,h,body=fetch(base+p)
    print('\n==', p, st, u)
    print('x-robots-tag:', h.get('x-robots-tag'))
    print('meta robots:', re.findall(r'<meta[^>]+name=["\\']robots["\\'][^>]*>', body, re.I)[:3])
    print('canonical:', re.findall(r'<link[^>]+rel=["\\']canonical["\\'][^>]*>', body, re.I)[:3])
PY
```

Practical result observed during legal-page publish work:
- `www.querypie.com/sitemap.xml` includes `/ja/cookie-preference` and `/ja/eula`, but not `/ja/terms-of-service` or `/ja/privacy-policy`.
- `www.querypie.com/robots.txt` disallows `/ja/terms-of-service` and `/ja/privacy-policy`.
- The live legal page HTML still uses meta robots `index, follow` on all four pages.

For corp-web-japan, the matching implementation is:
- keep `/cookie-preference` and `/eula` in `src/app/sitemap.ts`
- exclude `/terms-of-service` and `/privacy-policy` from `src/app/sitemap.ts`
- add `disallow: ["/privacy-policy", "/terms-of-service"]` to `src/app/robots.ts`
- keep page-level metadata as `robots: { index: true, follow: true }` for all four pages, matching the live HTML meta robots contract
- update `tests/seo-metadata.test.mjs`, `tests/canonical-endpoints.test.mjs`, and launch-readiness/indexability tests so sitemap inclusion/exclusion and robots disallow are asserted explicitly

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

## Mixed-state batch rollout rule

When the user asks to "release" several `/t/*`-related pages together in one PR, do not assume every named page still needs the same class of code change.

First inspect each requested surface and classify it into one of these buckets:
- already canonical public page exists and `/t/*` preview is already gone
- canonical public page exists but some docs/tests/navigation still describe it as preview-only
- public route is still a redirect or legacy endpoint while `/t/*` contains the real implementation

Execution rule for this repo/user:
- keep the user-requested single PR when the rollout theme is still one homogeneous release batch
- only promote the pages that still need promotion
- for pages that are already canonical, limit the diff to truth-alignment work such as README/docs/tests if they still describe the old preview state
- explicitly report that distinction to the user so they know why some named pages got code changes and others only got validation/alignment

Practical example:
- user requests `about-us`, `news`, `contact-us`, and `certifications` in one production-release PR
- latest `main` already has canonical `/news` and `/contact-us`
- only `/about-us` and `/certifications` still need route promotion from `/t/*`
- the correct PR still stays combined, but code promotion is limited to those two pages while tests/docs are updated to reflect that `news` and `contact-us` were already released

## Service/detail-page rollout lesson learned

When publishing an individual service/detail preview page such as `/t/platforms/aip/usage-based-llm`, treat the work as a route promotion plus endpoint-contract cleanup, not just a file move.

Typical pattern:
- move `src/app/t/platforms/<family>/<slug>/page.tsx` to `src/app/platforms/<family>/<slug>/page.tsx`
- change metadata from preview to public:
  - `alternates.canonical` loses `/t`
  - `robots` changes from `{ index: false, follow: false }` to `{ index: true, follow: true }`
- add the new static public route to `src/app/sitemap.ts`
- remove the old `/t/*` page entirely unless the user explicitly requests a compatibility route
- update parent preview/list cards that should now link to the published page, even if the parent page itself remains under `/t`
- if an older legacy route like `src/app/platform/ai/aip/<slug>/route.ts` still redirects to `www.querypie.com/ja/...`, retarget it to the new local canonical route instead of leaving the external redirect behind
- if repo docs/audits track outstanding external QueryPie redirects, update the row/count for this now-local route so the audit remains truthful
  - concrete current example: `docs/querypie-owned-link-audit.md` has an "Expected current result: only the N route files below" count plus one table row per remaining external redirect; when publishing a detail page, remove its external row and decrement the count in the same PR
- update redirect tests to expect the local destination; if the redirect handler now needs `request.url` to build an internal URL, assert that shape through the existing redirect-endpoint test
- update the still-preview parent/list page links that point at the child page. For example, when `/t/platforms/aip/mcp-gateway` becomes `/platforms/aip/mcp-gateway`, keep `/t/platforms/aip` itself as preview if it is not being published, but change that card's `href` to the newly published child route.
- treat finite static product/detail pages such as `/platforms/aip/usage-based-llm` and `/platforms/aip/mcp-gateway` as public indexability/list-route entries in `tests/publication-detail-indexability.test.mjs` if the existing test classifies them under `publicIndexableListRoutes` rather than MDX dynamic detail routes

For service landing pages that replace a public `route.ts` redirect (e.g. `/services/fde` replacing an upstream redirect), also clean up:
- `tests/redirect-endpoints.test.mjs`: remove the corresponding redirect rule object from `expectedRedirectRules`, decrement the total count assertion, and add rollout assertions such as:
  ```js
  test("/t/services/fde preview entrypoint has been removed after public rollout", () => {
    assert.equal(existsSync(new URL("../src/app/t/services/fde/page.tsx", import.meta.url)), false);
  });
  test("/services/fde is now a local public page and replaces the old redirect", () => {
    assert.equal(existsSync(new URL("../src/app/services/fde/page.tsx", import.meta.url)), true);
    assert.equal(existsSync(new URL("../src/app/services/fde/route.ts", import.meta.url)), false);
  });
  ```
- `tests/services-preview-routes.test.mjs`: remove the rolled-out preview page from `previewPages` and its corresponding redirect route from `redirectRoutes`
- `tests/preview-navigation-path-helper.test.mjs`: do **not** remove or change; the `t()` helper itself continues to work unchanged even after a specific route is rolled out

Verification checklist for this pattern:
- source test confirms the canonical `src/app/platforms/.../page.tsx` exists and the old `src/app/t/platforms/.../page.tsx` is absent
- `publication-detail-indexability.test.mjs` or the relevant SEO/indexability test includes the new public route and no longer lists the old preview route as non-indexable
- `services-preview-routes.test.mjs` or equivalent removed-preview-route contract includes the deleted `/t/*` file path
- `redirect-endpoints.test.mjs` no longer asserts the old public redirect and instead asserts the new canonical page file exists while the old `route.ts` does not
- negative grep for the old `/t/<path>` should only return tests that assert absence, not rendered links or docs that still describe it as current
- preview deployment smoke: canonical URL returns 200, old `/t/*` URL returns 404, and legacy redirect URL resolves to the canonical local route

## Test relocation and shard-assignment pitfall

If a route-source test mirrors the old preview path under `tests/src/app/t/...` and you promote the page to a canonical non-`/t` path, do not only rename the source route file.

### Preserve the old test's assertion content

When moving the test file, keep the existing assertion content and adapt it for the public route — do not delete the old assertions and write a thin replacement from scratch.

Adaptation checklist:
- `canonical: "/t/..."` → `canonical: "/..."` (remove `/t` prefix)
- `robots: { index: false, follow: false }` → `robots: { index: true, follow: true }`
- Add assertions that the old `route.ts` redirect is gone: `sourceExists("src/app/<route>/route.ts") === false`
- Add assertions that the old `/t/*` preview route is gone: `sourceExists("src/app/t/<route>/page.tsx") === false`
- Keep all existing section/layout primitive contract assertions (hero spacing, feature bands, CTA, image paths, asset existence, etc.)
- If the only differences are metadata route and robots flags, amend the existing test in place rather than rewriting it

This ensures the public route test is just as comprehensive as the preview test it replaces.

Also update all of the following in the same PR:
- move the mirrored source-based test file to the canonical path under `tests/src/app/...`
- fix the moved test's relative import path to shared helpers such as `tests/helpers/source-readers.mjs`
- update `scripts/ci/test-groups.mjs` so the new test path still matches the intended shard/group
- remove the old preview-path test file instead of leaving both copies behind

Failure signatures if missed:
- `ERR_MODULE_NOT_FOUND` from the moved test because the old `../../../../helpers/...` import depth is no longer correct
- `AssertionError [ERR_ASSERTION]: Unassigned test files:` from `node scripts/ci/assert-test-groups.mjs`

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

## Preview taxonomy rename is not public rollout

When the user asks to rename `/t/*` preview routes as part of route taxonomy planning, do **not** treat it as a public-route rollout or as authorization to remove all preview endpoints.

Before editing, explicitly confirm all naming/canonical decisions that materially affect route files, nav links, aliases, and tests. Do not ask one question, get one answer, and then proceed if other route-policy decisions remain open.

For a preview-only rename stage:
- move the existing preview route files to the new `/t/...` paths
- update `metadata.alternates.canonical` to the new preview paths
- update preview-navigation base links when the new public target taxonomy is already confirmed (for example `t("/platforms/aip", previewModeEnabled)`)
- remove the old preview route files without adding compatibility redirects when the user says old preview routes should simply be renamed
- keep existing public redirect routes unchanged unless the user explicitly includes public release in the current scope
- do not create new public `page.tsx` files just because the future canonical public paths are known
- do not create AIP child routes the user explicitly excludes (for example no `/platforms/aip/fde-services` when FDE stays under `/services/fde`)

After renaming mirrored test paths under `tests/src/app/t/...`, update both CI routing and test assignment helpers if they enumerate those paths:
- `.github/workflows/ci.yml` changed-scope filters
- `scripts/ci/test-groups.mjs`
- run `node scripts/ci/assert-test-groups.mjs`

## Pitfalls

- Treating a `/t/*` preview taxonomy rename as a public release/promotion task
- Removing or redirecting preview routes before the planned final public release stage
- Proceeding after only one naming answer when related route-policy questions are still unsettled
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

## Legal-page rollout lesson learned

When the user asks to publish legal pages by removing `/t/` from routes such as `/t/privacy-policy`, treat it as a combined legal-surface rollout, not as a content rewrite.

Current corp-web-japan legal rollout pattern:
- move the existing local page implementations from:
  - `src/app/t/cookie-preference/page.tsx` -> `src/app/cookie-preference/page.tsx`
  - `src/app/t/terms-of-service/page.tsx` + `content.mdx` -> `src/app/terms-of-service/`
  - `src/app/t/privacy-policy/page.tsx` and `[slug]/page.tsx` -> `src/app/privacy-policy/`
  - `src/app/t/eula/page.tsx` + `content.mdx` -> `src/app/eula/`
- delete the old public external redirect handlers such as `src/app/privacy-policy/route.ts`, not just shadow them with a page file
- unless explicitly requested, do not keep `/t/*` compatibility redirects for these published legal pages
- change footer legal links to direct canonical hrefs rather than `t("/privacy-policy", previewModeEnabled)` etc.; other non-legal preview-switched navigation can remain unchanged
- update privacy-policy version selector navigation from `/t/privacy-policy/${nextSlug}` to `/privacy-policy/${nextSlug}`
- update `src/app/sitemap.ts` for the newly published legal pages
- make published legal metadata canonical and indexable (`robots: { index: true, follow: true }`) where the page owns metadata directly; for privacy-policy, the alias page may delegate to the shared `generatePrivacyPolicyMetadata` helper, so source tests should assert delegation plus the helper's indexable robots rather than requiring a literal `robots` block in the alias file
- move mirrored tests from `tests/src/app/t/<route>/page.test.mjs` to `tests/src/app/<route>/page.test.mjs` and fix relative helper imports
- update `scripts/ci/test-groups.mjs` whenever these mirrored tests move out from under `tests/src/app/t/`
- run a negative grep for old legal preview/external targets before finishing:
  - `/t/(cookie-preference|terms-of-service|privacy-policy|eula)`
  - `src/app/t/(cookie-preference|terms-of-service|privacy-policy|eula)`
  - `t("/(cookie-preference|terms-of-service|privacy-policy|eula)`
  - `www.querypie.com/ja/(cookie-preference|terms-of-service|privacy-policy|eula)`

Docs pitfall:
- if route-aligned authoring docs contain commit-pinned GitHub links to the old `/t/*` legal examples, do not mechanically rewrite the URL path while leaving the old commit SHA; that creates broken historical links. Prefer repo-relative links for newly moved examples, or update to a commit that actually contains the moved paths after the PR lands.
