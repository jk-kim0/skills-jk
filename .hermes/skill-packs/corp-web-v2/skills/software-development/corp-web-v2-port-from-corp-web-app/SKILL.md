---
name: corp-web-v2-port-from-corp-web-app
description: Port an existing feature from corp-web-app into corp-web-v2 by locating the original commit(s), reproducing behavior with tests first, and delivering the change through a clean worktree PR.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-v2, corp-web-app, porting, mdx, nextjs, worktree, tdd]
    related_skills: [test-driven-development, github-pr-workflow]
---

# Porting a feature from corp-web-app to corp-web-v2

Use this when the user says a feature existed in `corp-web-app` and wants it added to `corp-web-v2`, especially when they reference an old commit or expect parity with prior behavior.

## When to use
- User mentions `../corp-web-app/` has the prior implementation
- User asks to reuse an old commit/log as reference
- corp-web-v2 already has local unrelated modifications, so isolation matters
- The feature touches MDX/rendering/components and should be verified with tests and PR CI

## Workflow

1. Confirm current repo state before editing.
   - In `corp-web-v2`, run:
     - `git status -sb`
     - `git branch --show-current`
   - If the working tree is dirty or on an unrelated branch, do not edit in place.

2. Create an isolated worktree from `origin/main`.
   - Example:
     - `git fetch origin`
     - `git worktree add ../corp-web-v2-<topic> -b feat/<topic> origin/main`
   - Use the new worktree for all changes.

3. Read required repo context files in the new worktree.
   - `README.md`
   - `next.config.ts`
   - `src/features/content/config.ts`
   - `src/constants/navigation.ts`

4. Mine the legacy implementation from `corp-web-app`.
   - Search commit history first:
     - `git log --oneline --decorate --all --grep='<keyword>' -n 30`
   - Then inspect the exact commits/files with `git show`.
   - For Mermaid/MDX-type ports, inspect both the initial feature commit and any follow-up fix commits.

5. Translate the old behavior to corp-web-v2 patterns instead of copying blindly.
   - Compare the old architecture with current corp-web-v2 equivalents.
   - For MDX features in corp-web-v2, inspect `src/features/mdx/*` before implementing.
   - Reuse current styling/utilities where possible instead of bringing old CSS module structure over unchanged.

6. Follow TDD strictly.
   - Add failing tests first.
   - For MDX rendering changes, prefer:
     - component routing tests in `src/features/mdx/components.test.tsx`
     - dedicated component tests for success/error states in a new `*.test.tsx`
   - Run the targeted tests and confirm they fail for the expected reason before implementing.

7. Implement the smallest compatible change.
   - Keep existing non-target behavior unchanged.
   - Example Mermaid pattern that worked well in corp-web-v2:
     - intercept MDX `pre` blocks
     - detect `language-mermaid`
     - render a client component that dynamically imports `mermaid`
     - preserve normal `pre` rendering for every other language

8. Verify locally.
   - Install dependencies in the new worktree if needed: `npm install`
   - Run targeted tests for the changed area
   - Run broader relevant suite, e.g. `npm run test:run -- src/features/mdx`
   - Run `npm run typecheck`

9. Commit, push, open Draft PR, and wait for CI.
   - Commit after verification
   - Push branch
   - Create Draft PR with legacy commit references in the body when helpful
   - Use `env -u GITHUB_TOKEN gh ...`
   - Wait for checks to finish; do not stop at “pending”

## Mermaid-specific findings
- In corp-web-v2 MDX, overriding `pre` was enough to route fenced Mermaid blocks to a custom renderer.
- A client `MermaidDiagram` component using `await import("mermaid")` kept the dependency isolated to the browser path.
- Useful UI states:
  - loading text while rendering
  - explicit error box with Mermaid parse/render message
- Container styling should support wide diagrams with `overflow-x-auto` and avoid forcing SVG to shrink awkwardly.
- If the user also wants old internal MDX guide/sample pages, the source content may live in `corp-web-contents` rather than `corp-web-app`.
  - Example source used successfully: `corp-web-contents/pages/internal/mdx-guide/mermaid-diagrams/en/content.mdx`
  - In corp-web-v2, copy the content under `src/content/internal/...` and load it with a small dedicated loader such as `src/features/mdx/internalLoader.ts`, reusing the same locale→`en` fallback behavior as the main MDX loader.
  - For multiple internal pages, prefer one catch-all App Router page like `src/app/[locale]/internal/[[...slug]]/page.tsx` plus an explicit whitelist helper such as `src/features/mdx/internalPaths.ts` instead of creating one page file per article.
  - This worked well for migrating `/internal`, `/internal/sample-article`, and the `/internal/mdx-guide/*` pages while intentionally excluding `/internal/plans` and `/internal/mdx-preview`.

## Author-box / localized metadata findings
- When `corp-web-app` depends on layout data that does not exist in `corp-web-v2`, check `corp-web-contents` for the canonical source before inventing a new schema.
- For article author boxes, a workable pattern was:
  1. keep MDX frontmatter `author` values as the source of which authors to render
  2. copy locale-specific author registry data from `corp-web-contents/layout/{en,ko,ja}/author.json` into a small v2-side registry module
  3. normalize `public/...` asset paths to web `/...` paths at read time
  4. render a shared author-box component from the resolved author objects
- Preserve unregistered/guest author names in the article header, but restrict the rich author-intro box to registered authors with profile metadata.
- Prefer shortening copied profile image assets to `corp-web-v2/public/crew/*` and rewrite registry entries to `crew/<file>` rather than keeping either the longer legacy `public/querypie-company/crew/*` path or redundant `public/crew/<file>` values.
- In rendering, normalize stored image paths defensively so `public/crew/...`, `crew/...`, and `/crew/...` all become runtime `/crew/...` URLs.
- Keep the shared component name generic (`AuthorBox.tsx`) unless there is a real need to distinguish article-specific behavior.
- Tests should cover mixed-author cases (registered + unregistered), locale-specific display names/translations, `/crew/...` image URLs, and the no-box fallback when only unregistered authors exist.

## Solutions / route-parity findings
- For `corp-web-v2` public-site parity work, do not treat placeholder pages like `/aip-not-found`, `/acp-not-found`, and `/fdes-not-found` as the full scope. First inspect the GitHub wiki migration page plus legacy redirects/content to recover the real public route family and alias relationships.
- A proven pattern for multi-page parity is:
  1. define a canonical route table in a small helper such as `src/features/<domain>/routes.ts`
  2. add route tests first for canonical entries, placeholder redirects, and legacy alias resolution
  3. render the canonical family with one catch-all page such as `src/app/[locale]/solutions/[[...slug]]/page.tsx`
  4. implement legacy aliases as thin App Router redirect pages that call the shared resolver instead of duplicating mapping logic in each route file.
- For Solutions specifically, the legacy canonical family was under `/solutions/...`, while important aliases also existed under `/platform/ai/aip/**`, `/platform/security/*`, `/products/*`, `/resources/manage/*`, `/resources/integrations`, and `/resources/discover/integrations`.
- When migrating legacy MDX-backed static pages, copy the source tree into a dedicated v2 content root such as `src/content/solutions/**` and add a tiny loader module for `meta.json` + `content.mdx` with locale fallback.
- Important loader pitfall: only fall back to `en` on missing-file (`ENOENT`) errors. Do not swallow permission errors or other filesystem failures by returning fallback/null for every read error.
- Legacy public assets may come from both repos, not only `corp-web-contents`. In the Solutions parity work, most assets came from `corp-web-contents/public/*`, but `/assets/dac-analyzer.json` had to be copied from `corp-web-app/public/assets`.
- Legacy MDX custom tags may not map cleanly to existing v2 MDX components. A reusable migration approach is to add a domain-specific adapter module such as `src/features/solutions/mdxComponents.tsx` that:
  - preserves existing MDX source as much as possible
  - normalizes `public/...` asset references to runtime `/...` URLs
  - locale-prefixes internal links
  - provides graceful fallbacks for unsupported widgets instead of blocking the entire migration.
- In `corp-web-v2`, do not assume `npm run lint` exists. Verify the repo's actual scripts first; for this codebase snapshot, `test:run`, `typecheck`, and `build` were the reliable gates, while standalone ESLint also failed if no repo config was present.

## Pitfalls
- A dirty existing worktree can make a small feature request risky; use a separate worktree early.
- New worktrees may not have dependencies installed yet; `vitest: command not found` usually means `npm install` is needed there.
- Port the follow-up fix commits too, not just the initial feature commit; otherwise you may reintroduce known layout issues.
- Do not assume old repo component structure maps 1:1 to corp-web-v2.

## Evidence checklist before finishing
- Legacy commit(s) identified and inspected
- Failing tests added first
- Targeted tests pass
- Broader relevant suite passes
- Typecheck passes
- Branch pushed
- Draft PR created
- CI checks complete successfully
