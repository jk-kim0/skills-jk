---
name: nextjs-vercel-runtime-404-observability
description: Investigate why 404s are missing from Vercel Runtime Logs in a Next.js App Router project, and make unmatched page requests visible in runtime logs without changing the final 404 response.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, vercel, runtime-logs, 404, observability, app-router]
---

# Next.js + Vercel runtime 404 observability

Use this when:
- Users report real 404 pages, but `vercel logs` shows `404 = 0`
- A Next.js App Router site on Vercel appears to hide some missing-page traffic from Runtime Logs
- You need 404 requests to remain 404s for users but also appear in Runtime Logs for investigation

## Core finding

On Vercel, some missing-path requests can be handled by edge/static 404 behavior instead of an application runtime invocation.

When that happens:
- users still see a real `404`
- but Vercel Runtime Logs may have no entry for that request

This is especially likely when:
- no page/route handler matches the request
- no middleware/runtime code runs for that path
- Vercel serves the fallback 404 without a function invocation

## Key documentation finding

Vercel Runtime Logs include:
- function invocations
- routing middleware invocations
- only limited static request visibility

Practical implication:
- Runtime Logs are not a full access log
- use Log Drains or another request/access source if you need every static/edge miss

## Reliable fix for page-like missing routes

For a Next.js App Router site, add a root catch-all page route that:
1. runs in runtime
2. logs the requested unmatched path
3. then calls `notFound()`

Pattern:

```tsx
import { headers } from "next/headers";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function MissingRoutePage({
  params,
}: {
  params: Promise<{ missing: string[] }>;
}) {
  const { missing } = await params;
  const requestHeaders = await headers();
  const requestedPath = `/${missing.join("/")}`;

  console.log(
    "[runtime-404]",
    JSON.stringify({
      requestedPath,
      host: requestHeaders.get("host"),
      referer: requestHeaders.get("referer"),
      userAgent: requestHeaders.get("user-agent"),
    }),
  );

  notFound();
}
```

Recommended file:
- `src/app/[...missing]/page.tsx`

Why it works:
- the catch-all page forces the unmatched request through the application runtime
- the runtime invocation produces a Runtime Log entry
- `notFound()` still preserves the final `404` response

## Important route-precedence lesson

If your app already has route handlers that match a locale/prefix path before the catch-all page does, those routes must be updated separately.

Example:
- `src/app/ja/[[...path]]/route.ts` will intercept `/ja/...`
- in that case, fixing only `src/app/[...missing]/page.tsx` is not enough for `/ja/...`

You must audit higher-priority route handlers and apply the intended redirect/404 logic there too.

## Verification workflow

### 1. Verify the current blind spot

Trigger a known missing path:

```bash
curl -I https://your-site.example/__hermes-vercel-log-test-404
```

Then query recent logs:

```bash
vercel logs --project <project> --environment production --since 5m --json --no-branch --limit 200
```

If the request returns `404` but no matching log entry appears, you likely have the edge/static blind spot.

### 2. Verify the fix locally

After adding the catch-all page:

```bash
npm test
npm run typecheck
npm run build
npm run start -- --port 3012
curl -I http://127.0.0.1:3012/__hermes-vercel-log-test-404
```

Expected:
- response is `404`
- app log contains `[runtime-404]`

### 3. Verify the fix on Vercel

If project Git deployments are disabled, branch pushes may not create a preview deployment automatically.

In that case:

```bash
vercel pull --yes --environment=preview
vercel build
vercel deploy --prebuilt --yes --no-wait
vercel inspect <preview-url> --wait --timeout 25s --format json
```

Then trigger a missing path on the preview URL and query preview logs:

```bash
vercel logs --project <project> --environment preview --since 10m --status-code 404 --json --no-branch --limit 50
```

Expected after the fix:
- missing request still returns `404`
- Runtime Logs show that path with source `serverless`
- log message includes `[runtime-404]`

## Vercel project deployment caveat

If `vercel.json` contains:

```json
"git": {
  "deploymentEnabled": false
}
```

then:
- pushing a branch will not automatically produce a Vercel preview deployment for verification
- manual CLI deploy may be required during investigation

Useful pattern:
1. `vercel pull`
2. `vercel build`
3. `vercel deploy --prebuilt`

This was necessary in `corp-web-japan` to verify the runtime-404 behavior end-to-end.

## Operational interpretation after the fix

Once the catch-all runtime logging is in place, the Runtime Logs become useful for classifying missing traffic into:
- true runtime-visible 404s (`[runtime-404]`)
- runtime-visible redirects for normalized missing paths (for example `[runtime-missing-redirect]` if you add that behavior)

At that point, the main question shifts from:
- “why are 404s invisible?”

to:
- “which requests remain 404 and which are intentionally redirected?”

## Pitfalls

- Do not assume `404 = 0` in Runtime Logs means users saw no 404s
- Do not forget route precedence: locale/prefix route handlers can bypass the catch-all page
- Do not verify only locally; confirm behavior on a real Vercel deployment when the issue is about Vercel Runtime Logs
- Do not mistake Runtime Logs for full access logs; use Log Drains if complete request visibility is required

## Good evidence to collect in reports

- example request path that returned `404`
- proof that it was previously absent from Runtime Logs
- the exact catch-all route added
- local verification result (`404` + `[runtime-404]`)
- preview/production verification result (`404` + log row visible)
- any route-precedence exceptions such as locale catch-all routes
