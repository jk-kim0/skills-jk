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
- Important follow-up lesson from PR #223 review: treat a single flat `src/content/docs/*.mdx` directory plus per-loader filename allowlists as an exception-only compromise, not the preferred steady-state architecture.
- Why: family ownership becomes implicit in loader string arrays instead of obvious in the filesystem, new files/renames require touching loader allowlists, and category leakage/omission becomes easier.
- Preferred default remains physically separated family roots (for example `src/content/<family>/*.mdx`, or at minimum `src/content/docs/<family>/*.mdx`) unless the user explicitly accepts the flatter tradeoff.
- If you are following up on a PR that already flattened the files and the user wants the cleaner structure back, prefer a rename-based reversal into family roots instead of reauthoring the MDX from scratch. Typical target recovery shape:
  - `src/content/introduction-deck/*.mdx`
  - `src/content/glossary/*.mdx`
  - `src/content/manuals/*.mdx`
- In that reversal, update all of these together in one pass:
  - each repository `contentRoot`
  - any tests asserting concrete content paths
  - any temporary `public/docs/**` hero-image references back to family-aligned public paths
  - any now-empty `src/content/docs` / `public/docs` directories should be deleted after references are gone
- Additional PR #223 follow-up lesson: if the branch also introduced a new list-page abstraction just to support the content-root move, verify that abstraction actually exists in the repo before keeping it. In `corp-web-japan`, the safer default for preview list pages like `/t/manuals` is to preserve the existing composition built from `ResourceListHeroSection`, `ResourceListContentSection`, `ResourceCategorySidebar`, and `ResourceListItems` unless the user explicitly asked for a UI abstraction refactor.
- Also preserve `ResourceItem.id` when changing `BaseResourcePublicationRepository.listItems()`. The preview list grid keys items by `item.id`, and dropping that field causes both typecheck and build failures even if the content move itself is otherwise correct.
- The same rule applies to public assets: do not mirror a generic content-storage umbrella as `public/documentation/**`.
- The user still expects public asset paths to remain route/content-family aligned by feature, even if MDX sources are consolidated under `src/content/docs`.
- Good examples:
  - `public/introduction-deck/1/thumbnail.png`
  - `public/glossary/1/thumbnail.png`
  - `public/manuals/4/thumbnail.png`
  - `public/manuals/7/install-guide-1.png`
- Introduction-deck specific follow-up lessons:
  - if the user wants original downloadable PDFs localized into this repo, place them under the same route-aligned asset directory as the matching MDX item, for example:
    - `public/introduction-deck/1/QueryPie_AIP_Intro_JP.pdf`
    - `public/introduction-deck/2/QueryPie_ACP_Intro_JP.pdf`
  - then update the gated download CTA in the MDX body from the upstream `https://www.querypie.com/public/downloads/...` URL to the local asset path such as `/introduction-deck/1/QueryPie_AIP_Intro_JP.pdf`
  - if the user later asks for shorter canonical slugs/file names, keep the file-name pattern `<id>-<slug>.mdx` and update both the filename and frontmatter `slug` together (for example `1-querypie-aip.mdx` with `slug: "querypie-aip"`)
  - introduction-deck items can cross-link each other through frontmatter `relatedItems` using the existing local preview detail route shape and each item's own thumbnail, for example:
    - `href: "/t/introduction-deck/2/querypie-acp"`
    - `imageSrc: "/introduction-deck/2/thumbnail.png"`
    - `title: "QueryPie ACP 製品紹介書"`
  - when the downloadable PDF has no embedded PDF creation date (`CreateDate` / `ModifyDate` absent), and the user still wants a frontmatter `date`, inspect the upstream source repo git history carefully:
    - first-added date is only a fallback
    - if the file was later replaced, copied/renamed from another source file, or otherwise updated, prefer the date when the current final blob/version was introduced on the canonical path
  - important loader behavior lesson: `BaseResourcePublicationRepository.listSourceFiles()` loads every `*.mdx` file under `src/content/introduction-deck`
  - therefore, when renaming introduction-deck files (for example `1-querypie-aip-introduction.mdx` -> `1-querypie-aip.mdx`), leaving the old files behind will make the preview list show duplicate items
  - if you reconstruct or rewrite a PR on latest `origin/main`, do not just copy in the new filenames; explicitly delete the old `*-introduction.mdx` files in the same commit so the final tree contains only the canonical pair
- Additional filename/ID convention lesson from corp-web-japan PR 223 follow-up:
  - preferred content filename shape for localized preview resources is `<id>-<slug>.mdx`
  - keep `frontmatter.id` as the stable numeric lookup key
  - keep `frontmatter.slug` as the canonical display slug
  - examples:
    - `src/content/introduction-deck/1-querypie-aip-introduction.mdx`
    - `src/content/glossary/1-querypie-ai-glossary.mdx`
    - `src/content/manuals/2-acp-administrator-manual.mdx`
- This is usually a better steady-state than either plain `1.mdx` or slug-as-id files, because it preserves route stability while keeping filenames readable in reviews and IDE navigation.
- Follow-up naming lesson from introduction-deck PR work: if the user wants shorter canonical slugs later, it is acceptable to further shorten both the filename and frontmatter slug together while keeping the numeric `id` stable.
  - Example:
    - `1-querypie-aip-introduction.mdx` with `slug: querypie-aip-introduction`
    - -> `1-querypie-aip.mdx` with `slug: querypie-aip`
    - `2-querypie-acp-introduction.mdx` with `slug: querypie-acp-introduction`
    - -> `2-querypie-acp.mdx` with `slug: querypie-acp`
  - When doing this, also update any tests that assert concrete file paths.
- Additional introduction-deck content pattern lesson:
  - these preview introduction-deck MDX files can use frontmatter `relatedItems` just like other resource families
  - a valid shape is:
    - `href: "/t/introduction-deck/<id>/<slug>"`
    - `imageSrc: "/introduction-deck/<id>/thumbnail.png"`
    - `title: "..."`
  - For small cross-linking between deck variants (for example AIP <-> ACP), reusing the sibling deck's existing thumbnail as the related card image is acceptable and avoids creating extra assets.
  - If you need a publication `date` for localized intro-deck PDFs and the PDF itself has no embedded `CreateDate`/`ModifyDate`, inspect the upstream `corp-web-contents` git history carefully:
    - do not stop at the first-added date if the file was later replaced, copied from another file, or otherwise updated
    - use the commit date where the current final blob/version on the canonical intro-deck path was introduced
    - practical examples learned from the JP decks:
      - AIP final JP blob was introduced by `AIP Intro Deck 업데이트 PR (#768)` on `2025-10-29 19:16:35 +0900`
      - ACP final JP blob was introduced by `ACP 소개資料 업데이트 및 화이트페이퍼 이관 PR (#769)` on `2025-10-30 15:39:13 +0900`
  - When shortening intro-deck file names/slugs in a PR, also update any file-path-based tests outside the route-family test file itself.
    - A concrete example is `tests/button-link-external-prop.test.mjs`, which can still read the old `*-introduction.mdx` paths and fail CI with `ENOENT` even if the main route tests were updated.
  - Preserve the current intro-deck PDF button contract unless the user explicitly changes it:
    - keep `external={true}` on `ButtonLink` for the downloadable PDF CTAs when that is the current tested behavior
    - if a rewrite-on-main or squash/reconstruction drops that prop accidentally, CI can still fail even when the renamed MDX paths are otherwise correct.
- Avoid leaving legacy flat assets like `public/documentation/docu-thumb-*` or content roots like `src/content/documentation/<family>` once the new canonical paths exist.

4. Inline MDX images need the same cleanup as hero thumbnails.
- Do not stop after fixing only `heroImageSrc`.
- Search the MDX body for `ArticleFileImage filepath="public/..."` and move those files to route-aligned paths too.
- Example:
  - from `public/documentation/install-guide-1.png`
  - to `public/manuals/4/install-guide-1.png`
- When a family's item IDs are renumbered or repurposed, move the whole asset set to the new ID directory and update every MDX `heroImageSrc`, `relatedItems.imageSrc`, and `ArticleFileImage filepath` reference in the same change.
- For manuals specifically, if formerly external-only entries become local MDX detail pages, give each manual its own stable ID directory such as `public/manuals/1/thumbnail.png`, `public/manuals/2/thumbnail.png`, etc., instead of keeping legacy directories like `public/manuals/api-docs/` or `public/manuals/aip-guide/`.
- Important semantics lesson from PR 223 follow-up: when you normalize IDs/paths, do not automatically rewrite every `relatedItems.href` into local `/t/manuals/...` links just because local manual detail routes now exist.
- Some source documents intentionally point to external QueryPie docs and also use family-specific related thumbnail assets. A key example is glossary: preserve original external docs destinations such as `https://docs.querypie.com/ja/release-notes`, `.../administrator-manual`, and `.../user-manual`, with image paths like `/glossary/1/related-*-thumbnail.png`, instead of replacing them with local manual cards.
- Another important semantics lesson: if a manual wrapper page already exists and the user says its label/title is wrong, fix the naming first before deleting the page. In PR 254 follow-up work, deleting `5-acp-manual.mdx` was the wrong interpretation when the user actually wanted the page retained but renamed from `QCP Manual` to `QueryPie ACP Manual`.
- Practical rule: distinguish between three operations before editing manuals links/content:
  1. rename a mistaken label/title on an existing wrapper page,
  2. remove a wrapper page because the user explicitly no longer wants that concept,
  3. replace an external destination with a local detail route.
- Do not treat those as interchangeable. Preserve the original information architecture unless the user clearly asks to collapse or remove it.
- Be careful when converting related-item references during that numeric-ID migration: not every old manual-family card should become a local `/t/manuals/...` related link.
- Specific lesson from the glossary migration follow-up: glossary related items originally pointed at external docs endpoints and glossary-owned related thumbnails. Those should stay as:
  - external docs `href`s like `https://docs.querypie.com/ja/release-notes`
  - glossary-owned `imageSrc`s like `/glossary/1/related-release-notes-thumbnail.png`
  rather than being rewritten to local manual detail routes or `/manuals/*` thumbnails just because manuals were localized.

5. Keep the preview hub separate from category loaders.
- A mixed hub like `/t/resources` can compose items from several category loaders plus existing local blog/whitepaper lists.
- But the category-specific list/detail loaders should not be collapsed back into one generic grouped implementation.
- If a preview family still mixes local MDX records with ad hoc external item arrays (for example manuals), prefer converting those external entries into local MDX records as well once the user wants a fully local route family. Then simplify the preview item source back to the category repository only.
- For manuals specifically, a common follow-up is that the user wants all manual cards represented as local MDX records with stable numeric IDs and explicit canonical slugs. In that case:
  - prefer readable numeric filenames of the form `<id>-<slug>.mdx` instead of bare `1.mdx` or slug-only filenames
  - example target shape:
    - `src/content/manuals/1-acp-community-install-guide.mdx`
    - `src/content/manuals/2-acp-administrator-manual.mdx`
    - `src/content/manuals/3-acp-user-manual.mdx`
    - `src/content/manuals/4-acp-api-reference.mdx`
    - `src/content/manuals/5-acp-manual.mdx`
    - `src/content/manuals/6-aip-manual.mdx`
    - `src/content/manuals/7-acp-release-notes.mdx`
  - keep frontmatter split cleanly: `id` stays numeric-string, `slug` stays canonical route slug
  - move or duplicate legacy thumbnail assets into stable ID directories like `public/manuals/1/thumbnail.png`, `public/manuals/2/thumbnail.png`, etc.
  - if an older manual record is repurposed or renumbered (for example an install guide moving from one numeric slot to another), move its body-image assets to the new ID directory and update every `ArticleFileImage filepath` reference in the same edit
  - update `relatedItems.href` values across all manuals to the new canonical `/t/manuals/:id/:slug` routes after slug changes
  - if the branch removed old external-only manual entries but later content still links to one of those destinations (for example ACP manual / QCP Manual), add a small local wrapper MDX such as `5-acp-manual.mdx` instead of leaving broken `/t/manuals/acp-manual/acp-manual` references
  - if the user later clarifies that a label was wrong but the wrapper page itself is still desired, restore that wrapper page on the same PR branch instead of insisting on the earlier removal
  - for that restored wrapper page, preserve the local route (`/t/manuals/5/acp-manual`) but fix all user-facing strings consistently: title, section heading, button text, descriptive copy, and every related-item label that points to it
  - do not over-correct by redirecting all references to another manual family page (for example AIP manual) when the user's actual instruction was only to rename the ACP wrapper page
  - remove the old mixed external-item array from preview item composition so the list source is only `listManualPublicationItems()`
  - if the user asks for a shorter canonical slug after the numeric migration, it is fine to shorten both the filename and `slug` together (for example `1-querypie-acp-community-install-guide.mdx` -> `1-acp-community-install-guide.mdx`) as long as all internal `/t/manuals/:id/:slug` references and tests are updated in the same commit
- For glossary specifically, preserve the original meaning of `relatedItems` when normalizing IDs/slugs/file names.
  - The glossary page's related links may intentionally remain external QueryPie docs URLs instead of local `/t/manuals/...` routes.
  - The related thumbnails may intentionally remain glossary-specific assets such as `public/glossary/1/related-*.png`, not manual thumbnail paths.
  - If a later follow-up shortens the glossary slug, also rename the file to keep the `<id>-<slug>.mdx` convention aligned, and update any file-existence tests in the same commit.

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
