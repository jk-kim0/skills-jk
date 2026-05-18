# corp-web-japan gtag audit notes

This reference captures a concrete Next.js App Router analytics audit pattern from `querypie/corp-web-japan`.

## Repo observations

- App root layout is `src/app/layout.tsx`.
- The layout currently imports metadata, local font setup, `preload` from `react-dom`, global CSS, and `siteUrl`.
- There is a single root layout and no existing `next/script` analytics integration.
- No GA/GTM IDs were found in source, config, local env files, Vercel env listing, production HTML, stage HTML, or downloaded Next.js JS chunks during the session.

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

## Best-fit hardcoded gtag plan for this repo shape

Recommended implementation if the user asks to add a hardcoded gtag:

1. Create `src/components/analytics/google-analytics.tsx`.
2. Put `const GA_MEASUREMENT_ID = "G-...";` in that file.
3. Use `next/script` with `strategy="afterInteractive"` for both the external loader and inline config script.
4. Guard with the existing `src/lib/is-production.ts`, which returns `process.env.VERCEL_TARGET_ENV === 'production'`.
5. Render `<GoogleAnalytics />` once inside `<body>` in `src/app/layout.tsx`, before `{children}`.

## Cookie preference nuance

The repo has a cookie preference page and cookie keys in `src/lib/cookie-preferences.ts`:

- `cookie-preference-performance`
- `cookie-preference-functional`
- `cookie-preference-event` for analysis
- `cookie-preference-marketing`

The page describes analytics cookies as opt-in. If implementing GA, the user should choose between:

- Simple production-gated hardcoded load, which starts collecting immediately.
- Consent-gated load based on `cookie-preference-event=1`, which aligns better with the existing wording but will not collect most traffic unless the site also provides a discoverable consent banner/UX.

Do not silently choose consent behavior when the requested scope is only a hardcoded tag audit/plan; state the trade-off clearly.
