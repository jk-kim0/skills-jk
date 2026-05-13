---
name: corp-web-japan-route-local-authoring-wiki-scope
description: Update the corp-web-japan Route-Local-Authoring wiki page with the correct non-MDX scope, excluding content families already migrated through the separate MDX/publication pipeline.
---

# corp-web-japan Route-Local-Authoring wiki scope

Use this when updating these wiki pages in `corp-web-japan.wiki`:
- `Route-Local-Authoring`
- `Route-Local-Authoring-ko`
- future language variants of the same page

## Core rule

This wiki page is **not** the general migration inventory for all content.
It should track only the remaining **non-MDX** public page migration scope.

Do **not** include families that are already handled by the separate MDX/publication migration system.

## Explicitly exclude from this wiki page

Treat these as out of scope for `Route-Local-Authoring*`:
- blog
- whitepapers
- webinars / event-style document postings
- news
- use-cases
- AIP demo
- ACP demo
- introduction deck
- glossary
- manuals
- resources hub

Even if those surfaces still matter for the overall site migration, they belong to the publication / MDX migration track, not to route-local authoring scope.

## What this wiki page should track instead

Focus on non-MDX static/service/policy/company pages such as:
- home
- about-us
- certifications
- cookie-preference
- contact-us
- services landing pages (`AIP`, `ACP`, `FDE`)
- AIP / ACP non-MDX solution subpages
- legal / policy pages like `eula`, `privacy-policy`, `terms-of-service`
- any `corp-web-app` public pages that still need an explicit decision before local replacement, such as `plans`, `key-values`, or pricing-related pages

## Recommended wording

Frame the document around this question:
- which Japan-site pages still need to be finished as local non-MDX public pages in `corp-web-japan`?

Useful phrasing:
- "This page tracks the remaining non-MDX page migration scope"
- "Document-style MDX families are intentionally excluded"
- "Preview-only or redirect-backed static pages are the main remaining route-local authoring scope"

## Practical page structure

Recommended sections:
1. Purpose
2. Scope rule / explicit exclusions
3. Source-of-truth snapshots (`corp-web-japan`, `corp-web-app`, `corp-web-contents` SHAs)
4. Non-MDX static/service/policy inventory table
5. Current priority order
6. Reference routes already aligned enough
7. Conclusion

## Important repo-specific lesson

If a route family is already migrated through the local MDX/publication system, do not keep listing it here just because it still has detail routes or a list page.
This wiki page should stay narrow and actionable; otherwise it turns back into a generic migration dashboard.

## Latest-main audit lessons to preserve

When rewriting `Route-Local-Authoring*` from latest `origin/main`, do not preserve older classifications mechanically.
Re-audit these specific cases because they changed over time and are easy to describe incorrectly:

- top page route-local baseline
  - Do not keep describing the home page using older `src/content/home.ts`-driven wording if latest main has already removed that file.
  - If `src/content/home.ts` is gone and `src/app/page.tsx` now owns the visible copy/composition directly, explicitly note that the top page became a stronger route-local authoring reference point.
- route-local convention docs
  - Before updating the wiki, check whether `docs/static-page-route-local-authoring.md` and `docs/code-location-conventions.md` were updated on latest main.
  - If they now align with the intended route-local authoring split, mention that the repository guidance has caught up with the current implementation instead of leaving the wiki framed as if only the code changed.
- legacy `/posts/**` routes
  - Do not leave deleted legacy `/posts/**` routes sounding like remaining public migration candidates.
  - If latest main removed them, explicitly record that they are no longer part of the remaining non-MDX public-page inventory.
- section-file reorganization
  - If preview/static section implementations were reorganized into `src/components/sections/<family>/...`, treat that as supporting structure cleanup rather than a route-status change by itself.
  - Mention it when summarizing what changed on latest main, but do not let the inventory table imply that public/preview rollout status changed unless the routes themselves changed.

- `privacy-policy`
  - Do not leave this as only a `scope decision needed` item if latest main already has local preview implementation and local content versions.
  - On the audited baseline from 2026-05-10, latest main had `/t/privacy-policy`, `/t/privacy-policy/[slug]`, and local `src/content/privacy-policy/*.mdx` version records, so the correct status was `partial` with remaining public-rollout work.
- AIP integrations
  - Do not describe `/ja/solutions/aip/integrations` as redirect-only if latest main already has `/t/services/aip/integrations`.
  - If that preview route exists, classify it as `partial`, not `not yet migrated`.
- FDE route family
  - Check for both `/t/services/fde` and `/t/solutions/aip/fde-services` before writing the inventory.
  - If both preview routes exist while the public route is still redirect-only, explicitly note the duplicate-preview state and that canonical public rollout still needs to be decided.
- Contact us
  - Verify whether `/contact-us` is a real local page plus submit flow, not just a redirect endpoint.
  - If `src/app/contact-us/page.tsx` and `src/app/contact-us/submit/route.ts` both exist, treat it as already migrated.

## Recommended verification queries

Before finalizing the wiki page, explicitly inspect these latest-main files when relevant:

- `src/app/contact-us/page.tsx`
- `src/app/contact-us/submit/route.ts`
- `src/app/privacy-policy/route.ts`
- `src/app/t/privacy-policy/page.tsx`
- `src/app/t/privacy-policy/[slug]/page.tsx`
- `src/app/services/aip/route.ts`
- `src/app/services/acp/route.ts`
- `src/app/services/fde/route.ts`
- `src/app/t/services/aip/page.tsx`
- `src/app/t/services/acp/page.tsx`
- `src/app/t/services/fde/page.tsx`
- `src/app/t/services/aip/integrations/page.tsx`
- `src/app/t/solutions/aip/usage-based-llm/page.tsx`
- `src/app/t/solutions/aip/mcp-gateway/page.tsx`
- `src/app/t/solutions/aip/fde-services/page.tsx`

Also inspect route-only redirects for these public paths before classifying them as migrated:

- `/about-us`
- `/certifications`
- `/cookie-preference`
- `/services/aip`
- `/services/acp`
- `/services/fde`
- `/platform/ai/aip/*`
- `/platform/security/*`
- `/eula`
- `/terms-of-service`
