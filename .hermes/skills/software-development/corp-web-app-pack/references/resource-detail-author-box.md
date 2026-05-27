# Resource detail author boxes in corp-web-app

Use this when adding author information to migrated `/<locale>/t/*` resource detail pages, especially blog and whitepaper detail routes.

## Proven pattern

1. Keep author copy in the existing localized author data source, not in route components.
   - Source: `src/content/authors/{en,ja,ko}.json`
   - Resolver: `src/utils/author/author.ts` (`composeAuthors`), with imports pointing at the content JSON files
2. Parse the MDX `author` frontmatter into the shared resource record model.
   - Current location after PR #895: `src/lib/resources/resource-collection.ts`
   - Add/keep a normalized `author: string | string[] | null` field on `ResourceRecord`.
   - Normalize empty strings and empty arrays to `null`.
3. In each detail route page, resolve authors with the route locale before rendering.
   - Example shape:
     ```ts
     const authors = detail.post.author ? await composeAuthors(detail.post.author, locale) : [];
     return <BlogDetailPostPage locale={locale} post={detail.post} authors={authors} ... />;
     ```
4. Put the reusable author UI in the shared resource detail component surface, not in one blog/whitepaper-only file.
   - Current export surface: `src/components/sections/resource-detail.ts`
   - Current implementation surface: `src/components/sections/resource-detail/resource-detail.component.tsx`
5. Match the `corp-web-japan` `AuthorBox` visual structure closely, but adapt field names to corp-web-app author data:
   - `avatarSrc` -> `profileImage` normalized from `public/...` to `/...`
   - `role` -> `position`
   - `bio` -> `description`
   - `profileUrl` -> first `urls[]` entry with `type === 'linkedin'`
   - Do not blindly keep corp-web-japan's small lucide icon sizing (`h-[15px] w-[15px]`) when the visual target is an existing corp-web-app/stage legacy page. For author LinkedIn icons, stage/legacy rendered the SVG box at `40px x 40px`.
   - For the author LinkedIn icon color, use browser-computed stage/legacy evidence rather than a Tailwind approximate. In the Replit blog author card, the author LinkedIn SVG path fill measured as `rgb(87, 96, 106)` / `#57606A`; `text-slate-950` was too dark.
6. Render author boxes in the detail header before the date/share metadata.
   - Blog detail: after `<h1>`, before date/share metadata.
   - Whitepaper detail: after title/description, before date metadata.

## Verification

- Add or update route verification tests under:
  - `src/__tests__/app/[locale]/t/blog-verification-route.test.tsx`
  - `src/__tests__/app/[locale]/t/whitepapers-verification-route.test.tsx`
- Assert real localized author fields from the data source, e.g. Korean Brant bio or Japanese Terazawa bio.
- When author images are introduced, do not rely on `getAllByRole('img')[0]` for hero image assertions; the author avatar can become the first image. Query the hero image by its accessible name instead.
- Run:
  ```bash
  npm run test:publications
  git diff --check
  node scripts/ci/assert-test-groups.mjs
  npm run lint
  ```

## Pitfalls

- Latest main may have renamed `src/lib/repo-content/**` to `src/lib/resources/**`. During rebase conflicts, preserve the latest `src/lib/resources/**` imports and reapply only the author-box delta.
- Do not hardcode EN/JA/KO author descriptions in page components. The locale JSON files already own those descriptions.
- Do not add this only to one family if the request covers both blog and whitepaper; keep the record model and shared component reusable.
