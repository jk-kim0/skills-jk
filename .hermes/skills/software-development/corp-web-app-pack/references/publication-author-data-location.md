# Publication author data placement

Use this when adding or refactoring author/profile rendering for migrated publication detail pages in `corp-web-app`.

## Learned pattern

- MDX records carry author references in frontmatter, for example `author: "brant"` or an author ID array.
- The loader should normalize the frontmatter value onto the resource/publication record without resolving profile data inside the loader.
- Route/detail pages can call the existing `composeAuthors(author, locale)` API to resolve locale-specific profile records.
- Localized author/profile JSON is content, not utility implementation. Store it under:

```text
src/content/authors/en.json
src/content/authors/ja.json
src/content/authors/ko.json
```

- Keep `src/utils/author/author-data.ts` as the thin resolver/importer if existing callers already depend on `composeAuthors`; update its imports to `src/content/authors/*.json` instead of `src/utils/author/data/*.json`.

## Rendering pattern

For blog and whitepaper migrated detail routes:

1. Parse `author` frontmatter in the resource collection record type.
2. In the route page, resolve authors with `composeAuthors(detail.post.author, locale)`.
3. Pass the resolved authors into the detail component.
4. Render an author card component that mirrors `corp-web-japan`'s `AuthorBox` structure: avatar, name, role/position, optional LinkedIn link, and bio/description.
5. Preserve `composeAuthors` fallback behavior: unknown strings can render as plain author names, while registered IDs render full localized profiles.

## Verification

- Add route tests that assert localized author name, position, description, and profile link for at least one blog and one whitepaper detail page.
- If author cards add an image before the hero image, update tests to select the hero image by accessible name rather than by `getAllByRole('img')[0]`.
- Run `npm run test:publications`, `git diff --check`, `node scripts/ci/assert-test-groups.mjs`, and `npm run lint` when updating the PR.

## Rebase pitfall

Recent corp-web-app main moved resource library imports from `src/lib/repo-content/**` to `src/lib/resources/**`. If a PR branch created before that rename conflicts during rebase, keep the latest-main `src/lib/resources` paths and reapply only the scoped author-rendering/content-location changes.
