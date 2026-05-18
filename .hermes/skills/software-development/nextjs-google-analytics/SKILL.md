---
name: nextjs-google-analytics
description: Add or audit Google Analytics / gtag.js in Next.js App Router sites, including hardcoded GA4 IDs, production-only loading, route-change tracking, and CI source tests.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, google-analytics, gtag, app-router, analytics, performance]
---

# Next.js Google Analytics / gtag.js

Use this when adding, auditing, or fixing Google Analytics in a Next.js App Router website, especially when the user wants a code-level GA4 measurement ID rather than environment-variable configuration.

## Core approach

1. Confirm the framework and routing model:
   - Inspect `package.json` for `next` version.
   - Inspect `src/app/layout.tsx` for the root layout.
   - Search for existing analytics implementations before adding a new one: `gtag`, `googletagmanager`, `GoogleAnalytics`, `next/script`, `@next/third-parties`.

2. Prefer a small analytics component over inline snippets in `layout.tsx`:
   - `src/components/analytics/google-analytics.tsx` for script loading and GA ID.
   - `src/components/analytics/google-analytics-page-view-tracker.tsx` for App Router client navigation events.
   - Mount `<GoogleAnalytics />` exactly once in the root layout body.

3. If the user asks for code configuration / hardcoding, use a code constant:

```tsx
const GA_MEASUREMENT_ID = "G-XXXXXXXXXX";
```

Do not add or depend on `NEXT_PUBLIC_*` env vars for that task unless the user explicitly switches requirements.

4. Use `next/script` with `strategy="afterInteractive"`:
   - Good balance for GA reliability and performance.
   - Avoids blocking initial HTML rendering.
   - Avoid `lazyOnload` when reliable first-visit pageview capture is more important than delaying analytics.

5. Production-only loading:
   - Reuse the repo's existing production detection helper if one exists.
   - In corp-web-japan specifically, use `src/lib/is-production.ts`; do not introduce a new production check.
   - If no helper exists, prefer a single shared helper based on the deployment platform's explicit production signal instead of ad hoc branch-name checks.

## Recommended implementation

`src/components/analytics/google-analytics.tsx`:

```tsx
import { Suspense } from "react";
import Script from "next/script";
import isProduction from "@/lib/is-production";
import { GoogleAnalyticsPageViewTracker } from "./google-analytics-page-view-tracker";

const GA_MEASUREMENT_ID = "G-XXXXXXXXXX";

export function GoogleAnalytics() {
  if (!isProduction()) {
    return null;
  }

  return (
    <>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
        strategy="afterInteractive"
      />
      <Script id="google-analytics-init" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){window.dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA_MEASUREMENT_ID}');
        `}
      </Script>
      <Suspense fallback={null}>
        <GoogleAnalyticsPageViewTracker measurementId={GA_MEASUREMENT_ID} />
      </Suspense>
    </>
  );
}
```

`src/components/analytics/google-analytics-page-view-tracker.tsx`:

```tsx
"use client";

import { useEffect, useRef } from "react";
import { usePathname, useSearchParams } from "next/navigation";

type GoogleAnalyticsPageViewTrackerProps = {
  measurementId: string;
};

type WindowWithGtag = Window & {
  gtag?: (...args: [string, ...unknown[]]) => void;
};

export function GoogleAnalyticsPageViewTracker({
  measurementId,
}: GoogleAnalyticsPageViewTrackerProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const hasTrackedInitialPageView = useRef(false);

  useEffect(() => {
    if (!hasTrackedInitialPageView.current) {
      hasTrackedInitialPageView.current = true;
      return;
    }

    const gtag = (window as WindowWithGtag).gtag;

    if (!gtag) {
      return;
    }

    const search = searchParams.toString();
    const pagePath = search ? `${pathname}?${search}` : pathname;

    gtag("event", "page_view", {
      page_title: document.title,
      page_location: window.location.href,
      page_path: pagePath,
      send_to: measurementId,
    });
  }, [measurementId, pathname, searchParams]);

  return null;
}
```

Root layout:

```tsx
import { GoogleAnalytics } from "@/components/analytics/google-analytics";

// ...
<body className="font-sans antialiased">
  <GoogleAnalytics />
  {children}
</body>
```

## Why this shape

- The GA config snippet handles the initial page view, which avoids a race where a custom client tracker fires before `gtag` exists.
- The client tracker skips its first render and only sends page views for client-side App Router navigations, avoiding duplicate initial page views.
- `Suspense fallback={null}` protects root layout builds when `useSearchParams()` is used by the client tracker.
- The GA ID stays in one component-level constant, making future replacement simple.
- Production-only gating keeps local/stage/preview traffic out of the production GA property.

## Cookie consent note

If the site has a real consent banner/consent-mode contract, integrate with that contract instead of always loading GA. If the repo only has a settings page without a global consent flow and the user explicitly requests immediate GA tracking, keep the scope to production-only analytics and do not invent consent UX in the same PR.

## Verification

- Run a targeted TypeScript check: `npm run typecheck`.
- Add a source-level contract test if the repository uses source tests.
- In repositories with CI test grouping, run the group assertion before pushing, e.g. `node scripts/ci/assert-test-groups.mjs`, and assign the new test to exactly one group.
- For PRs, run the repo's smoke check if it is reasonably short, e.g. `npm run test:smoke`.
- After push, verify fresh checks attach to the new head SHA.

## References

- `references/corp-web-japan.md` — repo-specific GA ID, production helper, file layout, and CI grouping lesson from the corp-web-japan implementation.

## Pitfalls

- Do not paste raw `<script>` tags directly into JSX root layout when `next/script` is available.
- Do not create a new production detector if the repo already has a shared helper.
- Do not rely only on `gtag('config', ...)` for App Router client-side navigation if the site behaves as an SPA.
- Do not set `send_page_view: false` unless the custom tracker also reliably sends the initial page view after `gtag` exists; otherwise the first page view can be missed.
- Do not leave new tests unassigned in repos that enforce test grouping.
