---
name: nextjs-analytics-tagging
description: Add, audit, or plan Google Analytics / gtag / GTM tagging in Next.js App Router sites, including hardcoded measurement IDs, production gating, Vercel env audits, and cookie-consent interactions.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, analytics, google-analytics, gtag, gtm, app-router, vercel, cookies]
    related_skills: [codebase-inspection, vercel-project-env-parity-copy]
---

# Next.js analytics tagging

Use this skill when the user asks whether a Next.js site has Google Analytics / Google Tag / GTM installed, asks where to add a tag, or asks to implement or plan hardcoded gtag/GTM behavior.

## Goals

- Distinguish source-code tags, Vercel environment variables, and actually deployed HTML/JS behavior.
- Recommend the smallest site-wide integration point for App Router sites.
- Avoid mixing staging/preview/local traffic into production analytics unless the user explicitly wants that.
- Respect existing cookie-consent or cookie-preference architecture instead of adding analytics in isolation.

## Quick audit workflow

1. Confirm repository and framework context.
   - Check `pwd`, branch, and `package.json`.
   - For App Router, locate `src/app/layout.tsx` and any nested `layout.tsx` files.

2. Search source and config for existing analytics.
   - Search broadly for `G-`, `GT-`, `GTM-`, `gtag(`, `googletagmanager`, `google-analytics`, `GoogleAnalytics`, `NEXT_PUBLIC_*GA*`, `GOOGLE_ANALYTICS`, `GOOGLE_TAG`, and `ANALYTICS`.
   - Include app source, config, env examples, docs, and Vercel config files.

3. If the question includes Vercel settings, audit remote env separately.
   - Use `vercel-project-env-parity-copy` for read-only env listing.
   - Report key names, targets, and type only; do not print secret values.
   - Do not infer remote env absence from missing local `.env` or missing `.vercel/project.json`.

4. Verify deployed output when the user asks what is currently applied.
   - Fetch production and stage HTML if relevant.
   - Search both HTML and Next.js JS chunks for tag IDs and loader URLs.
   - Treat code/env/deployed-output as separate evidence streams.

## Recommended hardcoded gtag pattern for App Router

Prefer a small component rendered once from the root layout rather than inline snippets scattered through pages. For App Router sites where client-side navigation page views matter, use the route-change tracker pattern in `references/app-router-route-change-tracking.md` instead of relying only on a one-time static snippet.

1. Add a component such as `src/components/analytics/google-analytics.tsx`.
2. Put the hardcoded measurement ID near the top as a constant:

```tsx
const GA_MEASUREMENT_ID = "G-XXXXXXXXXX";
```

3. Use `next/script`, not raw `<script>` tags:

```tsx
import Script from "next/script";
import isProduction from "@/lib/is-production";

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
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA_MEASUREMENT_ID}');
        `}
      </Script>
    </>
  );
}
```

4. Render the component once inside `src/app/layout.tsx`, usually at the start of `<body>` before `{children}`:

```tsx
<body className="font-sans antialiased">
  <GoogleAnalytics />
  {children}
</body>
```

5. Use the repository's existing production detector if one exists, such as an `isProduction()` helper based on `VERCEL_TARGET_ENV`. If no helper exists, create a tiny one instead of duplicating environment checks in the analytics component.

## Cookie-consent decision point

Before implementing, check for existing cookie preference or consent code.

- If the site has no cookie consent architecture and the user only asked for hardcoded GA, the simple production-gated component is the smallest implementation.
- If the site already describes analytics/performance cookies as opt-in, do not silently ignore that. Explain the trade-off:
  - Immediate production load: simplest and collects traffic immediately, but may not align with the stated consent model.
  - Consent-gated load: load only when the analytics/performance preference cookie is enabled; policy-aligned, but requires a discoverable banner or consent UX if the site currently only has a settings page.
- If the user asks for implementation and does not specify consent handling, prefer asking one focused decision question only when the difference changes behavior materially.

## Verification

Use the lightest check that proves the change:

- TypeScript/typecheck for compile safety.
- Source-level tests for root layout/component presence if the repo has lightweight structure tests.
- For deployed verification after merge/deploy, fetch HTML and JS chunks and search for the measurement ID and `googletagmanager.com/gtag/js`.
- Avoid starting a local dev server unless the user explicitly requests it or browser-only behavior must be verified.

## Pitfalls

- Do not add `@next/third-parties` solely for a simple gtag integration unless the repo already uses it or the user asks for it.
- Do not put a public measurement ID in Vercel env if the user explicitly asks for hardcoding.
- Do not place analytics snippets in individual page files for a site-wide tag.
- Do not allow preview/stage/local traffic into the production GA property by default.
- Do not call a site "tagged" just because a Vercel env var exists; verify whether code actually reads it and whether deployed output includes the script.
- Do not call a site "untagged" from source search alone; check deployed output if the user asks about the current website.

## References

- `references/corp-web-japan-gtag-audit.md` — concrete audit notes from a corp-web-japan session, including Vercel env, root layout, production gating, and cookie preference findings.
