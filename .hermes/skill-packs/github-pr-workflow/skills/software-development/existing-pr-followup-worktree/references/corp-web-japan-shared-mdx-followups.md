# corp-web-japan shared MDX follow-up patterns

Use this when an existing PR follow-up starts as a page-specific tweak but reveals a shared publication-MDX concern.

## Pattern 1: replace one-off inline wrappers with the smallest shared MDX primitive

Symptom:
- a PR already contains a page-local workaround such as `<div className="mt-6">...</div>` around a CTA
- the user asks whether spacing should be handled more generally

Preferred move:
- keep `ButtonLink` as the pure button primitive
- add a tiny shared wrapper such as `ArticleCta` in `src/lib/publications/mdx/components.tsx`
- switch the page from the ad hoc wrapper to that primitive
- update the same PR branch instead of opening a cleanup PR

Why:
- avoids baking layout responsibility into `ButtonLink`
- keeps article-body spacing ownership in the publication MDX layer
- avoids leaving throwaway route-local wrappers in a PR that is still under review

## Pattern 2: first MDX body image looks too narrow

Symptom:
- the first article-body image does not fill the content column even after removing an outer centering wrapper

Likely cause in this repo:
- shared publication body styling in `src/components/sections/publication-post-page.tsx`
- `img.wp-figure_img` has `max-w-full` only, so it never exceeds its intrinsic image width

Preferred fix:
- treat `figure.wp-figure` as the shared centering container
- set `img.wp-figure_img` to `block w-full max-w-full`
- keep centering on the figure (`flex flex-col items-center text-center` was the chosen pattern here)

Why:
- fixes the whole publication surface consistently
- prevents repeated page-by-page MDX wrapper churn

## Minimal verification used successfully here

- `node --test tests/events-imported-ja-corpus.test.mjs`
- diff-scope check on only the touched shared publication files and target MDX page
