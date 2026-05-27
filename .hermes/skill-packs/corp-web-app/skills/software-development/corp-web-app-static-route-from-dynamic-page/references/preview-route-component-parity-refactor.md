# Preview-route component parity refactor example

Session example: corp-web-app `/[locale]/t/company/certifications` was refactored to follow corp-web-japan's equivalent `/certifications` page shape.

Reusable workflow:

1. Confirm scope literally.
   - If the user names `https://stage.querypie.com/ko/t/...`, target the `src/app/[locale]/t/...` verification route.
   - Do not touch the sibling public route (`src/app/[locale]/company/...`) unless public rollout is explicitly requested.

2. Inspect the equivalent implementation in the source repo.
   - For certifications, the corp-web-japan source used:
     - `CompanyPageSection`, `CompanyPageIntro`, `CompanyPageTitle`, `CompanyPageLead`, `CompanyPageLayout`
     - `CertificationsGrid`, `CertificationCard`, `CertificationsTrustCenterSection`, `CertificationsTrustCenterAction`
     - `AipFreeTrialCtaSection`, implemented from `SimpleCtaSection`

3. Port class-level primitives into corp-web-app shared section locations.
   - Add reusable page-family primitives under `src/components/sections/company/`.
   - Add reusable certifications primitives under `src/components/sections/certifications/`.
   - Use CSS Modules for corp-web-app styling instead of copying Tailwind class strings verbatim from corp-web-japan.

4. Keep route-local authoring visible.
   - Locale files should directly compose the primitives and show localized page copy, trust-center labels, and `SimpleCtaSection` content.
   - It is acceptable for repeated certification badge metadata to live in a tiny route-local `certification-items.ts` if the narrative and CTA copy remain in the locale TSX files.

5. Remove obsolete route-local implementation.
   - Delete stale route CSS if `CenterSection`, `StaticH*`, old button wrappers, or widget CSS are no longer used.
   - Remove preview route `DownloadBottom` if the requested structure uses `SimpleCtaSection` as the bottom CTA.
   - Update colocated README/provenance notes from the old widget render path to the new shared section component path.

6. Focused tests.
   - Assert the route renders representative locale copy, certification labels, trust-center link, and simple CTA label.
   - Add source-shape assertions that locale files contain the new primitives and no longer import/use old wrappers such as `CenterSection` or `src/components/widget/certifications`.

Pitfall:
- In fresh worktrees, local test execution may fail before test collection if dev dependencies for CSS/PostCSS are not installed. Do not encode that as a durable rule about the repo. Report it as environment state and rely on CI if the user's workflow prefers no install/build delay.
