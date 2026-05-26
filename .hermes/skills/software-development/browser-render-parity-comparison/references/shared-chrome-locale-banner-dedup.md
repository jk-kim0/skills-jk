# Shared chrome locale banner deduplication

Use this note when a Tailwind route-group header/footer/GNB surface is expected to match a legacy route-group surface, especially for the locale/language nudge banner.

## Lesson

If browser probes show the legacy and Tailwind-rendered banner already have identical computed styles at the relevant breakpoints, do not invent local CSS tweaks just because the user reported a UI mismatch in the broader chrome.

Instead, inspect whether the two route groups maintain duplicated copies of the same banner implementation. If so, the narrowest durable parity fix may be to move only that banner into a shared layout module and have both legacy and Tailwind headers re-export/use the same component and CSS.

This prevents future drift while keeping the PR scoped to the banner surface.

## Suggested workflow

1. Force the banner to render with a controlled browser locale, for example `navigator.language = 'ko-KR'`, no selected-locale cookie, and cleared localStorage.
2. Compare the exact reference and target URLs at desktop, breakpoint edge, tablet, and phone widths.
3. Probe elements whose CSS module class contains `locale-nudge-banner`, not only text matches, because text-based nearest-ancestor probes can accidentally pick the root layout wrapper.
4. Compare computed style and geometry for:
   - container
   - content wrapper
   - description text
   - locale control wrapper
   - styled select
   - native select overlay
   - action button
   - close button wrapper
5. If computed output matches but source is duplicated, refactor to a shared module such as `src/components/layout/locale-nudge-banner/*` and keep legacy/Tailwind import paths as thin re-export shims when that minimizes caller churn.
6. Add or update a source-level contract test that asserts the Tailwind shim uses the shared banner implementation.

## PR scope guard

Keep this PR limited to the locale/language banner. Do not bundle broader GNB, header, footer, breakpoint, navigation, or Tailwind global reset changes unless the user explicitly asks for that broader scope.
