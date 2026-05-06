---
name: corp-web-japan-redirect-endpoints
description: Add temporary redirect endpoints in corp-web-japan using per-route App Router handlers, keep redirect rules local to each route directory, verify with a table-driven test, and avoid sitemap entries for redirect-only endpoints.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, Next.js, App Router, redirects, sitemap, PR workflow]
---

# corp-web-japan redirect endpoints

Use this when adding redirect-only public endpoints in `corp-web-japan`.

## When to use

- The user wants a public path in `src/app/**` that redirects elsewhere.
- The user explicitly prefers route-local redirect rules instead of a centralized `next.config` redirects table.
- The redirect should be temporary.

## Default approach

1. Start from a fresh worktree and fresh branch off `origin/main`.
2. Implement one `route.ts` per endpoint under `src/app/<path>/route.ts`.
3. Keep each endpoint's destination URL in that route file, not in a shared registry.
4. Use `NextResponse.redirect(destination, 307)`.
   - For external targets, `destination` can be an absolute string constant.
   - For same-origin local targets inside route handlers, do not pass a bare relative string such as `"/whitepapers/..."` directly. Build an absolute URL with `new URL(destinationPath, request.url)` first.
5. Export `HEAD = GET` so HEAD requests behave consistently.
6. Add or update a single table-driven test that lists all redirect rules in one place.
7. Do not add redirect-only endpoints to `src/app/sitemap.ts` unless the user explicitly asks for that behavior.
8. Verify with `npm run test:ci` and `npm run build`.
9. Push and open a Draft PR, then wait for CI to finish.

## Implementation pattern

Example route file:

```ts
import { NextResponse } from "next/server";

const destination = "https://www.querypie.ai/solutions/aip";

export function GET() {
  return NextResponse.redirect(destination, 307);
}

export const HEAD = GET;
```

If the redirect must preserve incoming query strings for downstream features such as contact-form prefills, switch to `NextRequest` and copy `request.nextUrl.search` onto the destination URL:

```ts
import { NextRequest, NextResponse } from "next/server";

const destination = new URL("https://www.querypie.com/ja/company/contact-us");

export function GET(request: NextRequest) {
  const redirectedUrl = new URL(destination);

  redirectedUrl.search = request.nextUrl.search;

  return NextResponse.redirect(redirectedUrl, 307);
}

export const HEAD = GET;
```

Use this query-preserving pattern when local `querypie.ai` endpoints should behave as thin pass-through aliases to `querypie.com/ja` while keeping repeated params and stable prefill keys intact.

If the redirect target is a same-origin local path rather than an external absolute URL, build it from `request.url` so the current host is preserved:

```ts
import { NextRequest, NextResponse } from "next/server";

export function GET(request: NextRequest) {
  const redirectedUrl = new URL("/", request.url);

  redirectedUrl.search = request.nextUrl.search;

  return NextResponse.redirect(redirectedUrl, 307);
}

export const HEAD = GET;
```

Use this same-origin pattern for lightweight alias routes created only to avoid 404s, such as redirecting `/ja` back to `/` on whatever host handled the request.

Important runtime lesson from the legacy whitepaper detail redirects on `stage.querypie.ai`:
- In App Router `route.ts` handlers, a same-origin relative string passed directly to `NextResponse.redirect()` can fail at runtime with errors like `URL is malformed` / `Please use only absolute URLs`.
- This is especially easy to miss when the intended canonical target itself is valid and returns 200, because the bug is in the redirect handler implementation rather than the destination content.
- For dynamic legacy detail redirects such as `/resources/discover/whitepapers/[id]/[slug] -> /whitepapers/:id/:slug`, prefer this pattern:

```ts
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const destinationPath = "/whitepapers";
  const destination = new URL(destinationPath, request.url);

  return NextResponse.redirect(destination, 307);
}
```

If the destination path is computed dynamically, compute the path string first, then wrap it with `new URL(destinationPath, request.url)` before calling `NextResponse.redirect()`.

If the requirement is to strip a legacy prefix from all nested paths, use an optional catch-all route such as `src/app/ja/[[...path]]/route.ts` and derive the redirect target from `request.nextUrl.pathname`:

```ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function GET(request: NextRequest) {
  const strippedPath = request.nextUrl.pathname.replace(/^\/ja(?=\/|$)/, "") || "/";
  const redirectedUrl = new URL(strippedPath, request.url);

  redirectedUrl.search = request.nextUrl.search;

  return NextResponse.redirect(redirectedUrl, 307);
}

export const HEAD = GET;
```

Use this catch-all prefix-stripping pattern when legacy URLs like `/ja`, `/ja/blog`, and `/ja/solutions/ai-crew` should all redirect to the same-origin canonical local path without the `/ja` prefix.

Recommended file layout:

- `src/app/services/aip/route.ts`
- `src/app/services/acp/route.ts`
- `src/app/services/fde/route.ts`

This keeps rule ownership at the route directory level.

Exact-match dotted paths are also valid route directories when the public URI literally includes an extension-like segment. For example, implement `/api-docs.html` as:

- `src/app/api-docs.html/route.ts`

Do not rename these to a normalized slug such as `/api-docs`; if the user asks for an exact-match redirect to fix a broken in-repo link, preserve the literal request path.

## Test pattern

Prefer one table-driven test file such as `tests/redirect-endpoints.test.mjs`.

Example structure:

```js
import test from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { readSource } from "./helpers/source-readers.mjs";

const expectedRedirectRules = [
  {
    requestPath: "/services/aip",
    file: "src/app/services/aip/route.ts",
    destination: "https://www.querypie.ai/solutions/aip",
  },
  {
    requestPath: "/services/acp",
    file: "src/app/services/acp/route.ts",
    destination: "https://www.querypie.ai/solutions/acp",
  },
];

test("redirect endpoints are defined in a single test-case table with temporary redirect destinations", () => {
  for (const rule of expectedRedirectRules) {
    assert.equal(existsSync(new URL(`../${rule.file}`, import.meta.url)), true);

    const source = readSource(rule.file);

    assert.match(source, /export function GET\(/);
    assert.match(source, /307/);
    assert.match(source, new RegExp(rule.destination.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
});
```

This gives reviewers one place to inspect the full redirect set without moving rule ownership out of the route files.

## Important pitfalls

- Do not silently change unrelated existing pages into redirects. Confirm with the user first if an existing `page.tsx` would need to be replaced.
- If you are confused about the exact request paths or destination URLs, ask the user before continuing.
- When the user provides a redirect rule table, interpret `Request Link` as the URI path on this website and `Target Link` as the redirect destination. Do not treat both columns as external destinations.
- In `corp-web-japan`, the site itself is served on `querypie.ai` / `www.querypie.ai`; only explicitly requested legacy or alias paths should redirect externally, while normal local pages should remain on the site.
- Do not assume `querypie.com/ja` vs `querypie.ai`; confirm the actual destination domain from the user or current product requirements.
- Do not add these redirect-only endpoints to `sitemap.ts` by default. Sitemap entries should usually represent canonical indexable URLs, not redirect hops.
- Before creating a new redirect route, check `origin/main` or a fresh worktree first. A matching endpoint may already exist and only need a small patch.
- If the endpoint already exists, prefer updating that route in place and extending the existing shared redirect test table rather than creating a duplicate route or a one-off test file.
- For `/contact-us` specifically, `origin/main` may already contain `src/app/contact-us/route.ts`; in that case only add query-string pass-through behavior and test assertions for `request.nextUrl.search`.

## Canonical endpoint naming guidance

When deciding whether a path should remain a local `page.tsx` or become a redirect endpoint, separate two decisions:
1. Is this path supposed to be a local canonical page on `querypie.ai`?
2. If it is canonical, what singular/plural form best matches the content model?

### Keep these as local canonical pages when they exist
- `/solutions/ai-crew`
- `/solutions/ai-dashi`
- `/demo/use-cases`
- `/blog`
- `/whitepapers`
- `/events` only when the events page is actually launched for public indexing

Important nuance learned from PR #71 / Issue #72 follow-up:
- Do not assume `/events` belongs in the sitemap just because the route exists locally.
- If the events page is still unpublished or guarded by a launch-readiness check, keep that gate in place and keep `/events` out of `src/app/sitemap.ts`.
- Do not rewrite an unpublished existing page into an always-public page unless the user explicitly asks for that launch behavior.
- For paths without existing local content such as `/resources`, `/manuals`, and `/glossary`, prefer redirect-only `route.ts` endpoints rather than creating new `page.tsx` files, unless the user explicitly asks for new local content pages.

### Naming rules
- Use plural paths for collection hubs whose names naturally represent multiple items:
  - `/demo/use-cases`
  - `/whitepapers`
  - `/events`
- Keep `blog` singular as a section noun:
  - `/blog`
- Keep `glossary` singular even when it contains many entries:
  - `/glossary`
- For multi-document manual hubs, prefer plural:
  - `/manuals` over `/manual`
- Avoid vague `material` as a canonical endpoint for a multi-document hub. Prefer a more precise name such as:
  - `/introduction-deck`
  - `/documents`
  - `/materials`
  in that order of preference depending on the actual content.

### Practical consequence
- Do not replace an existing correct canonical page such as `/demo/use-cases` or `/whitepapers` with a redirect just because a table contains a nearby singular variant.
- If the user says not to consider typo handling or legacy aliases, choose the strongest canonical name directly instead of adding alternate paths.
- If a page exists locally and is the intended canonical route but is not launched yet, keep the page metadata canonical aligned to that route, but do not add it to `src/app/sitemap.ts` until the user confirms it is publicly launch-ready.
- Treat endpoint-decision work separately from navigation copy work. Choosing `/resources`, `/manuals`, or `/glossary` as endpoint names does not by itself justify changing UI labels such as `全て` to `全てのリソース`, or adding new navigation items like `イベント`, unless the user explicitly asks for those UI/copy changes.
- When updating header/footer/sidebar links to use new endpoint paths, preserve existing labels by default and avoid broadening the visible IA beyond what the user requested.
- For legal-document redirects such as `/terms-of-service` and `/privacy-policy`, audit non-navigation consent surfaces too, especially `src/components/sections/resource-lead-form.tsx`. In this repo, legal links may exist outside header/footer/sidebar, so keep footer links and consent-form links aligned unless the user explicitly scopes the change to only one surface.
- If the user later provides an explicit Request Link -> Target Link mapping table, treat that table as the highest-priority source of truth for this task, even when it overrides an earlier canonical-endpoint discussion. In that case, convert any affected local pages into redirect `route.ts` endpoints, remove those redirect-only paths from `src/app/sitemap.ts`, and update tests to match the table.
- Do not keep arguing from a previously chosen canonical path once a concrete mapping table exists. If the table says `/demo/use-case` or `/introduction-deck`, follow that mapping for the requested implementation/review task even if an earlier discussion preferred `/demo/use-cases` or another resource-hub naming scheme.
- When applying a mapping table, review each row against the actual header/footer/sidebar surfaces and report mismatches separately for: request path, redirect target, hidden/gated state, and UI label copy. A path can be correct while the label is still wrong, and vice versa.

## Verification checklist

Run:

```bash
npm run test:ci
npm run build
```

If `npm run test:ci` fails for unrelated generated files under sibling worktrees such as `.worktrees/**/.next/**`, do not treat that as a regression in your redirect change. In `corp-web-japan`, this can happen because root-level linting may traverse neighboring worktree artifacts. In that case:

1. verify the changed files directly with targeted `eslint`
2. run targeted Node tests that cover the redirect/link updates
3. run `npm run typecheck`
4. run `npm run build`
5. report clearly that the full `test:ci` failure came from unrelated generated artifacts outside the modified path

Typical targeted commands:

```bash
npx eslint src/app/contact-us/route.ts src/components/layout/site-header.tsx src/components/layout/site-footer.tsx tests/link-and-metadata-integrity.test.mjs tests/redirect-endpoints.test.mjs
node --test tests/link-and-metadata-integrity.test.mjs tests/redirect-endpoints.test.mjs
npm run typecheck
npm run build
```

If you replaced an existing `page.tsx` with a `route.ts` redirect endpoint, clear the local build artifacts before verification if TypeScript still references the removed page through `.next/types/validator.ts`:

```bash
rm -rf .next
npm run test:ci
```

This avoids stale Next.js validator entries causing false typecheck failures after a route shape change.

Then create a Draft PR and monitor CI with `gh` using the required safe invocation form:

```bash
gh pr create --draft ...
gh pr checks <PR_NUMBER> --watch
```

## User preference reminder

If the intended redirect rules are unclear, stop and ask the user instead of guessing.
