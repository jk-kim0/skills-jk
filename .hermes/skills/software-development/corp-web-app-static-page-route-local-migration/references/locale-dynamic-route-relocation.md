# Locale dynamic route relocation pattern

Session context: reviewed whether corp-web-app Contact Us implementation could move from explicit locale route directories to `src/app/[locale]/company/contact-us/`.

## Useful pattern

When consolidating a static/semistatic page that currently has separate App Router directories like:

```text
src/app/company/contact-us/page.tsx
src/app/en/company/contact-us/page.tsx
src/app/ko/company/contact-us/page.tsx
src/app/ja/company/contact-us/page.tsx
```

A safe route-local target is:

```text
src/app/company/contact-us/page.tsx              # default EN public wrapper
src/app/[locale]/company/contact-us/page.tsx     # thin locale dispatcher
src/app/[locale]/company/contact-us/page.en.tsx  # EN authored page
src/app/[locale]/company/contact-us/page.ko.tsx  # KO authored page
src/app/[locale]/company/contact-us/page.ja.tsx  # JA authored page
```

Keep `/company/contact-us` as a thin EN wrapper unless the user explicitly asks to change the public route policy. This preserves existing header/footer links, E2E specs, and public query contracts.

## Key pitfall

Do not leave the old explicit locale route files in place after introducing `src/app/[locale]/...`. In Next.js App Router, explicit static segments such as `src/app/en/company/contact-us/page.tsx` can continue to win over the new dynamic `[locale]` route for `/en/company/contact-us`, `/ko/company/contact-us`, and `/ja/company/contact-us`. If the goal is a real relocation, move/delete those explicit locale route implementations and update tests/imports to target the `[locale]` path.

## Metadata note

Existing pages that reused `src/app/dynamic-page` metadata by synthesizing a `PageRequest` can keep the same approach in the new structure. The thin dispatcher should select locale-specific metadata; the default unprefixed wrapper can delegate to the EN authored page.

## Implementation notes from Contact Us relocation

- Move route-local shared section CSS/components with the authored pages when they are page-specific. For Contact Us, `contact-us-page-section.component.tsx` and `.module.css` moved from the unprefixed wrapper route into `src/app/[locale]/company/contact-us/`.
- Make locale `generateMetadata` exports callable both from the dispatcher and from the unprefixed default wrapper. A practical pattern is an optional props default like `{ searchParams: Promise.resolve({}) }` on `page.en.tsx`/`page.ko.tsx`/`page.ja.tsx` metadata functions.
- Keep the unprefixed wrapper test mocking the new `src/app/[locale]/.../page.en` module, not the deleted `src/app/en/...` module.

## Verification pointers

- Search for imports of the old explicit locale paths.
- Search for public URL references before changing links; public URL changes are separate route-policy work.
- Add/update a dispatcher test similar to an existing `[locale]` route-local page test.
- Run targeted Vitest for both the default wrapper and all relocated locale-authored pages.
- Keep query-prefill/form E2E route expectations unchanged if the public URL remains `/company/contact-us`.
- If broad `tsc --noEmit` fails on unrelated existing test type issues, report that baseline separately and confirm no changed-path errors appeared.
