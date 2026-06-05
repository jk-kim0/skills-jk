# Lingo-web sibling migration into corp-web-japan

Use this reference when refreshing `corp-web-japan/src/app/lingo/**` from the sibling `../lingo-web` repository or maintaining the durable Lingo migration contract.

## Durable workflow

1. Start from latest `origin/main` in a fresh corp-web-japan worktree or the existing PR worktree for the active Lingo PR.
2. Inspect `../lingo-web` state and recent commits before copying:
   - `git -C ../lingo-web status --short --branch`
   - `git -C ../lingo-web log --oneline -15`
   - list `app/[locale]/**/page.tsx`, `components/**`, `messages/*.json`, `public/images/**`.
3. Treat existing `src/app/lingo` as a namespaced snapshot, not a direct drop-in Next Intl app.
4. Copy source pages/components/assets, then adapt paths and imports:
   - `next-intl` -> `@/lib/lingo/intl`
   - `@/components/common/*` -> `@/components/lingo/common/*`
   - `@/components/layout/*` -> `@/components/layout/lingo/*`
   - `@/components/sections/*` -> `@/components/sections/lingo/*`
   - `@/components/home/*` -> `@/components/sections/lingo/home/*`
   - `@/components/mockup/*` -> `@/components/lingo/mockup/*`
   - `@/lib/*` lingo helpers -> `@/lib/lingo/*`
   - `/images/...` -> `/lingo/images/...`
   - `/symbol.png` -> `/lingo/symbol.png`
5. Preserve corp-web-japan route and link policy after copying:
   - Lingo-internal links must stay under `/lingo/**`, not `/${locale}/...`.
   - Do not reintroduce locale routes like `/ja`, `/ko`, `/en` inside corp-web-japan.
   - Same-site `querypie.ai` destinations must be root-relative paths such as `/about-us`, `/contact-us`, `/terms-of-service`, `/privacy-policy`, and `/eula`, and must open in the current tab/window.
   - The same-site rule applies to Footer, GNB, CTA buttons, cookie consent, and all other in-page links. Do not copy `https://querypie.ai/...` or `https://www.querypie.ai/...` literally into Lingo implementation code.
   - For migrated `querypie.com` source links that correspond to implemented `querypie.ai` pages, normalize to the local route rather than preserving the legacy absolute URL.
   - Do not keep `target="_blank"` / `rel="noopener noreferrer"` on same-site root-relative navigation. External hosts can still use external-link behavior.
6. Keep `src/app/lingo/README.md` as a short handoff and make OpenSpec the canonical durable contract. The OpenSpec spec is `openspec/specs/contract-lingo-website-migration/spec.md`.
7. If source code calls `t(key, values)`, ensure the local `@/lib/lingo/intl` shim supports simple placeholder interpolation such as `{id}`.

## Verification

Run stale-path searches before committing, covering at least these roots:

```text
src/app/lingo
src/components/lingo
src/components/sections/lingo
src/components/layout/lingo
src/lib/lingo
```

Search for:

```bash
rg -n 'from "next-intl"|from '\''next-intl'\''|href=\{?`?/\$\{locale\}|router\.push\(`/|href="/(ko|ja|en)(/|")|/lingo/lingo' src/app/lingo src/components/lingo src/components/sections/lingo src/components/layout/lingo src/lib/lingo || true
rg -n 'https://(www\.)?querypie\.ai/' src/app/lingo src/components/lingo src/components/sections/lingo src/components/layout/lingo src/lib/lingo || true
rg -n '"/images/|'\''/images/|`/images/|"/symbol\.png|'\''/symbol\.png' src/app/lingo src/components/lingo src/components/sections/lingo src/components/layout/lingo src/lib/lingo || true
```

Verify with at least:

```bash
node tests/lingo-migration-contract.test.mjs
node scripts/ci/assert-test-groups.mjs
npm run typecheck
git diff --check
```

Use `npm run test:assets-shell` when link/shell/footer/GNB behavior changes or when `tests/lingo-migration-contract.test.mjs` is registered in that group.

## Conflict pattern from Lingo contract PRs

When rebasing a Lingo migration-contract PR after another shell/test PR lands, `scripts/ci/test-groups.mjs` can conflict inside `assetsShell`. Resolve by preserving both independently-added test matchers. For example, keep both `component-name-debug.test.mjs` from main and `lingo-migration-contract.test.mjs` from the Lingo PR, then rerun `node scripts/ci/assert-test-groups.mjs` before continuing the rebase.

After any amend/rebase/force-push, re-query the PR head SHA and do not rely on stale `gh pr checks --watch` output from the previous SHA.

## Pitfalls

- Do not blindly copy `lingo-web` GNB/Footer/Button/CookieConsent links; those files are where repo-local `/lingo` and `querypie.ai` policies most often get overwritten.
- Do not treat `querypie.ai` as an external host inside this migrated subtree. The migration result is served under the same site, so same-site links should be root-relative current-tab navigation.
- Do not use `npx prettier --write` as a broad cleanup unless this repo has a matching Prettier config for the target files. It can add semicolon/style churn that obscures the migration diff. Prefer targeted edits or restore source-local style after formatting.
- If `typecheck` reports missing modules that already exist in corp-web-japan `package.json`, check whether the fresh worktree has had dependencies installed before treating it as a code migration error.
- Keep new lingo-specific public assets under `public/lingo/**`; do not create generic `public/images/**` or `public/t/**` assets for this migration.
