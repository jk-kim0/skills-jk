# Migrated memory and user context for corp-web-app

These entries were moved out of global Hermes memory/user profile because they are repository- or platform-specific. Keep them here or split them into narrower workflow skills as they evolve.


## From MEMORY.md


### MEMORY entry 1

In corp-web-app MDX migration, tutorials and manuals are distinct; tutorials from `page-archives/learn/tutorials/**` use `src/content/tutorials/<category>/<id>-<slug>.{locale}.mdx` and `public/tutorials/<category>/<id>/...`, not manuals or flat `dac-1` paths.


### MEMORY entry 2

In corp-web-app PR follow-up, keep scope narrow: do not modify public home/locale entries or shared ArticleFileImage/ArticleMain for internal sample MDX unless explicitly requested; prefer route-local MDX/frontmatter fixes; tests mirror route paths.


### MEMORY entry 3

In corp-web-app routing, unprefixed English public URLs rewrite to /en/...; non-English defaults redirect to /ko or /ja. Translation coverage is internal-only at `/{locale}/internal/translations/{events,blog}`; avoid public `/translations/**`, keep noindex/out of sitemap. QueryPie messaging should position QueryPie as an AI Solution/AI Platform company. For `(tailwind)` route-group work, keep `globals.css` minimal (ideally only Tailwind import) and handle old component compatibility via explicit tests/refactors, not legacy globals.


## From USER.md


### USER entry 1

Git tasks are complete only after commit/push and a PR/web URL; in corp-web-app route-local authoring, `/t` routes are interim safety checks, not the final deliverable.


### USER entry 2

User prefers sitemap-style docs to emphasize URI paths first; for corp-web-app sitemap E2E, keep sitemap-absent required public URLs in a separate fixture merged into checks.


### USER entry 3

For corp-web-app MDX migration reviews, user expects frontmatter relationship fields such as relatedIds, accepted identifier formats, and collection/family identifier contracts to be audited explicitly, not just content counts/routes/assets.
