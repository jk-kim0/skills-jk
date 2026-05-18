---
name: nextjs-app-router-analytics
description: Add or audit analytics tags in Next.js App Router sites with minimal performance impact, production gating, and reliable client-side navigation page views.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, app-router, analytics, google-analytics, gtag, performance]
---

# Next.js App Router analytics

Use this when adding, reviewing, or debugging analytics tags in a Next.js App Router site, especially Google Analytics / gtag / GA4.

## Trigger signals

- User asks to add GA, gtag, GTM, or analytics tracking.
- User provides a Google tag snippet and asks how to apply it in a Next.js site.
- User wants code-based configuration rather than environment-variable based configuration.
- User asks whether analytics affects performance or whether SPA navigation page views will be tracked.

## Recommended GA4 pattern for App Router

1. Extract only the GA4 measurement ID from the Google-provided snippet, for example `G-XXXXXXXXXX`.
2. Create a small analytics component under `src/components/analytics/` rather than pasting raw script tags directly into route files.
3. Load the external tag with `next/script` and `strategy="afterInteractive"`.
4. Gate production-only analytics with the repo's existing production signal if present, for example `isProduction()` based on `VERCEL_TARGET_ENV === "production"`.
5. Mount the component once in the root `src/app/layout.tsx` body so all routes inherit it and duplicate scripts are avoided.
6. Track App Router client-side navigations separately with a tiny client component using `usePathname()` and `useSearchParams()`.
7. Let `gtag('config', measurementId)` handle the initial page view, and have the route-change tracker skip its first render. This avoids losing the initial page view when the external script loads after hydration while still preventing duplicate page views on the first render.
8. Wrap the route-change tracker in `<Suspense fallback={null}>` when it uses `useSearchParams()` from a server component boundary such as root layout.

## Example

```tsx
// src/components/analytics/google-analytics.tsx
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

```tsx
// src/components/analytics/google-analytics-page-view-tracker.tsx
"use client";

import { useEffect, useRef } from "react";
import { usePathname, useSearchParams } from "next/navigation";

type Props = { measurementId: string };
type WindowWithGtag = Window & { gtag?: (...args: [string, ...unknown[]]) => void };

export function GoogleAnalyticsPageViewTracker({ measurementId }: Props) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const hasTrackedInitialPageView = useRef(false);

  useEffect(() => {
    if (!hasTrackedInitialPageView.current) {
      hasTrackedInitialPageView.current = true;
      return;
    }

    const gtag = (window as WindowWithGtag).gtag;
    if (!gtag) return;

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

Mount once:

```tsx
// src/app/layout.tsx
<body>
  <GoogleAnalytics />
  {children}
</body>
```

## Verification

- Add a narrow source-level test that asserts:
  - root layout renders `<GoogleAnalytics />` once
  - the measurement ID is hardcoded when requested
  - `process.env` is not used when the user requested code configuration
  - production gating exists
  - `next/script` uses `afterInteractive`
  - the route-change tracker uses `usePathname`, `useSearchParams`, and skips the first render
- Run `npm run typecheck` for TypeScript safety.
- Do not start a local dev server unless the user explicitly asks; for many repo workflows CI/preview deployment is preferred.

## Pitfalls

- Do not paste raw `<script>` tags into JSX layout; use `next/script` so Next.js controls loading and avoids render-blocking behavior.
- Do not rely only on the static Google snippet for App Router sites if SPA navigation page views matter.
- Do not use `send_page_view: false` unless the app sends a reliable initial page view after gtag has loaded. A client effect can run before the external script is ready and silently skip the first page view.
- Do not send an immediate manual page view from the route tracker without guarding the first render, or the initial load can be double-counted.
- Production-only analytics should use the deployment target signal, not branch-name guesses, when the repo already has such a helper.
