# corp-web-app skill pack

Use when working in corp-web-app, especially route-local authoring, Tailwind migration, content unification, or stage E2E tasks.

This pack is intentionally stored outside active `.hermes/skills/` so its detailed skill index is not injected into every Hermes request. Load this index only when the current task matches this repository area, then read the specific `SKILL.md` files needed for the task.

## Summary

- skills: 13
- skill root: `.hermes/skill-packs/corp-web-app/skills/`
- active entrypoint: `.hermes/skills/software-development/corp-web-app-pack/SKILL.md`

## How to use

1. Read this `INDEX.md` first.
2. Pick the smallest relevant skill set from the trigger map below.
3. Read the selected `.hermes/skill-packs/.../SKILL.md` files directly with file tools.
4. Do not copy the whole pack into the prompt unless the task truly requires broad repo archaeology.

## Trigger map

### content/MDX migration

- `corp-web-app-content-unification-planning` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-content-unification-planning/SKILL.md`
  - Plan corp-web-app migration from corp-web-contents/Vercel Blob toward repo-local content management, borrowing structural lessons from corp-web-japan without copying Japan-only assumptions.
- `corp-web-app-public-route-locale-404-debugging` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-public-route-locale-404-debugging/SKILL.md`
  - Diagnose corp-web-app locale-prefixed public-route 404s by separating true missing resources from locale/route mismatches, including /public/** locale redirects and legacy share/redirect paths such as /:locale/chat/publication/**.
- `corp-web-app-static-page-route-local-migration` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-static-page-route-local-migration/SKILL.md`
  - Migrate or maintain corp-web-app static/semistatic pages as route-local App Router pages, preserving legacy source provenance, locale-specific authoring, route-aligned assets, and existing PR workflow.

### routes/SEO/rollout

- `corp-web-app` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app/SKILL.md`
  - Use when working in corp-web-app, especially route-local authoring, contact-us, stage E2E, and sitemap checks; contains migrated repo-specific memory and user preferences.
- `corp-web-app-contact-us-static-route-authoring` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-contact-us-static-route-authoring/SKILL.md`
  - Refactor corp-web-app contact-us routes into static app routes with route-local authoring, locale-specific pages, and safe unprefixed route handling via either a root EN wrapper or route-level redirect.
- `corp-web-app-internal-route-authoring` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-internal-route-authoring/SKILL.md`
  - Author and review corp-web-app internal-only utility pages so they stay under the internal namespace, remain noindex, avoid sitemap/canonical exposure, and are verified with route-mirrored tests.
- `corp-web-app-stage-e2e` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-stage-e2e/SKILL.md`
  - Add or maintain corp-web-app Playwright E2E coverage against https://stage.querypie.com, including production-vs-stage availability gates such as sitemap URL checks.

### tests/CI/ops

- `corp-web-app-contact-form-query-prefill` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-contact-form-query-prefill/SKILL.md`
  - Add stable query-string prefills to the corp-web-app ContactSales form while preserving locale-specific submitted values.
- `corp-web-app-contact-us-stage-e2e` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-contact-us-stage-e2e/SKILL.md`
  - Add or update corp-web-app Playwright E2E coverage for the public Contact Us page on stage.querypie.com, using the repo's existing tests/ runner instead of inventing a separate local-only harness.

### visual/render parity

- `corp-web-app-contact-us-layout-parity` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-contact-us-layout-parity/SKILL.md`
  - Update corp-web-app /company/contact-us to visually track a reference contact page by converting the shared ContactSales form UI into a contact-sales-only two-column layout with a right-side form card, without affecting other FormUI consumers.
- `corp-web-app-layout-data-localization` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-layout-data-localization/SKILL.md`
  - Convert corp-web-app shared layout data such as header/GNB/footer from remote blob-backed layout JSON to checked-in local locale modules while preserving locale parity, preview-navigation rewriting, and PR workflow.
- `corp-web-app-mdx-collection-migration` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-mdx-collection-migration/SKILL.md`
  - Migrate corp-web-contents MDX/publication collections into corp-web-app repo-local content, preserving corpus parity, locale coverage, route-aligned assets, docs inventory/matrix alignment, and existing PR workflow.
- `corp-web-app-static-route-from-dynamic-page` — `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-static-route-from-dynamic-page/SKILL.md`
  - Split a corp-web-app path out of the catch-all dynamic page into a dedicated app-route page.tsx wrapper while preserving existing DynamicPage rendering and metadata.

## Full skill list

| skill | path | description |
| --- | --- | --- |
| `corp-web-app` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app/SKILL.md` | Use when working in corp-web-app, especially route-local authoring, contact-us, stage E2E, and sitemap checks; contains migrated repo-specific memory and user preferences. |
| `corp-web-app-contact-form-query-prefill` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-contact-form-query-prefill/SKILL.md` | Add stable query-string prefills to the corp-web-app ContactSales form while preserving locale-specific submitted values. |
| `corp-web-app-contact-us-layout-parity` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-contact-us-layout-parity/SKILL.md` | Update corp-web-app /company/contact-us to visually track a reference contact page by converting the shared ContactSales form UI into a contact-sales-only two-column layout with a right-side form card, without affecting other FormUI consume |
| `corp-web-app-contact-us-stage-e2e` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-contact-us-stage-e2e/SKILL.md` | Add or update corp-web-app Playwright E2E coverage for the public Contact Us page on stage.querypie.com, using the repo's existing tests/ runner instead of inventing a separate local-only harness. |
| `corp-web-app-contact-us-static-route-authoring` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-contact-us-static-route-authoring/SKILL.md` | Refactor corp-web-app contact-us routes into static app routes with route-local authoring, locale-specific pages, and safe unprefixed route handling via either a root EN wrapper or route-level redirect. |
| `corp-web-app-content-unification-planning` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-content-unification-planning/SKILL.md` | Plan corp-web-app migration from corp-web-contents/Vercel Blob toward repo-local content management, borrowing structural lessons from corp-web-japan without copying Japan-only assumptions. |
| `corp-web-app-internal-route-authoring` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-internal-route-authoring/SKILL.md` | Author and review corp-web-app internal-only utility pages so they stay under the internal namespace, remain noindex, avoid sitemap/canonical exposure, and are verified with route-mirrored tests. |
| `corp-web-app-layout-data-localization` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-layout-data-localization/SKILL.md` | Convert corp-web-app shared layout data such as header/GNB/footer from remote blob-backed layout JSON to checked-in local locale modules while preserving locale parity, preview-navigation rewriting, and PR workflow. |
| `corp-web-app-mdx-collection-migration` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-mdx-collection-migration/SKILL.md` | Migrate corp-web-contents MDX/publication collections into corp-web-app repo-local content, preserving corpus parity, locale coverage, route-aligned assets, docs inventory/matrix alignment, and existing PR workflow. |
| `corp-web-app-public-route-locale-404-debugging` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-public-route-locale-404-debugging/SKILL.md` | Diagnose corp-web-app locale-prefixed public-route 404s by separating true missing resources from locale/route mismatches, including /public/** locale redirects and legacy share/redirect paths such as /:locale/chat/publication/**. |
| `corp-web-app-stage-e2e` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-stage-e2e/SKILL.md` | Add or maintain corp-web-app Playwright E2E coverage against https://stage.querypie.com, including production-vs-stage availability gates such as sitemap URL checks. |
| `corp-web-app-static-page-route-local-migration` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-static-page-route-local-migration/SKILL.md` | Migrate or maintain corp-web-app static/semistatic pages as route-local App Router pages, preserving legacy source provenance, locale-specific authoring, route-aligned assets, and existing PR workflow. |
| `corp-web-app-static-route-from-dynamic-page` | `.hermes/skill-packs/corp-web-app/skills/software-development/corp-web-app-static-route-from-dynamic-page/SKILL.md` | Split a corp-web-app path out of the catch-all dynamic page into a dedicated app-route page.tsx wrapper while preserving existing DynamicPage rendering and metadata. |
