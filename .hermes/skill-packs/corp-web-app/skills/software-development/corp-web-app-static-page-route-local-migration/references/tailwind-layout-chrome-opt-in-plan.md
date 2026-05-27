# Tailwind layout chrome opt-in planning

Use this reference when the user asks to introduce Tailwind-based layout, header, GNB, or footer in corp-web-app while keeping the existing chrome available.

Session pattern:

- Existing plan doc: `docs/plans/2026-05-19-tailwind-adoption-and-blog-detail-migration.md`.
- Add Tailwind layout chrome as a separate axis from Tailwind page/content migration.
- Do not rewrite or delete existing layout/header/GNB/footer in the planning PR.
- Plan a new parallel component family under `src/components/layout/**`, e.g.:
  - `tailwind-site-layout.tsx`
  - `tailwind-site-header.tsx`
  - `tailwind-site-gnb.tsx`
  - `tailwind-site-mobile-menu.tsx`
  - `tailwind-site-footer.tsx`
  - `tailwind-site-locale-switcher.tsx`
  - `tailwind-site-chrome.types.ts`
- Root layout replacement should be a late, separate all-page visual-risk PR after endpoint-level proof.
- First implementation PR should be a foundation-only PR for the Tailwind chrome components and focused tests/internal smoke surface.
- First adoption PR should opt in one route/endpoint explicitly with a wrapper such as `TailwindSiteLayout`, preferably a `/[locale]/t/*` verification route that already uses Tailwind page shell.
- Keep public navigation targets, middleware, sitemap, canonical, redirects, and CMS-managed data out of the Tailwind chrome PRs unless explicitly requested.

Useful PR-plan sections to include:

1. Why the new chrome is parallel instead of an immediate replacement.
2. Component boundary/responsibility list for layout/header/GNB/mobile-menu/footer.
3. Endpoint opt-in pattern using a route wrapper or URL-neutral route group.
4. Forbidden scope for the foundation PR and endpoint opt-in PR.
5. Verification criteria for desktop header, mobile menu, dropdown/mega menu, footer links, sticky header overlap, computed reset/preflight effects, and mobile horizontal overflow.
6. Rollback strategy: revert the endpoint wrapper to existing chrome; avoid whole-site rollback until root layout is intentionally switched.

Verification for a docs-only planning PR:

- Use a fresh worktree from latest `origin/main`.
- Patch the plan doc only.
- Run `git diff --check`.
- Commit, push, and open the PR; report attached CI without waiting passively.
