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

## Service/detail-page and platform-landing rollout lesson learned

When publishing an individual service/detail preview page such as `/t/platforms/aip/usage-based-llm`, or a parent platform landing page such as `/t/platforms/aip`, treat the work as a route promotion plus endpoint-contract cleanup, not just a file move.

Typical pattern:
- move `src/app/t/platforms/<family>/<slug>/page.tsx` to `src/app/platforms/<family>/<slug>/page.tsx`, or for a platform landing page move `src/app/t/platforms/<family>/page.tsx` to `src/app/platforms/<family>/page.tsx`
- change metadata from preview to public:
  - `alternates.canonical` loses `/t`
  - `robots` changes from `{ index: false, follow: false }` to `{ index: true, follow: true }`
- add the new static public route to `src/app/sitemap.ts`
- remove the old `/t/*` page entirely unless the user explicitly requests a compatibility route
- if the public target currently has a `route.ts` external redirect, delete that public redirect file once the local `page.tsx` is published
- update header/footer navigation for the published route from `t("/platforms/<family>", previewModeEnabled)` to the direct canonical href, but leave unrelated preview-switched routes alone
- update parent preview/list cards that should now link to the published page, even if the parent page itself remains under `/t`
- when publishing the parent platform landing page, audit every linked card/inline link inside that page; child links that already went public should stay canonical, and service links such as FDE must use the public service route (`/services/fde`), not stale preview paths such as `/t/services/fde` or older AIP subpaths like `/platform/ai/aip/fde-services`
- if an older legacy route like `src/app/platform/ai/aip/<slug>/route.ts` still redirects to `www.querypie.com/ja/...`, retarget it to the new local canonical route instead of leaving the external redirect behind
  - for the AIP platform landing rollout, `src/app/platform/ai/aip/route.ts` should redirect internally to `/platforms/aip`
  - for the old AIP FDE subpath, `src/app/platform/ai/aip/fde-services/route.ts` should redirect internally to `/services/fde` after FDE is public; this avoids a broken or externally bounced FDE path from the AIP page
- after the AIP parent page is published at `/platforms/aip`, legacy parent aliases should also redirect locally, not upstream:
  - `src/app/services/aip/route.ts` -> `new URL("/platforms/aip", request.url)`
  - `src/app/platform/ai/aihub/route.ts` -> `new URL("/platforms/aip", request.url)`
  - keep them as alias redirects rather than creating duplicate pages
- if repo docs/audits track outstanding external QueryPie redirects, update the row/count for this now-local route so the audit remains truthful
  - concrete current examples: `docs/querypie-owned-link-audit.md` may have an "Expected current result: only the N route files below" count or a table of remaining external redirects. When publishing a route, remove rows whose redirects are now internal, update all affected summary/checklist counts, and if final runtime `src` references are removed, update the audit to say there should be no `https://www.querypie.com/ja` occurrences under runtime `src` files instead of preserving a stale "known redirect files" exception.
- update redirect tests to expect the local destination; if the redirect handler now needs `request.url` to build an internal URL, assert that shape through the existing redirect-endpoint test
- update the still-preview parent/list page links that point at the child page. For example, when `/t/platforms/aip/mcp-gateway` becomes `/platforms/aip/mcp-gateway`, keep `/t/platforms/aip` itself as preview if it is not being published, but change that card's `href` to the newly published child route.
- treat finite static product/detail pages such as `/platforms/aip`, `/platforms/aip/usage-based-llm`, and `/platforms/aip/mcp-gateway` as public indexability/list-route entries in `tests/publication-detail-indexability.test.mjs` if the existing test classifies them under `publicIndexableListRoutes` rather than MDX dynamic detail routes

### ACP platform parent + integrations rollout nuance

When publishing `/t/platforms/acp` and `/t/platforms/acp/integrations` together, promote only the requested two pages unless the user explicitly includes the ACP child controller pages.

Correct outcome for this narrow rollout:
- move `src/app/t/platforms/acp/page.tsx` to `src/app/platforms/acp/page.tsx`
- move `src/app/t/platforms/acp/integrations/page.tsx` to `src/app/platforms/acp/integrations/page.tsx`
- remove `src/app/platforms/acp/route.ts` because the canonical page now exists locally
- remove only the two old preview entrypoints (`/t/platforms/acp` and `/t/platforms/acp/integrations`); keep sibling child-controller preview routes such as `/t/platforms/acp/database-access-controller`, `/system-access-controller`, `/kubernetes-access-controller`, and `/web-access-controller` in place until their own rollout
- update the parent ACP page's integrations link from `/t/platforms/acp/integrations` to `/platforms/acp/integrations`
- update ACP integrations category links/query links from `/t/platforms/acp/integrations?...` to `/platforms/acp/integrations?...`
- retarget `src/app/services/acp/route.ts` internally to `new URL("/platforms/acp", request.url)` rather than leaving it as an external `www.querypie.com/ja/solutions/acp` redirect, but do not remove that route unless the user explicitly asks to remove the alias
- update header/footer nav from `t("/platforms/acp", previewModeEnabled)` to direct `"/platforms/acp"`
- add `/platforms/acp` and `/platforms/acp/integrations` to `src/app/sitemap.ts`
- add both public pages to `tests/publication-detail-indexability.test.mjs` and remove only the parent `/t/platforms/acp/page.tsx` from the non-indexable preview list
- move the parent mirrored test from `tests/src/app/t/platforms/acp/page.test.mjs` to `tests/src/app/platforms/acp/page.test.mjs`, fixing the helper import depth from `../../../../../helpers/...` to `../../../../helpers/...`
- add a focused `tests/src/app/platforms/acp/integrations/page.test.mjs` for public metadata, route-local catalog/filter links, CTA, and removed preview entrypoint
- keep `tests/src/app/t/platforms/acp/static-routes.test.mjs` for the remaining preview child-controller routes, but remove `integrations` from its preview route list and point its integrations assertions at the new public file
- in `tests/services-preview-routes.test.mjs`, `previewPages` may become an empty array after the last top-level platform preview page is promoted; keep the removed-preview-route assertions and make redirect-route assertions accept both external `const destination = ...` style and internal `new URL(..., request.url)` style redirects
- in `tests/redirect-endpoints.test.mjs`, remove the `/platforms/acp` external redirect row, decrement the expected redirect count, and assert the new public page exists while the old route/preview files do not
- if `docs/querypie-owned-link-audit.md` tracks remaining `www.querypie.com/ja` redirect shims, remove the `/platforms/acp` and `/services/acp` external rows, update counts, and note that `/services/acp` now redirects internally

### ACP child controller rollout nuance

When the user asks to publish the pages “under `/t/platforms/acp`” after the ACP parent and integrations pages are already public, first classify current main. If `src/app/platforms/acp/page.tsx` and `src/app/platforms/acp/integrations/page.tsx` already exist and the only remaining `/t/platforms/acp/**` files are the four child controller pages, treat the task as a child-controller rollout, not as a parent rollout redo.

Correct outcome for this child-controller rollout:
- move these four route directories from `src/app/t/platforms/acp/<route>/` to `src/app/platforms/acp/<route>/`:
  - `database-access-controller`
  - `system-access-controller`
  - `kubernetes-access-controller`
  - `web-access-controller`
- move their adjacent route README/render-audit notes with the route directories, and update stage/source paths inside those README files from `/t/platforms/acp/...` to `/platforms/acp/...`
- change each child page metadata:
  - `alternates.canonical` loses `/t`
  - `robots` changes from `{ index: false, follow: false }` to `{ index: true, follow: true }`
- remove the old `/t/platforms/acp/<route>` preview entrypoints entirely; do not leave `/t/*` compatibility redirects unless explicitly requested
- add the four canonical child paths to `src/app/sitemap.ts`
- retarget the matching legacy aliases under `src/app/platform/security/<route>/route.ts` from external `https://www.querypie.com/ja/solutions/acp/<route>` to same-origin internal redirects such as `new URL("/platforms/acp/database-access-controller", request.url)`; preserve `HEAD = GET`
- keep page assets route-aligned under `public/platforms/acp/<route>/...`; do not move assets during rollout unless explicitly requested
- update `tests/publication-detail-indexability.test.mjs` so the four child pages are public indexable list/static routes
- move the mirrored static route test from `tests/src/app/t/platforms/acp/static-routes.test.mjs` to `tests/src/app/platforms/acp/static-routes.test.mjs`, and rewrite its assertions from preview/noindex paths to public/indexable paths while preserving existing structure/copy/visual-contract assertions
- update `tests/services-preview-routes.test.mjs`, `tests/redirect-endpoints.test.mjs`, and `tests/canonical-endpoints.test.mjs` to assert the old `/t/platforms/acp/<route>/page.tsx` files are absent and the new canonical files/redirect targets/sitemap entries exist
- if docs track external links, update `docs/querypie-owned-link-audit.md` counts and remove the four ACP child `www.querypie.com/ja` redirect rows; update `docs/external-link-audit.md` rows from preview `/t/platforms/acp/<route>` to public `/platforms/acp/<route>`

Focused verification for this child-controller rollout:
```bash
node --test \
  tests/src/app/platforms/acp/static-routes.test.mjs \
  tests/publication-detail-indexability.test.mjs \
  tests/canonical-endpoints.test.mjs \
  tests/redirect-endpoints.test.mjs \
  tests/services-preview-routes.test.mjs
node scripts/ci/assert-test-groups.mjs
git diff --check
```

Rebase pitfall:
- ACP rollout PRs often overlap with other finite-route rollouts in `tests/canonical-endpoints.test.mjs`, `tests/publication-detail-indexability.test.mjs`, `tests/redirect-endpoints.test.mjs`, and `src/app/sitemap.ts`.
- If latest `origin/main` added another rollout such as `/plans`, resolve conflicts by preserving both the main-side public route assertions and the ACP child-route assertions. Do not drop the other rollout's sitemap/canonical/removed-preview checks while applying the ACP child rollout.
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
- if the rollout is a parent landing page, source test also confirms `src/app/platforms/<family>/route.ts` is absent, metadata is canonical/indexable, and all in-page card/inline hrefs use public canonical destinations
- for AIP platform landing rollout specifically, grep runtime `src/**` for stale `href="/t/platforms/aip`, `href="/t/services/fde`, and `https://www.querypie.com/ja/solutions/aip/fde-services`; only absence assertions in tests/docs should remain, not rendered links
- `publication-detail-indexability.test.mjs` or the relevant SEO/indexability test includes the new public route and no longer lists the old preview route as non-indexable
- `services-preview-routes.test.mjs` or equivalent removed-preview-route contract includes the deleted `/t/*` file path
- `redirect-endpoints.test.mjs` no longer asserts the old public redirect and instead asserts the new canonical page file exists while the old `route.ts` does not; legacy aliases that now point internally should use `new URL("/<canonical>", request.url)`
- negative grep for the old `/t/<path>` should only return tests that assert absence, not rendered links or docs that still describe it as current
- preview deployment smoke: canonical URL returns 200, old `/t/*` URL returns 404, and legacy redirect URL resolves to the canonical local route

## Plans finite-route rollout lesson learned

When publishing the finite static plans routes from `/t/plans`, `/t/plans/aip`, and `/t/plans/acp` to `/plans`, `/plans/aip`, and `/plans/acp`, treat it as a straight route promotion, not as a content or layout refactor.

Correct narrow rollout pattern:
- move `src/app/t/plans/page.tsx` to `src/app/plans/page.tsx`
- move explicit sibling route directories `src/app/t/plans/aip/` and `src/app/t/plans/acp/` to `src/app/plans/aip/` and `src/app/plans/acp/`
- remove the old `/t/plans*` route files entirely unless the user explicitly requests preview compatibility redirects
- change metadata canonical paths from `/t/plans*` to `/plans*`
- change robots from `{ index: false, follow: false }` to `{ index: true, follow: true }`
- preserve the existing finite explicit route shape; do not introduce `src/app/plans/[product]/page.tsx`
- keep the root `/plans` behavior that renders the AIP page by default and redirects legacy query-tab URLs like `?acp` / `?aip` to `/plans/acp` / `/plans/aip`
- when moving the root route, make the legacy query redirect target absolute-rooted (`/plans/${product}`), not relative (`plans/${product}`), so tests and route intent stay unambiguous
- add `/plans`, `/plans/aip`, and `/plans/acp` to `src/app/sitemap.ts`
- move the mirrored source test from `tests/src/app/t/plans/page.test.mjs` to `tests/src/app/plans/page.test.mjs`, fix the helper import depth, and keep its route-local pricing/table primitive assertions intact
- update `tests/publication-detail-indexability.test.mjs` by moving the plans files from the non-indexable preview list to the public indexable list
- update broad route/sitemap tests such as `tests/canonical-endpoints.test.mjs` to assert the new canonical paths, sitemap entries, and absence of old `/t/plans*` files
- update source/path tests such as `tests/static-page-mobile-container-contract.test.mjs` from `src/app/t/plans/*` to `src/app/plans/*`
- update `scripts/ci/test-groups.mjs` when the mirrored test moves out from `tests/src/app/t/plans/` to `tests/src/app/plans/`

Focused verification for this class:
```bash
node --test \
  tests/src/app/plans/page.test.mjs \
  tests/static-page-mobile-container-contract.test.mjs \
  tests/publication-detail-indexability.test.mjs \
  tests/canonical-endpoints.test.mjs
node scripts/ci/assert-test-groups.mjs
```

## Test relocation and shard-assignment pitfall

If a route-source test mirrors the old preview path under `tests/src/app/t/...` and you promote the page to a canonical non-`/t` path, do not only rename/move the source route file.

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

### Import depth fix for moved tests

When a test moves from `tests/src/app/t/<family>/<page>/page.test.mjs` to `tests/src/app/<family>/<page>/page.test.mjs`, the relative path to `tests/helpers/source-readers.mjs` changes because the `/t/` segment is removed.

Concrete example from AIP integrations rollout:
- old path: `tests/src/app/t/platforms/aip/integrations/page.test.mjs`
- new path: `tests/src/app/platforms/aip/integrations/page.test.mjs`
- old import: `import { readSource } from "../../../../../../helpers/source-readers.mjs";` (6 levels up from `tests/src/app/t/platforms/aip/integrations/`)
- new import: `import { readSource } from "../../../../../helpers/source-readers.mjs";` (5 levels up from `tests/src/app/platforms/aip/integrations/`)

Verification: run the moved test in isolation before pushing:
```bash
node --test tests/src/app/<family>/<page>/page.test.mjs
```

If it fails with `ERR_MODULE_NOT_FOUND`, the import depth is wrong. Fix by counting directory levels from the test file to `tests/helpers/`.

## Rebase-conflict pitfall for overlapping rollout PRs

When two preview-route-rollout PRs both touch the same shared test files — typically `tests/publication-detail-indexability.test.mjs`, `tests/redirect-endpoints.test.mjs`, `tests/services-preview-routes.test.mjs`, or `tests/canonical-endpoints.test.mjs` — rebasing the later PR onto latest main (after the earlier PR merged) almost always produces content conflicts in the list/array blocks.

The conflict pattern is:
- The earlier merged PR added/removed entries in `publicIndexableListRoutes`, `nonIndexableRoutes`, `expectedRedirectRules`, etc.
- The later rebasing PR also adds/removes entries in the same arrays.
- Git cannot auto-merge because both PRs touched adjacent or overlapping lines.

Resolution rule:
- Include **both** the main-side additions (from the already-merged PR) and the PR-side additions (from the current rebasing PR).
- Do not drop the other PR's changes while resolving.
- If both PRs added new public routes to `publicIndexableListRoutes`, keep both.
- If both PRs removed preview routes from `nonIndexableRoutes`, remove both.
- If both PRs changed the `expectedRedirectRules` count assertion, the final count must reflect **both** removals.

Quick rebase workflow when an editor prompt would block automation:
```bash
# after fixing conflicts manually:
GIT_EDITOR=true git rebase --continue
```

This avoids getting stuck in Vim when the commit message does not need editing.

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

## Plans-specific rollout lesson learned

When publishing the finite pricing/plans preview routes, treat `/t/plans`, `/t/plans/aip`, and `/t/plans/acp` as one route family:
- move the explicit sibling App Router files to `src/app/plans/page.tsx`, `src/app/plans/aip/page.tsx`, and `src/app/plans/acp/page.tsx`
- do not replace the explicit `aip` / `acp` siblings with a dynamic `[product]` route during rollout
- keep the root `/plans` page rendering the default AIP view while preserving legacy product query redirects such as `?acp` and `?aip`; after rollout those redirects must target absolute path strings like `/plans/acp`, not route-relative `plans/acp`
- update metadata canonical paths from `/t/plans*` to `/plans*` and change robots from non-indexable preview to public indexable
- add `/plans`, `/plans/aip`, and `/plans/acp` to `src/app/sitemap.ts`
- remove the old `/t/plans*` route files entirely unless the user explicitly requests compatibility redirects
- move the mirrored source test from `tests/src/app/t/plans/page.test.mjs` to `tests/src/app/plans/page.test.mjs`, fix the helper import depth, and update `scripts/ci/test-groups.mjs`
- update source/indexability/canonical tests so the canonical pages are public/indexable and old `/t/plans*` files are absent
- if the user asks for a legacy `/pricing` alias in the same PR, add `src/app/pricing/route.ts` as a route-local same-origin redirect to `/plans`, preserve `request.nextUrl.search`, export `HEAD = GET`, and add it to `tests/redirect-endpoints.test.mjs` without adding `/pricing` to the sitemap

Verification checklist for this pattern:
```bash
node --test tests/redirect-endpoints.test.mjs tests/src/app/plans/page.test.mjs tests/publication-detail-indexability.test.mjs tests/canonical-endpoints.test.mjs
node scripts/ci/assert-test-groups.mjs
```

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
