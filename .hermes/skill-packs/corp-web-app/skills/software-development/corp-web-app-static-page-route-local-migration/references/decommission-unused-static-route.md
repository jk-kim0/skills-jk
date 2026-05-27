# Decommissioning an unused corp-web-app static route

Use this reference when the user asks to delete an unused static page such as `/<locale>/<route>` or `src/app/[locale]/<route>`.

## Procedure

1. Start from latest `origin/main` in a fresh `.worktrees/<flat-name>` worktree.
2. Locate the exact route owner under `src/app/**`.
   - For `/{locale}/foo`, check both explicit locale directories like `src/app/ja/foo` and dynamic locale routes like `src/app/[locale]/foo`.
   - Read the route entry before deletion; a dynamic `[locale]` route can intentionally 404 non-target locales.
3. Search for route references before editing:
   - exact public paths such as `/ja/foo`
   - dynamic route paths such as `[locale]/foo`
   - code symbols such as `FooPage` / `FooJa`
4. Delete only the public route files requested.
   - Do not delete similarly named internal/demo routes such as `/en/internal/foo` unless the user explicitly includes them.
   - If an internal index points only to the internal route, leave it unchanged.
5. Update docs or inventories that explicitly list the removed public route.
6. Verify narrowly:
   - `git diff --check`
   - search again for the removed public path and route directory references
   - confirm any remaining matches are intentionally separate routes, usually `/internal/...`.
7. Commit, push, and open the PR. In the PR body, explicitly state which similarly named routes were preserved.

## Session pattern

For removing the unused `/{locale}/key-values` public page in corp-web-app, the route owner was `src/app/[locale]/key-values/page.tsx` plus `page.ja.tsx`. The separate internal demo route `src/app/[locale]/internal/key-values/**` and its internal index/test references were left unchanged. The route inventory row for `/ja/key-values` was removed because it was stale after deleting the public route.
