# corp-web-japan gtag audit notes

This reference captures a concrete Next.js App Router analytics audit pattern from `querypie/corp-web-japan`.

## Repo observations

- App root layout is `src/app/layout.tsx`.
- Current main has a production-only GA4 integration in `src/components/analytics/google-analytics.tsx`, rendered once from the root layout before `{children}`.
- Current measurement ID: `G-DGKPWV2DP2`.
- The integration uses `next/script`, `isProduction()`, and an App Router client navigation tracker in `src/components/analytics/google-analytics-page-view-tracker.tsx`.
- The route-change tracker sends follow-up `page_view` events with `page_location: window.location.href` and `page_path` including `useSearchParams()`, so standard `utm_*` query strings are carried into GA4 page-view hits.
- Production `https://querypie.ai/?utm_source=...` HTML has been verified to include `G-DGKPWV2DP2` and `googletagmanager.com/gtag/js`; stage does not render the tag because of production gating.
- Forms also have separate UTM-to-Salesforce attribution mapping in `src/lib/forms/server/utm-attribution.ts` for contact/whitepaper gated flows.

## Historical note

An earlier audit found no GA/GTM IDs in source, config, Vercel env, production HTML, stage HTML, or downloaded Next.js JS chunks. That finding is stale after the GA4 implementation landed; future audits should treat the current source/deployed output as authoritative rather than reusing the old absence claim.

## Vercel env audit detail

Project evidence used:

- Vercel project name: `corp-web-japan`
- Repo link: `querypie/corp-web-japan`
- Production branch: `main`

Read-only env API returned 14 env vars and 0 analytics/tag matches for broad patterns such as `GA`, `GA4`, `GTAG`, `GTM`, `GOOGLE_ANALYTICS`, `GOOGLE_TAG`, and `ANALYTICS`.

Important shell-loading lesson:

- Credentials were exported from `~/.zshrc`.
- The default tool shell did not load them, so direct `bash` checks incorrectly showed no `VERCEL_TOKEN`.
- Running the API probe through `zsh -ic '...'` loaded the token and succeeded.
- Future audits should verify shell loading before reporting missing Vercel credentials.

## Best-fit hardcoded gtag pattern for this repo shape

Current implementation shape to preserve:

1. `src/components/analytics/google-analytics.tsx` owns the hardcoded measurement ID `G-DGKPWV2DP2`.
2. It uses `next/script` with `strategy="afterInteractive"` for both the external loader and inline init script.
3. It guards rendering with the existing `src/lib/is-production.ts`, which returns `process.env.VERCEL_TARGET_ENV === 'production'`.
4. `src/app/layout.tsx` renders `<GoogleAnalytics />` once inside `<body>`, before `{children}`.
5. `src/components/analytics/google-analytics-page-view-tracker.tsx` handles App Router client-side navigation page views and must keep query strings in `page_path` for UTM visibility.

If this implementation is missing or regresses, restore this shape rather than inventing a Vercel env-based tag or page-local snippets.

## Cookie preference nuance

The repo has a cookie preference page and cookie keys in `src/lib/cookie-preferences.ts`:

- `cookie-preference-performance`
- `cookie-preference-functional`
- `cookie-preference-event` for analysis
- `cookie-preference-marketing`

The current GA4 implementation is production-gated but not consent-gated. If future work asks for consent alignment, explicitly discuss the behavior change: gating on `cookie-preference-event=1` is more consistent with the preference-page wording, but it will reduce collection unless there is a discoverable consent UX.

Do not silently change the current production-load behavior during a routine UTM/GA audit; report the trade-off and change only when requested.

## Verification notes

Use the lightest checks that prove both source and deployment state:

- Source/structure tests:
  - `node --test tests/src/components/analytics/google-analytics.test.mjs tests/src/lib/forms/server/utm-attribution.test.mjs`
- Deployed production probe:
  - Fetch `https://querypie.ai/?utm_source=hermes_test&utm_medium=check&utm_campaign=utm_audit` and verify the HTML includes `G-DGKPWV2DP2` and `googletagmanager.com/gtag/js`.
  - Check stage separately only to confirm production gating; absence of the rendered tag on `stage.querypie.ai` is expected.
- If using Vercel API, verify the production deployment commit is at or after the GA4 implementation commit; do not rely on source presence alone when the user asks whether the website is tracking now.
- Do not report GA Data API unavailability as a durable limitation when local auth tools are missing; it is a setup state, not a skill rule.
