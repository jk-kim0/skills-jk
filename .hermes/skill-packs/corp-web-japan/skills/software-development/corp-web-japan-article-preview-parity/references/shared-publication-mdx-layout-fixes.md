# Shared publication MDX layout fixes

Use this reference when a specific corp-web-japan article page complaint turns out to be caused by the shared publication shell rather than by that page's MDX alone.

## First body image looks too narrow

Symptom:
- the first `ArticleFileImage` in the MDX body renders narrower than the article content column

Root cause seen in this repo:
- shared publication body styling in `src/components/sections/publication-post-page.tsx`
- `img.wp-figure_img` had `max-w-full` only, so the image respected its intrinsic pixel width instead of expanding to the full content width

Fix pattern used successfully:
- keep centering responsibility on `figure.wp-figure`
- make the figure a centered column container
- set `img.wp-figure_img` to `block w-full max-w-full`

Why this is the right layer:
- fixes all publication surfaces consistently
- avoids repeated page-level MDX wrapper churn

## CTA spacing should be shared but not owned by ButtonLink

Symptom:
- a page got a temporary inline wrapper such as `<div className="mt-6">` around a `ButtonLink`
- user asks whether spacing should be handled more generally

Preferred fix pattern:
- keep `ButtonLink` as the pure button/link primitive
- add a shared article-body wrapper such as `ArticleCta` in `src/lib/publications/mdx/components.tsx`
- replace the page-local inline wrapper with the shared MDX primitive

Why:
- keeps spacing ownership in the publication MDX layer
- avoids coupling generic button markup to article-body spacing rules
