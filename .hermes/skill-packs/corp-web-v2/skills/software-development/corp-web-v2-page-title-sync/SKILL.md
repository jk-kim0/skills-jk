---
name: corp-web-v2-page-title-sync
description: Diagnose and fix public-page browser titles in corp-web-v2 when pages incorrectly inherit the root `CMS` title or otherwise diverge from https://www.querypie.com.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, metadata, seo, title, localization, querypie]
    related_skills: [systematic-debugging, github-pr-workflow]
---

# corp-web-v2 page title sync

Use this skill when public pages in `corp-web-v2` show the wrong browser tab title, especially when they fall back to `CMS` instead of a page-specific title.

## Why this happens
- The app root metadata in `src/app/layout.tsx` can provide a fallback title.
- If that fallback is left as `CMS`, any route without its own `title` in `generateMetadata()` inherits `CMS`.
- Several public routes may already define canonical URLs in `generateMetadata()` but omit `title`, so the bug is easy to miss.

## Source of truth to inspect
1. Live site titles on `https://www.querypie.com/` and matching locale routes (`/en`, `/ko`, `/ja` where relevant)
2. `src/app/layout.tsx`
3. `src/constants/site.ts`
4. The target route files under `src/app/[locale]/**/page.tsx`

## Workflow
1. Confirm the live title behavior
   - Open the matching page on `https://www.querypie.com/`
   - Check the route variants the repo serves, especially `/ko/...` and `/ja/...`
   - Record the exact page titles to mirror where appropriate

2. Find the fallback source
   - Inspect `src/app/layout.tsx`
   - If metadata title is `CMS` or another scaffold default, replace it with the real public site fallback title
   - Move the fallback title into `src/constants/site.ts` if it is reused

3. Identify title ownership before editing
   - Do not treat `src/constants/i18n.ts` as a translation store; keep it for locale/path utilities only
   - For pages that already have feature/page copy modules, keep both visible copy and metadata title in that copy module
   - For CMS detail pages, read metadata title directly from managed content (`readContentItem(...).title`)
   - For MDX detail pages, keep using MDX frontmatter titles

4. Find routes that inherit the fallback by accident
   - Search for `generateMetadata` implementations that only return `alternates` or canonical info without `title`
   - Search for any remaining literal `title: "CMS"`
   - Prioritize common public pages first: company pages, feature index pages, and other top-level marketing routes

5. Add route-specific titles using the owning source
   - For copy-backed pages, add `metadataTitle` to the existing copy module rather than hardcoding a second locale map in the route
   - For static groups without an existing copy module, create a small feature-level `pageCopy.ts` next to the domain (for example `src/features/company/pageCopy.ts` or `src/features/content/pageCopy.ts`)
   - In each affected `generateMetadata()`, read `title` from that owning source and keep canonical handling unchanged
   - Match live-site wording where the public site already has an established title

6. Verify no stale fallback remains
   - Search again for `title: "CMS"`
   - Typecheck and build the app
   - If the task also touched another UI area, keep any targeted regression test that already exists for that PR

6. Ship the fix
   - Commit and push the title updates to the active PR branch
   - Update the PR description if the scope expanded beyond the original change

## Known good patterns
- `src/constants/site.ts`
  - define `siteTitle = "QueryPie AI: AI That Gets How You Work"`
- `src/app/layout.tsx`
  - import `siteTitle`
  - use it as the root metadata `title`
- copy-backed route metadata
  - add `metadataTitle` to the page's existing copy module
  - example sources used successfully:
    - `src/features/contact/copy.ts`
    - `src/features/community-license/copy.ts`
    - `src/features/company/pageCopy.ts`
    - `src/features/content/pageCopy.ts`
  - return `{ title: metadataTitle, alternates: { canonical: ... } }`
- CMS detail route metadata
  - `const currentEntry = await readContentItem(section, slug, { includeBodies: false })`
  - `title: getLocalizedContent(currentEntry.title, locale)`
- MDX detail route metadata
  - keep `title: frontmatter.title`

## Pages previously found to need explicit titles
Top-level public pages:
- `/`
- `/plans`
- `/company/about-us`
- `/company/certifications`
- `/company/news`
- `/company/contact-us`
- `/community-license`
- `/features/demo`
- `/features/documentation`
- `/terms-of-service`
- `/privacy-policy`
- `/privacy-policy/[version]`
- `/eula`
- `/cookie-preference`

Managed-content-backed detail pages:
- `/company/news/[slug]`
- `/features/demo/[slug]`
- `/features/documentation/[slug]`
- `/features/demo/[slug]/download`
- `/features/documentation/[slug]/download`

MDX pages that should keep frontmatter titles:
- `/blog/[id]/[[...rest]]`
- `/white-paper/[id]/[[...rest]]`

Routes intentionally left alone because they immediately call `notFound()`:
- `/acp-not-found`
- `/aip-not-found`
- `/fdes-not-found`

## Extra repo workflow finding
- Before continuing title work on an existing branch, check whether its PR is still open.
- If the prior PR was already merged or the remote branch is gone, create a fresh branch from `origin/main` before committing and pushing more title fixes.

## Verification
```bash
npm run typecheck
npm run build
```

Optional search checks:
```bash
rg 'title: "CMS"' src
rg 'generateMetadata' src/app/[locale]
```

## Pitfalls
- Do not assume the live site uses the same visible heading and browser title
- Do not only fix the root fallback; pages that should have their own titles still need explicit metadata
- Do not hardcode English-only titles when the live site already differs in Japanese
- Keep canonical URLs intact while adding title metadata
