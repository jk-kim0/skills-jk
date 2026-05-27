# Use-cases demo namespace rollout checklist

Session source: PR #547 follow-up review in `querypie/corp-web-japan`.

## Lesson

When use-case content/assets are normalized to `demo/use-cases`, the route contract must be normalized too. A half-migrated state where list/content/assets use `demo/use-cases` but detail pages remain at `/use-cases/:id/:slug` is inconsistent and should be fixed in the same PR.

## Required target contract

- List route: `/demo/use-cases`
- Detail route: `/demo/use-cases/:id/:slug`
- ID-only redirect route: `/demo/use-cases/:id`
- Content root: `src/content/demo/use-cases/*.mdx`
- Asset root: `public/demo/use-cases/<id>/thumbnail.png`
- Publication category / collection identifier: `demo/use-cases`
- Href prefix in `src/lib/publications/get-publication-href.ts`: `"demo/use-cases": "/demo/use-cases"`

## Files to audit in follow-up reviews

- `src/app/demo/use-cases/[id]/[slug]/page.tsx`
- `src/app/demo/use-cases/[id]/page.tsx`
- absence of old `src/app/use-cases/**`
- `src/lib/publications/get-publication-href.ts`
- AI Crew or other page-authored use-case detail links, especially `src/app/solutions/ai-crew/page.tsx`
- `README.md`, `AGENTS.md`, `docs/mdx-collection-inventory*.md`, route-authoring docs
- repo-local skills under `.agents/skills/mdx-publication-operations` and `.agents/skills/use-case-posting`
- tests that hard-code detail route expectations, including routing, indexability, redirectable-publication, canonical/SEO, and AI Crew page tests

## Verification pattern

Run focused source tests plus typecheck, for example:

```sh
node --test \
  tests/use-cases-imported-ja-corpus.test.mjs \
  tests/src/app/demo/use-cases/routing.test.mjs \
  tests/src/app/demo/use-cases/page.test.mjs \
  tests/src/app/solutions/ai-crew/page.test.mjs \
  tests/publication-detail-indexability.test.mjs \
  tests/redirectable-publication-bot-handling.test.mjs \
  tests/canonical-endpoints.test.mjs \
  tests/seo-metadata.test.mjs
npm run typecheck
```

After pushing a PR follow-up, `gh pr view` may briefly lag on `headRefOid`; verify the remote tip directly with:

```sh
git ls-remote origin refs/heads/<pr-branch>
git rev-parse HEAD
```
