---
name: corp-web-app-layout-data-localization
description: Convert corp-web-app shared layout data such as header/GNB/footer from remote blob-backed layout JSON to checked-in local locale modules while preserving locale parity, preview-navigation rewriting, and PR workflow.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, Next.js, layout-data, localization, header, footer, GitHub]
    related_skills: [github-pr-workflow, repo-root-worktree-path-policy, main-checkout-edit-taboo]
---

# corp-web-app layout data localization

Use this when the user asks to make corp-web-app shared layout data stop reading a remote file/blob and instead reference checked-in local files. Typical surfaces are header/GNB and footer data used from `src/app/layout.tsx`.

Important shape preference:
- For first-pass parity migrations, JSON files may match older footer/header precedent.
- When the user asks for route-local-style/static-page-route-local-authoring treatment of layout chrome, prefer locale-specific TSX modules or explicit JSX/TS composition over JSON blobs or central data registries. Header/footer are not page routes, but the same authoring principle applies to site-wide layout chrome.

## Trigger phrases

- "PR #657처럼 gnb/header도 local file 참조"
- "remote file 이 아니라 local file 참조"
- "header/GNB/footer 데이터를 로컬 소스로 전환"
- "layout data fetch 제거"

## Workflow

1. Start from latest `origin/main` in a fresh repo-local worktree.
   - Use `.worktrees/<flat-name>` under the repo root.
   - Verify `git merge-base HEAD origin/main` equals `origin/main` before editing.

2. Inspect the prior local-data pattern first.
   - Footer reference pattern from PR #657/main:
     - `src/components/layout/footer/footer-data.ts`
     - `src/components/layout/footer/data/{en,ja,ko}.json`
     - `src/components/layout/footer/__tests__/footer-data.test.ts`
   - Header first-pass reference pattern from PR #660/main:
     - `src/components/layout/header/header-data.ts`
     - `src/components/layout/header/data/{en,ja,ko}.json`
     - `src/components/layout/header/__tests__/header-data.test.ts`
   - Match this shape for narrow parity migrations unless the user explicitly requests route-local-style authoring.
   - For route-local-style layout authoring, prefer locale modules such as:
     - `src/components/layout/header/header-data.en.tsx`
     - `src/components/layout/header/header-data.ja.tsx`
     - `src/components/layout/header/header-data.ko.tsx`
     and import them from `header-data.ts`.

3. Locate the current remote-backed layout read.
   - In `src/app/layout.tsx`, header previously used:
     - `fileQuery.getLayoutData<HeaderType>(FileType.HEADER, locale)`
   - Replace only the target layout data source. Leave unrelated remote-backed layout files such as cookie banner untouched unless the user explicitly scopes them in.

4. Recover the current remote JSON payload before removing the remote read.
   - Fast source when the public app exposes cached file metadata:
     - `https://www.querypie.com/api/data?branch=main`
   - Find paths like:
     - `main/layout/en/header.json`
     - `main/layout/ja/header.json`
     - `main/layout/ko/header.json`
   - Download each file's `url` and write it to the corresponding checked-in local JSON file.
   - Do not guess or recreate menu labels by hand if the remote source can be queried.

5. Add a typed local data loader.
   - JSON first-pass parity shape:
     ```ts
     import { Locale } from 'src/models/locale';
     import { HeaderType } from 'src/models/layout-data';

     import enHeaderData from './data/en.json';
     import jaHeaderData from './data/ja.json';
     import koHeaderData from './data/ko.json';

     const headerDataByLocale: Record<Locale, HeaderType> = {
       [Locale.EN]: enHeaderData as HeaderType,
       [Locale.JA]: jaHeaderData as HeaderType,
       [Locale.KO]: koHeaderData as HeaderType,
     };

     const getHeaderData = (locale: Locale): HeaderType => headerDataByLocale[locale] ?? headerDataByLocale[Locale.EN];

     export default getHeaderData;
     ```
   - Route-local-style TSX locale-module shape:
     ```ts
     import { Locale } from 'src/models/locale';
     import { HeaderType } from 'src/models/layout-data';

     import enHeaderData from './header-data.en';
     import jaHeaderData from './header-data.ja';
     import koHeaderData from './header-data.ko';

     const headerDataByLocale: Record<Locale, HeaderType> = {
       [Locale.EN]: enHeaderData,
       [Locale.JA]: jaHeaderData,
       [Locale.KO]: koHeaderData,
     };

     const getHeaderData = (locale: Locale): HeaderType => headerDataByLocale[locale] ?? headerDataByLocale[Locale.EN];

     export default getHeaderData;
     ```
   - Each locale module can export a `satisfies HeaderType` object from files such as `header-data.en.tsx`. This removes JSON casts and makes locale authoring visible/editable in TypeScript.
   - Keep the loader colocated with the layout component family, e.g. `src/components/layout/header/header-data.ts`.

6. Update `src/app/layout.tsx` narrowly.
   - Import the local loader.
   - Remove the target `FileType.HEADER` / `HeaderType` remote fetch from the `Promise.all`.
   - Keep `withPreviewNavigation(...)` wrapping for menus and mobile buttons exactly as before so preview mode behavior is preserved.
   - Keep `Header` receiving the same effective data shape.

7. Add or update focused tests.
   - Add a loader test next to the layout family, e.g. `src/components/layout/header/__tests__/header-data.test.ts`.
   - Verify supported locale data exists and key labels/sections are available.
   - For quick verification, run only targeted tests unless the user asked for full local validation:
     - `npx vitest run src/components/layout/header/__tests__/header-data.test.ts src/components/layout/footer/__tests__/footer-data.test.ts`

8. Commit, rebase, push, and open a PR.
   - Use the repo's normal GitHub PR flow.
   - Korean PR title/body is appropriate for this user's corp-web-app repo preference.
   - Do not wait passively for CI; verify fresh checks attached and report current status.

## Pitfalls

- Do not treat every `FileQuery.getLayoutData(...)` call as in-scope. Header/GNB local-data work does not imply changing cookie banner, plans, article categories, or other remote-backed content.
- Do not remove preview-navigation rewriting. Local JSON is still transformed by `withPreviewNavigation(...)` in preview mode.
- When adding preview-only footer/header links, verify the responsive layout contract as well as the data/JSX. In corp-web-app footer, navigation columns live inside `src/components/layout/footer/ui/footer.module.css` `.nav`; a historical `@media (max-width: 1260px) { .nav { display: none; } }` style hid all footer navigation on tablet/mobile, so desktop-only inspection missed that newly added preview links disappeared at mobile widths. Prefer responsive wrapping/stacking and add a source-level regression test that rejects `display: none` for the nav when the requirement is visibility on mobile.
- Do not hand-author Japanese/Korean labels from memory. Pull current remote JSON from the cached metadata endpoint or other authoritative current source.
- File-tool lint may show false import-resolution errors when writing files outside the repo-root context. Verify with the repo's own targeted `npx vitest run ...` command from the worktree.
- JSON data files can be large; use `git diff --stat` plus focused tests instead of pasting full JSON into reports.
- A PR that originally introduced JSON local layout data can become invalid if the same JSON migration lands through another PR first. If the user asks to keep the PR alive, reset/rebase the existing PR branch onto latest `origin/main` and turn it into a narrow follow-up such as JSON-to-TSX locale module authoring, then rewrite the PR title/body to match the new scope.

## References

- `references/header-gnb-local-data-pr-660.md` — session notes for the header/GNB implementation that followed footer PR #657.
- `references/header-json-to-tsx-authoring-pr-658.md` — session notes for rewriting a superseded header JSON PR into a latest-main TSX locale-module authoring follow-up.
- `references/footer-preview-internal-menu-mobile-nav.md` — session notes for the preview-only footer Internal menu and the mobile `.nav { display: none; }` regression.
