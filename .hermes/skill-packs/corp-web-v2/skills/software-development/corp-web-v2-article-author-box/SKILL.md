---
name: corp-web-v2-article-author-box
description: Implement or refine localized author profile boxes for corp-web-v2 MDX article layouts by porting author registry data and assets from corp-web-contents / corp-web-app, matching MDX frontmatter author IDs, and shipping through the existing PR branch or a fresh worktree as appropriate.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-v2, corp-web-app, corp-web-contents, mdx, author-box, localization, nextjs]
---

# corp-web-v2 article author box

Use when corp-web-v2 blog / white-paper / article MDX pages are missing author profile UI, or when the existing author box needs data-path, naming, or locale follow-up fixes.

## What this skill is for

This workflow was validated while adding localized author boxes to corp-web-v2 and updating the same PR with follow-up refinements.

Proven outcomes:
- ported author profile behavior from `corp-web-app`
- sourced locale-specific author data from `corp-web-contents`
- matched data using MDX frontmatter `author`
- supported guest / unregistered author strings safely
- shipped follow-up path/name refinements onto the same PR branch

## Source-of-truth decisions

1. Use MDX frontmatter `author` as the lookup source of truth.
   - `author` may be a string or string[].
   - Values are usually IDs like `brant`, `terazawa`, `terazawa-ko`, but some content contains display-name strings like `Jessica Kim`.

2. Keep localized author registry data inside corp-web-v2 under:
   - `src/features/mdx/authors/en.yaml`
   - `src/features/mdx/authors/ko.yaml`
   - `src/features/mdx/authors/ja.yaml`
   - with loader logic in `src/features/mdx/authors/index.ts`

3. Keep author profile image assets under:
   - `public/crew/*`

4. In registry data, store image paths without a `public/` prefix:
   - preferred: `crew/brant.png`
   - normalize at runtime to `/crew/brant.png`

5. If an `author` value is not found in the registry:
   - still show the name in the article header
   - do not render a detailed author profile box for that entry
   - if the user explicitly asks to fix migrated MDX author data, first search legacy sources for an existing canonical id or profile record
   - if none exists but the article should participate in the registered-author flow, add a minimal trustworthy registry record (`id`, `name`, optional empty `urls`) and normalize the MDX frontmatter to that canonical id
   - do not fabricate bios, titles, profile images, or social links

## Relevant legacy sources

Inspect these first:
- `../corp-web-app/src/components/widget/article/authors-information.component.tsx`
- `../corp-web-app/src/components/widget/article/authors-information.module.css`
- `../corp-web-app/src/utils/author/author.ts`
- `../corp-web-contents/layout/en/author.json`
- `../corp-web-contents/layout/ko/author.json`
- `../corp-web-contents/layout/ja/author.json`
- `../corp-web-contents/public/querypie-company/crew/*`

## corp-web-v2 target files

Typical implementation files:
- `src/features/mdx/authors/index.ts`
- `src/components/mdx-layout/AuthorBox.tsx`
- `src/components/mdx-layout/BlogLayout.tsx`
- `src/components/mdx-layout/WhitePaperLayout.tsx`
- `src/features/mdx/authors.test.ts`
- `src/components/mdx-layout/BlogLayout.test.tsx`
- `src/components/mdx-layout/WhitePaperLayout.test.tsx`

## Workflow

### 1. Start on the correct git line

For a new task:
- create a fresh worktree from latest `origin/main`

For follow-up to an open PR:
- use a fresh worktree on the existing PR branch, then push back to that same branch

### 2. Inspect current corp-web-v2 article rendering

Read:
- `src/components/mdx-layout/BlogLayout.tsx`
- `src/components/mdx-layout/WhitePaperLayout.tsx`
- `src/features/mdx/types.ts`

Confirm:
- where article header author text is built
- where post-body components can be inserted
- `frontmatter.author` type and existing usage

### 3. Add tests first

Before implementation, add targeted tests for:
- localized registered author resolution
- guest / unregistered author fallback behavior
- string[] author order preservation
- article header name rendering
- detailed author box rendering only for registered authors
- locale-specific heading strings
- image src normalization to `/crew/...`

Useful files:
- `src/features/mdx/authors.test.ts`
- `src/components/mdx-layout/BlogLayout.test.tsx`
- `src/components/mdx-layout/WhitePaperLayout.test.tsx`

### 4. Port the data and assets

Copy locale author records from corp-web-contents into corp-web-v2 registry files.

Important refinements validated during implementation:
- do not keep `public/querypie-company/crew/...`
- move images to `public/crew/*`
- use compact registry paths like `crew/brant.png`
- keep only YAML source files in git; do not commit generated JSON copies

### 5. Implement author resolution logic

In `src/features/mdx/authors/index.ts`:
- mark the module `server-only`
- read locale YAML files with `fs` + `path`
- parse them with the `yaml` package
- normalize `frontmatter.author` into a trimmed string[]
- build locale-specific lookup map by `id`
- return resolved author objects with:
  - `id`
  - `isRegistered`
  - localized `name`
  - `position`
  - `description`
  - normalized `profileImageSrc`
  - `links`

Runtime image normalization should accept any of these inputs and convert them to `/crew/...` form:
- `public/crew/brant.png`
- `crew/brant.png`
- `/crew/brant.png`

Recommended normalization pattern:
- strip optional leading `public/`
- strip leading slash
- prepend one canonical `/`

### 6. Render the UI

Use a shared component:
- `src/components/mdx-layout/AuthorBox.tsx`

Render:
- avatar image
- localized name
- localized position
- localized description paragraphs
- LinkedIn icon link when present

Current public-content composition reference:
- place the author card block immediately below the article title
- do not render an extra section heading like `About the author` / `작성자 소개` / `著者紹介`
- show the publish date after the author card block, then continue with hero image and body

The file name should stay concise:
- prefer `AuthorBox.tsx`
- avoid longer `ArticleAuthorBox.tsx`

Locale heading strings validated in production-style usage:
- en: `About the author`
- ko: `작성자 소개`
- ja: `著者紹介`

### 7. Wire layouts

In both:
- `BlogLayout.tsx`
- `WhitePaperLayout.tsx`

Do all of the following:
- resolve `frontmatter.author`
- show localized author names in the header
- render the detailed author box after the MDX body
- skip the box when no registered authors remain

### 8. Validate thoroughly

Run at minimum:
- `npm run test:run -- src/features/mdx/authors.test.ts src/components/mdx-layout/BlogLayout.test.tsx src/components/mdx-layout/WhitePaperLayout.test.tsx`
- `npm run typecheck`

If the change is broader, also run:
- `npm run test:run`

### 9. PR workflow

Before commit/push:
- review diffs
- run static secret/risky-pattern scan if you changed copied data or links
- request an independent review when the change is non-trivial

Then:
- commit with `[verified] ...`
- push to the working branch
- create or update the PR
- monitor CI until green

## Pitfalls

1. Do not assume all author values are registry IDs.
   - guest/display-name strings exist in content

2. Do not render blank or broken author boxes for unknown authors.

3. Do not keep old image path conventions from corp-web-contents.
   - old: `public/querypie-company/crew/...`
   - intermediate: `public/crew/...`
   - preferred registry value: `crew/...`
   - rendered value: `/crew/...`

4. Do not over-refactor the module layout unless author logic grows substantially.
   - current structure is clean as `authors.ts + author-data/`

5. If the user asks about YAML for readability, do not jump straight to webpack YAML import loaders.
   - in this repo, the simplest future YAML path is a server-only loader using `fs` + `yaml.parse`
   - direct JSON import remains the lowest-complexity runtime approach

## Verification checklist

- Header author names are localized for registered authors
- Guest/unregistered author names still show in header
- Author box renders only for registered authors
- Blog layout works
- White-paper layout works
- `profileImage` registry values normalize to `/crew/...`
- LinkedIn links render when present
- Header author card block sits directly below the article title
- Publish date appears after the author card block
- Hero image and body remain below the metadata area
- tests and typecheck pass
