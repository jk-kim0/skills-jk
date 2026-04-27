---
name: corp-web-japan-resource-externalization-pr
description: Keep local resource index pages in corp-web-japan while routing non-original resource detail posts to mapped querypie.com/ja URLs, then ship as a PR.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, nextjs, resources, redirects, github, pr]
---

# corp-web-japan resource externalization PR workflow

Use this when a corp-web-japan task says to keep a resource index page (such as `/blog`, `/whitepapers`, `/events`) but remove local detail-post rendering and send users to the corresponding `querypie.com/ja` posting instead.

Important: corp-web-japan is not publicly launched yet. Do not add legacy redirects for old local URLs unless the user explicitly asks for them.

## When to use
- The user wants to preserve a local index/list page.
- Individual resource posts are considered non-original and should point to `querypie.com/ja`.
- The task should end with a reviewable PR.

## Expected repo pattern
- Resource index card data may start in `src/content/resources.ts`, but for category-specific cleanup it is often better to split category data into a dedicated file while keeping shared types in `src/content/resources.ts`.
  - Practical pattern used here:
    - keep shared `ResourceItem` type and any truly shared helpers in `src/content/resources.ts`
    - move whitepaper listing data into `src/content/whitepapers.ts`
    - update only the direct import sites that actually consume the moved data (for example `src/app/whitepapers/page.tsx` and `src/lib/resource-posts.ts`)
    - avoid broad barrel/refactor work unless the task specifically asks for it
- When normalizing thumbnail asset paths, use category-specific index conventions for assets owned by the local resource index data.
  - Whitepaper index items should use `/assets/image/whitepapers/{id}/thumbnail.png` (for example entries in `src/content/whitepapers.ts`).
  - Blog index items should use `/assets/image/blog/{id}/thumbnail.png` once the blog index is externalized and the local blog detail pages are removed. Use the external QueryPie blog ID as `{id}` so the asset path matches the card's canonical destination.
  - Event index items should use `/assets/image/events/{id}/thumbnail.png` when the event cards are fake/local catalog data and their thumbnails belong to the event index itself.
- When normalizing thumbnail asset paths, follow a category-specific thumbnail convention for images that belong to the index data itself.
  - Whitepaper index thumbnails use `/assets/image/whitepapers/{id}/thumbnail.png` (for example entries in `src/content/whitepapers.ts`).
  - Event index thumbnails should mirror that pattern as `/assets/image/events/{id}/thumbnail.png` (for example entries in `src/content/resources/events.ts`).
  - If you rename the asset convention in code, also move/rename the actual files under `public/assets/image/<category>/{id}/thumbnail.png` in the same PR.
  - If a cover image is used only as supporting content in another surface, keep or move it to a context-appropriate asset location instead of forcing it into the shared index-asset namespace.
  - Use the canonical asset path for the page that owns that cover. If another page only references the image secondarily, it can keep using that canonical path instead of duplicating the asset.
  - If the same supporting image is shared by multiple non-index surfaces, prefer one clear owner path and reuse it from the other surface rather than keeping duplicate copies.
  - For solution-marketing surfaces, a solution-specific asset path such as `/solutions/ai-dashi/...` is often more appropriate than a generic category-assets path.
  - Use meaning-based filenames for non-index supporting images when possible.
  - Do not create extra thumbnail assets for unreferenced IDs just to make the directory tree look complete.
  - If the event data is clearly placeholder or fake seed content, simple numeric IDs (`1`, `2`, `3`) are acceptable and may be preferable to pseudo-real slugs like `ev-005`, as long as the source HTML filenames, related-post links, and index-card href values are all updated consistently.

- Shared resource-post helpers live in `src/lib/resource-posts.ts`.
- Legacy source HTML for a removed category may still live under `content/source-posts/<category>` and should be deleted if the category is no longer served locally.
- Because `corp-web-japan` is still pre-launch, when the user says old content does not need to be preserved, prefer fully deleting the removed category's local source HTML instead of keeping dormant files around.

## Workflow
1. Check issue and open PRs first.
   - `gh issue view <num> --json ...`
   - `gh pr list --state open --limit 30 --json ...`
2. Create a new worktree and branch from `origin/main`.
   - Prefer `.worktrees/<branch-name>`.
3. Update the index cards in `src/content/resources.ts`.
   - Replace local `href` values like `/posts/<category>/<slug>` with the mapped absolute `https://www.querypie.com/ja/...` URLs.
   - Align the index route itself with the current URI guide. For whitepapers, use `/whitepapers` rather than `/whitepaper`.
   - Update header/footer/sidebar/CTA links that point at the local index route.
   - It is acceptable, and often simplest in this repo, to keep the affected category's external URL map beside the index-card data in `src/content/resources.ts` or directly inline if only the card links need changing.
   - If the local detail route for that category is removed and no other code needs slug-based URL lookup anymore, prefer inlining the final external URLs directly in the index-card `href` values instead of keeping a separate slug-to-URL helper map.
4. Decide whether old local detail URLs should keep working.
   - Default for this repo: if the site is still pre-launch, do not preserve legacy local post URLs unless the user explicitly asks.
   - If legacy compatibility is explicitly requested, normalize incoming slugs before lookup. `generateStaticParams()` may emit filenames such as `b-001.html`, so helpers must strip a trailing `.html` before reading the map.
   - If you split out the affected category's content data during the same PR, prefer a minimal extraction for that category over a broad multi-category refactor.
5. Remove or keep local detail routes based on the request.
   - If compatibility is explicitly requested, redirect mapped local post URLs in `src/app/posts/[category]/[slug]/page.tsx`.
   - If compatibility is not requested, stop generating that category in `listResourcePostParams()` and return `notFound()` for that category in `src/app/posts/[category]/[slug]/page.tsx`.
   - Prefer checking only the categories that are actually served by the route (for example via `isStaticResourcePostCategory`) instead of checking a broader enum and then special-casing `whitepaper`.
   - Also short-circuit `generateMetadata()` for removed categories so deleted local post routes do not emit stale article title/description metadata.
   - After removing a category from local delivery, delete its unused source HTML under `content/source-posts/<category>`.
6. Verify.
   - Run `npm run test:ci`.
   - Run `npm run build`.
   - If route files were renamed or removed, clear stale `.next` state before re-running typecheck/dev if Next keeps referencing removed pages.
   - Browser-check that the index page links point to the expected `querypie.com/ja` URLs.
   - Browser-check the intended detail-route behavior: redirect only if explicitly requested; otherwise confirm 404/not found.
   - When checking deleted local detail routes, verify both slug forms if relevant: `/posts/<category>/<slug>` and `/posts/<category>/<slug>.html`.
7. Commit, push, and open a PR that references the issue.

## Important implementation notes
- Keep changes minimal and focused on the requested category.
- Do not remove the local index route unless explicitly requested.
- Follow the current URI guide for resource indexes: `/blog`, `/whitepapers`, `/events`.
- Do not add legacy redirects for pre-launch route renames unless the user explicitly wants them.
- Keep mapping data in code only for the affected category; avoid unrelated refactors.

## Worktree dependency and package-lock pitfalls
A fresh git worktree may not have `node_modules` populated even if the main checkout does. If `npm run test:ci` fails immediately with errors like `eslint: command not found`, check whether `node_modules/.bin/eslint` exists in the worktree.
- If dependencies are missing in the worktree, run `npm ci` there before verification.
- After `npm ci`, rerun `npm run test:ci` and `npm run build`.

If you run `npm install` or `npm ci` inside the worktree, `package-lock.json` may change due to npm/environment differences even when dependencies were not intentionally updated.
- Before committing, inspect `git diff -- package-lock.json`.
- If the lockfile change is unrelated to the task, revert it with `git checkout -- package-lock.json`.
- Next.js may also warn about multiple lockfiles when building from a worktree; this warning is acceptable for verification as long as the actual build succeeds and `package-lock.json` is not unintentionally modified.
- This avoids PR noise while still allowing local verification.

## Verification checklist
- The target index route renders locally, using the guided URI (`/blog`, `/whitepapers`, or `/events`).
- Index cards point to `querypie.com/ja` URLs.
- If compatibility was requested, `/posts/<category>/<slug>` redirects for all mapped slugs.
- If compatibility was not requested, removed local detail routes return 404.
- Unused source HTML for the removed category has been deleted from `content/source-posts/<category>`.
- `npm run test:ci` passes.
- `npm run build` passes.

## PR targeting guardrail
When the user refers to a specific open PR by number, treat that PR as the source of truth for where follow-up edits must land.

1. Inspect the PR before editing.
   - `gh pr view <num> --json headRefName,baseRefName,files,commits,url`
2. Verify the target branch/worktree before making changes.
   - Do not keep working on the last branch just because it is already checked out.
   - If the branch already has a worktree, reuse that worktree instead of trying to check the same branch out elsewhere.
   - If `git worktree add <path> origin/<branch>` gives you a detached HEAD, switch to the existing branch worktree or create a proper branch-attached worktree before editing.
3. Before pushing, re-check that `git branch --show-current` matches the PR head branch.
4. After pushing, confirm the PR now contains the intended commit/file set with `gh pr view <num> --json files,commits`.
5. If a follow-up change accidentally lands on the wrong PR branch, fix it immediately by resetting/removing the stray commits from that branch before touching the correct PR.

## Dead local flow cleanup pattern
When a task asks whether local resource-post code is still needed, do not assume the existence of download or gated flows just because the components exist.

1. Inspect the actual categories still served by the local posts route in `src/lib/resource-posts.ts`.
   - In current corp-web-japan, `STATIC_ROUTE_CATEGORIES` is the source of truth.
   - Blog and whitepaper index items may already be fully externalized even if generic resource-post helpers still mention those categories.
2. Search the source HTML under `content/source-posts/` for the real content markers before keeping any special-case renderer.
   - gated flow markers: `gating-wall`, `article-gated-content`
   - download flow marker: `wp-dl-wrap`
3. If those markers are absent across the repository, treat the related branches/components as dead code.
   - Remove `getResourceDownloadPost()` and related types from `src/lib/resource-posts.ts`.
   - Remove gated/download rendering branches from `src/app/posts/[category]/[slug]/page.tsx` and `src/components/sections/resource-post-page.tsx`.
   - Delete now-unreferenced components such as `resource-lead-form.tsx`, `resource-post-download-page.tsx`, and `resource-post-gated.tsx`.
4. Keep the cleanup minimal if local event posts still exist.
   - If `/posts/event/*` is still intentionally local, simplify the route to render only standard event posts rather than expanding the cleanup into a broader `/events` deprecation unless the user asks for that.
   - If the user says the `/events` page should stay hidden for now, prefer preserving the previous page composition as commented-out code in `src/app/events/page.tsx` with an English `TODO` explaining that the route should be exposed only when real externally publishable event content is ready.
   - In that case, implement the current behavior as `return notFound();` rather than deleting the old page copy outright.
   - If `src/components/sections/resource-page.tsx` is shared across categories, add a minimal guard so `activeCategory === "events"` renders no cards while the events surface remains pre-launch.
5. In a fresh worktree, verification may fail with `eslint: command not found` or `next: command not found` because dependencies are not installed locally.
   - Run `npm ci` in the worktree, then rerun `npm run test:ci` and `npm run build`.

## Example from issue #52
For whitepapers:
- Renamed the index route to `/whitepapers` and updated header/footer/sidebar/CTA links.
- Kept the local index page, but linked whitepaper cards to absolute `querypie.com/ja` whitepaper URLs.
- Removed local whitepaper detail serving by excluding `whitepaper` from generated post params and returning 404 for `/posts/whitepaper/*`.
- Simplified route checks to validate only categories actually served by the posts route instead of special-casing `whitepaper`.
- Split whitepaper listing data into `src/content/whitepapers.ts` while keeping shared resource types in `src/content/resources.ts`.
- Deleted unused `content/source-posts/whitepaper` HTML files.
- Reverted unrelated `package-lock.json` noise before commit when needed.
