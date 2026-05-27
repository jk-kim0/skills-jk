# `/{locale}/t/news` Tailwind list-parity notes

Session-derived details from implementing the corp-web-app `/{locale}/t/news` list to match `https://querypie.ai/news`.

## Live-page measurements to preserve

At a 1280px desktop viewport, the live `querypie.ai/news` page uses an editorial list layout rather than a resource-card grid:

- H1: `ニュース`, about `52px` font size, `62.4px` line-height, left aligned in a `1200px` container.
- Intro copy: directly below the H1 with a large vertical gap; max text width around `960px`.
- News rows: full-width vertical list; each row is text on the left and a thumbnail block on the right.
- Thumbnail block: about `400px x 225px`, `object-fit: cover`, light gray fallback background, `8px` radius.
- Text column: date at `16px/28px`, title around `36px` desktop with `1.35` line-height, description at `16px/32px`.
- Row gap: about `80px` on desktop.
- Load-more controls: centered progress text/bar and a bordered white `Load More` button.
- Bottom CTA: keep the existing shared `DownloadBottom`/CTA flow when the repo already has it; do not clone CTA CSS unnecessarily.

## Implementation pattern

For corp-web-app preview list routes, prefer converting the list surface itself to Tailwind classes in the route/list component when the task explicitly asks for Tailwind:

- Replace CSS-module-only classes for `NewsListPageSection`, `NewsListItems`, and `ProgressiveLoadMore` with Tailwind utility classes.
- Remove the CSS Module file only after searching for all `styles.` references and confirming no other component imports it.
- Keep shared generic resource-list/card functions intact if they are used by other publication families.
- Keep the route entry thin and keep content sourced from `src/content/news/*.mdx` / existing repository loaders.
- Do not change public `/news` route, sitemap, canonical, or redirects when the request is only for `/{locale}/t/news`.

Useful source check:

```bash
rg 'resource-list-section.module.css|styles\.' src/components/sections/resource-list
```

## Test/verification pattern

A targeted Vitest route test can pin the Tailwind conversion without requiring browser/dev-server startup:

- Assert the `/t/news` route renders the expected heading, 12 initial news rows, first thumbnail path, load-more button, and CTA link.
- Add a source-level assertion that the list component no longer imports `resource-list-section.module.css` and contains the expected Tailwind landmarks such as `md:text-[52px]`, `md:max-w-[400px]`, `md:flex-row md:gap-10`, and the bordered load-more button classes.
- Mock unrelated heavy layout components that import CSS Modules if the test only verifies the list shell.

Example command:

```bash
npm exec vitest -- run src/__tests__/app/[locale]/t/news-verification-route.test.tsx
git diff --check
```

## Pitfalls

- Vitest v3 in this repo does not accept Jest-style `--runInBand`; rerun without it.
- Fresh or stale worktree-local `node_modules` can fail PostCSS plugin resolution (`Cannot find module '@tailwindcss/postcss'`) even when the change is not about PostCSS. If the failing import is an unrelated component such as the bottom CTA, mock that component in the targeted test rather than doing a slow install just to validate the news list shell.
- Do not count the older `/{locale}/t/company/news` route as the target when the user explicitly asks for `/{locale}/t/news`; inspect both and edit the actual requested route.
