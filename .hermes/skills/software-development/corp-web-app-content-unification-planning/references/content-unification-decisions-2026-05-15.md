# corp-web-app content-unification decisions — 2026-05-15

Session outcome: PR #623 introduced the content-unification plan; PR #626 recorded the decisions below as `docs/global-site-upgrade-content-unification-decisions.md`.

## Confirmed decisions

1. corp-web-japan guidance import
   - Inventory all corp-web-japan docs/guidance/repo-local skills.
   - Classify each as `copy as-is`, `adapt`, or `exclude`.
   - Manifest path: `docs/imports/corp-web-japan-guidance-manifest.md`.
   - Target docs/guidance under `docs/`; target repo-local skills under `.agents/skills/`.

2. Public route policy
   - `/features/**` is legacy, not canonical for new/migrated implementations.
   - Canonical families: `/blog`, `/white-papers`, `/webinars`, `/demo/use-cases`, `/demo/aip`, `/demo/acp`.
   - When canonical routes are publicly released, matching legacy `/features/**` routes initially use `307 Temporary Redirect`; permanent redirect conversion is a later separate decision.

3. Content ID policy
   - Preserve existing corp-web-contents numeric IDs.
   - Default assumption: corp-web-japan numeric IDs and corp-web-contents numeric IDs are identical.
   - Verify equality per collection migration PR.
   - If mismatched, do not silently renumber; investigate/root-cause and split resolution separately.

4. Locale fallback policy
   - Public routes allow English fallback.
   - `/t/*` verification routes expose missing locales as 404.
   - Public fallback detail pages use the English canonical URL.
   - Public locale list pages hide missing-locale content; direct detail URL access may fallback to English.

5. `/t/*` verification policy
   - Every endpoint/collection migration is first exposed through `/t/*`.
   - Canonical public route connection happens in a separate public-release PR.
   - `/t/*` routes are excluded from sitemap, use the final public URL as canonical, and are not linked from public navigation.

6. Blob/corp-web-contents operational scope
   - Blob Storage and corp-web-contents operational cleanup is completely out of migration scope.
   - Do not target Blob removal, env-var deletion, corp-web-contents archive/read-only/delete, upload workflow deletion, or residual-reference cleanup.
   - Even if references remain after endpoint/collection migration, ignore them for this migration scope unless the user explicitly requests separate operational cleanup.

## PR follow-up pattern observed

After PR #626 was opened, PR #625 changed README's docs index and caused `mergeStateStatus=DIRTY` on #626. The correct fix was:

1. Rebase the open PR branch onto latest `origin/main`.
2. Resolve README docs-index conflicts by preserving the newer main wording and inserting only the new decision-record row.
3. Run docs-only checks (`git diff --check` plus conflict-marker/line-prefix scan).
4. Force-push with lease to the same PR branch.
5. Verify PR head SHA and `mergeable=MERGEABLE`; `mergeStateStatus=BLOCKED` after push meant checks were pending, not conflict remaining.
