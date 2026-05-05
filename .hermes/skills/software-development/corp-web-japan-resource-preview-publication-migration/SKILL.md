---
name: corp-web-japan-resource-preview-publication-migration
description: Migrate corp-web-japan resource preview families like introduction-deck, glossary, and manuals into local MDX-backed preview list/detail routes with category-specific loaders and route-aligned public assets.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, resources, mdx, preview, asset-paths, route-local-authoring]
---

# corp-web-japan resource preview publication migration

Use this when a corp-web-japan preview resource family should stop being a redirect or hardcoded card list and become a local MDX-backed publication family.

Typical targets:
- `/t/introduction-deck`
- `/t/glossary`
- `/t/manuals`
- mixed resource hub pages such as `/t/resources`

## Core lessons

1. Do not keep unrelated preview-resource families grouped under one generic `documentation` runtime type.
- Treat `introduction-deck`, `glossary`, and `manuals` as separate publication/resource types, like blog/whitepaper/event.
- Shared logic may exist, but category identity should stay explicit in loaders, routes, tests, and asset paths.

2.5 If multiple categories share one physical MDX directory, add an explicit filename allowlist per category loader.
- The current base repository pattern can support this by adding a hook like `listSourceFiles()` to the abstract repository and overriding it in each concrete loader/repository.
- Example consolidated `docs` mapping learned from PR 223 follow-up work:
  - introduction-deck loader -> `1.mdx`, `2.mdx`
  - glossary loader -> `3.mdx`
  - manuals loader -> `4.mdx`, `5.mdx`, `6.mdx`, `7.mdx`
- Without this allowlist, category loaders that share the same `contentRoot` will incorrectly ingest each other's documents.
- When IDs are reassigned during such a consolidation, update all of the following together in one change:
  - MDX frontmatter `id`
  - related internal hrefs such as `/t/manuals/:id/:slug`
  - `heroImageSrc`
  - `relatedItems.imageSrc`
  - `ArticleFileImage filepath`
  - any tests that assert concrete MDX file paths or file-number expectations

3. Content source roots and public asset paths must both avoid a generic `documentation` umbrella, but the exact content-root shape can vary by the user's requested organization.
- Do not use `src/content/documentation/**` for these families once they are localized.
- Two valid follow-up patterns now exist in this repo history:
  - family-separated roots:
    - `src/content/introduction-deck/*.mdx`
    - `src/content/glossary/*.mdx`
    - `src/content/manuals/*.mdx`
  - single consolidated docs root when the user explicitly wants one shared directory:
    - `src/content/docs/1.mdx`
    - `src/content/docs/2.mdx`
    - `src/content/docs/3.mdx`
    - ... with category-specific loader allowlists deciding which files belong to introduction-deck, glossary, and manuals
- Important lesson: do not assume the code abstraction name (`resources`) should also be the content directory name. The user may want the loader abstraction kept in `src/lib/resources/*` while the actual MDX files live under `src/content/docs` or direct family folders.
- If the user explicitly asks to collapse glossary/manuals/introduction-deck into one directory, prefer `src/content/docs` over `src/content/resources`.
- The same rule applies to public assets: do not mirror a generic content-storage umbrella as `public/documentation/**`.
- The user still expects public asset paths to remain route/content-family aligned by feature, even if MDX sources are consolidated under `src/content/docs`.
- Good examples:
  - `public/introduction-deck/1/thumbnail.png`
  - `public/glossary/3/thumbnail.png`
  - `public/manuals/4/thumbnail.png`
  - `public/manuals/7/install-guide-1.png`
- Avoid leaving legacy flat assets like `public/documentation/docu-thumb-*` or content roots like `src/content/documentation/<family>` once the new canonical paths exist.

4. Inline MDX images need the same cleanup as hero thumbnails.
- Do not stop after fixing only `heroImageSrc`.
- Search the MDX body for `ArticleFileImage filepath="public/..."` and move those files to route-aligned paths too.
- Example:
  - from `public/documentation/install-guide-1.png`
  - to `public/manuals/4/install-guide-1.png`
- When a family's item IDs are renumbered or repurposed, move the whole asset set to the new ID directory and update every MDX `heroImageSrc`, `relatedItems.imageSrc`, and `ArticleFileImage filepath` reference in the same change.
- For manuals specifically, if formerly external-only entries become local MDX detail pages, give each manual its own stable ID directory such as `public/manuals/1/thumbnail.png`, `public/manuals/2/thumbnail.png`, etc., instead of keeping legacy directories like `public/manuals/api-docs/` or `public/manuals/aip-guide/`.

5. Keep the preview hub separate from category loaders.
- A mixed hub like `/t/resources` can compose items from several category loaders plus existing local blog/whitepaper lists.
- But the category-specific list/detail loaders should not be collapsed back into one generic grouped implementation.
- If a preview family still mixes local MDX records with ad hoc external item arrays (for example manuals), prefer converting those external entries into local MDX records as well once the user wants a fully local route family. Then simplify the preview item source back to the category repository only.
- For manuals specifically, a common follow-up is that the user wants all manual cards represented as local MDX records with stable numeric IDs and explicit canonical slugs. In that case:
  - create one MDX file per manual under `src/content/resources/manuals/<id>.mdx`
  - move or duplicate legacy thumbnail assets into stable ID directories like `public/manuals/1/thumbnail.png`, `public/manuals/2/thumbnail.png`, etc.
  - if an older manual record is repurposed or renumbered (for example an install guide moving from `1.mdx` to `4.mdx`), move its body-image assets to the new ID directory and update every `ArticleFileImage filepath` reference in the same edit
  - update `relatedItems.href` values across all manuals to the new canonical `/t/manuals/:id/:slug` routes after slug changes
  - remove the old mixed external-item array from preview item composition so the list source is only `listManualPublicationItems()`

## Recommended workflow

1. Start from latest `origin/main` in a fresh worktree.
2. Import or author local MDX source files under `src/content/resources/<family>/`.
- In `corp-web-japan`, do not use a grouped `src/content/documentation/**` directory for these preview resource families.
- Preferred paths:
  - `src/content/resources/introduction-deck/*.mdx`
  - `src/content/resources/glossary/*.mdx`
  - `src/content/resources/manuals/*.mdx`
- Keep the family identity explicit in both the directory name and the loader `contentRoot`. 
3. Implement an abstract resource base repository and abstract post loader.
4. Add concrete category repositories/loaders for each family.
5. Add list routes using the category-specific item loaders.
6. Add id-only redirect routes and canonical slug detail routes for each category.
7. Align hero, related-card, and inline-body images to route/content-family public paths.
8. Delete stale legacy asset duplicates and grouped temporary loaders.
9. Split tests by module/path instead of keeping one giant combined test file.

## Test organization rule

When adding or refactoring coverage, mirror the source paths where practical.
- Prefer:
  - `tests/src/lib/resources/architecture.test.mjs`
  - `tests/src/app/t/introduction-deck/page.test.mjs`
  - `tests/src/app/t/glossary/page.test.mjs`
  - `tests/src/app/t/manuals/page.test.mjs`
- Avoid one broad `documentation-preview-routes.test.mjs` file once the implementation is split by module.

## Verification

Minimum useful checks:
```bash
npm run typecheck
npm run test
npm run build
```

For asset cleanup specifically, also search for stale paths before finishing:
```bash
# use Hermes search_files in practice
search for `public/documentation/` references in `src/content/documentation` and `src/lib/resources`
search for old `docu-thumb-` filenames in `src/`
```

## Pitfalls
- Treating `src/content/documentation/**` as proof that public assets should live under `public/documentation/**`
- Fixing only hero thumbnails but leaving inline MDX images on legacy paths
- Keeping a grouped `documentation-publications.ts` after the user has asked for per-type separation
- Leaving stale duplicated image files in the repo after switching references to new canonical paths
- Keeping one giant combined test file after splitting loaders/routes by module

## Done criteria
- Each family has its own concrete loader/repository
- Shared logic lives only in the abstract resource base layer
- Hero, related, and inline images all use route/content-family aligned public paths
- No stale `public/documentation/docu-thumb-*` style references remain in code
- Test files are split by module/path rather than one combined catch-all file
- `npm run typecheck`, `npm run test`, and `npm run build` pass
