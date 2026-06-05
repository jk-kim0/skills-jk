# App Router GA4 route-change tracking

Absorbed from the former `nextjs-app-router-analytics` and `nextjs-google-analytics` skills.

## Durable pattern

For Next.js App Router sites, the static GA4 snippet is not always enough for client-side navigation page views. Use a two-component pattern:

1. `google-analytics.tsx` loads `gtag/js`, runs the `gtag('config', measurementId)` init call, and wraps a client tracker in `<Suspense fallback={null}>`.
2. `google-analytics-page-view-tracker.tsx` is a small client component using `usePathname()` and `useSearchParams()`.
3. Let the initial `gtag('config', ...)` call send the initial page view.
4. Have the client tracker skip its first render, then send `gtag('event', 'page_view', { page_title, page_location, page_path, send_to })` on subsequent App Router navigations.
5. Do not set `send_page_view: false` unless you have another reliable initial page-view send that waits for `gtag` to exist.

## Example tracker

```tsx
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

## Test assertions worth keeping

When the repo has lightweight source/structure tests, assert that:

- root layout renders `<GoogleAnalytics />` exactly once
- the requested measurement ID is in code when the user asked for hardcoding
- no `process.env` dependency was introduced for code-configured tags
- production gating exists
- `next/script` uses `afterInteractive`
- route-change tracker uses `usePathname`, `useSearchParams`, and skips first render
- `<Suspense fallback={null}>` wraps the tracker when mounted from a server layout

## Repo-specific lessons formerly in the narrow skills

- In corp-web-japan, reuse `src/lib/is-production.ts` rather than creating a new production detector.
- In repos with CI test grouping, run the group assertion and assign any new analytics test to exactly one group.
- For README-only GA/Search Console documentation changes, inspect the diff and source identifier; local build/typecheck is usually unnecessary unless code changed.
