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
