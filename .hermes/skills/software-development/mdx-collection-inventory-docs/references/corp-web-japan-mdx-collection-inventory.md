# corp-web-japan MDX collection inventory pass (2026-05)

This reference captures the concrete investigation pattern used for a docs-only PR that summarized MDX-backed collections in `querypie/corp-web-japan`.

## Families found on latest main

Public publication/resource families:

- Blog: `src/content/blog/*.mdx`, `/blog`, `/blog/:id/:slug`, assets `public/blog/<id>/...`.
- Whitepapers: `src/content/whitepapers/*.mdx`, `/whitepapers`, `/whitepapers/:id/:slug`, `/whitepapers/:id/:slug/pdf`, assets `public/whitepapers/<id>/...`.
- News: `src/content/news/*.mdx`, `/news`, `/news/:id/:slug`, assets `public/news/<id>/...`.
- Events: `src/content/events/*.mdx`, `/events`, `/events/:id/:slug`, assets `public/events/<id>/...`.
- Use cases: `src/content/use-cases/*.mdx`, list `/demo/use-cases`, detail `/use-cases/:id/:slug`, assets `public/use-cases/<id>/...`.
- AIP demo: `src/content/demo/aip/*.mdx`, `/demo/aip`, `/demo/aip/:id/:slug`, assets `public/demo/aip/<id>/...`.
- ACP demo: `src/content/demo/acp/*.mdx`, `/demo/acp`, `/demo/acp/:id/:slug`, assets `public/demo/acp/<id>/...`.
- Introduction deck: `src/content/introduction-deck/*.mdx`, `/introduction-deck`, `/introduction-deck/:id/:slug`, assets `public/introduction-deck/<id>/...`.
- Glossary: `src/content/glossary/*.mdx`, `/glossary`, `/glossary/:id/:slug`, assets `public/glossary/<id>/...`.
- Manuals: `src/content/manuals/*.mdx`, `/manuals`, `/manuals/:id/:slug`, assets `public/manuals/<id>/...`.

Legal pages were documented separately:

- Privacy policy: `src/content/privacy-policy/YYYY-MM-DD.mdx`, latest `/privacy-policy`, versioned `/privacy-policy/:slug`, no current public image root.
- Terms of service: `src/app/terms-of-service/content.mdx`, endpoint `/terms-of-service`, no current public image root.

## Loader families

- Standard publication records: `src/lib/publications/create-standard-records-repository.ts`.
- Standard post rendering: `src/lib/publications/create-standard-publication-post-loader.ts`.
- Gated post rendering: `src/lib/publications/create-gated-publication-post-loader.ts`.
- Resource publication repository: `src/lib/resources/base-resource-publication.ts`.
- Legal MDX rendering: `src/lib/legal-mdx-source.ts`.

## Frontmatter support distinctions

Standard publication families generally support:

- `id`, `slug`, `title`, `description`, `date`, `heroImageSrc`.
- `author` when the family normalizer includes it.
- `relatedIds` for same-family related cards.
- `hidden` and `redirectUrl` via the standard records repository.

Whitepapers add:

- `listDescription`.
- `downloadCoverImageSrc`.
- `downloadCta`.
- `gated` + `<GatingCut />` through the gated post loader.

Events add:

- `eventDate` with ISO `YYYY-MM-DD` validation.
- `eventLabel`.
- `hideHeroImageOnDetail` and `hideTocOnDetail`.

Resource publication families use:

- `id`, `slug`, `title`, `description`, `heroImageSrc`.
- optional `date`, `gated`, `downloadCta`, `relatedItems`.
- no shared `hidden` / `redirectUrl` support unless code changes.

Legal pages use only legal-route frontmatter:

- Privacy policy: `title`, `description`, `date`, `version`; slug comes from the filename.
- Terms of service: `title`, `description`, `date`.

## Useful one-off inspection commands

```bash
find src/content -name '*.mdx' | sed 's#^src/content/##' | awk 'BEGIN{FS="/"} {if (NF==1) print "./"; else if ($1=="demo") print $1"/"$2; else print $1}' | sort | uniq -c
find src/app -path '*page.tsx' -o -path '*route.ts' | sort | grep -E '(blog|whitepapers|news|events|use-cases|demo/(aip|acp)|introduction-deck|glossary|manuals|privacy|terms)'
find src/lib -type f | sort | grep -E '(publication|resource|blog|whitepaper|news|events|use-case|demo|introduction|glossary|manual|legal|privacy)'
```
