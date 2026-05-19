---
name: preview-route-public-rollout
description: Publish a reviewed preview route (especially /<locale>/t/* in Next.js App Router sites) to its public route without duplicating route entries or preserving preview canonicals.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, app-router, preview-route, public-rollout, route-local-authoring, canonical]
---

# Preview Route Public Rollout

Use this skill when the user asks to publish, promote, roll out, or make public a page that has already been reviewed under a preview/review route such as `/<locale>/t/*`.

This is a class-level workflow skill. It is not limited to one repository, but it is especially important for repos that use route-local i18n pages with `page.tsx`, `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx`.

## Core rule

Public rollout means moving the reviewed implementation to the public route, not adding a second wrapper route beside the preview route.

Do not satisfy a rollout request by creating a new public `page.tsx` that imports from the old preview route while leaving the preview route intact. That creates duplicate route entries for the same reviewed page and can leave wrong preview canonical metadata in place.

## Trigger phrases

Load this skill when the task includes language like:

- "publish rollout"
- "promote the preview route"
- "make `/ko/t/...` public"
- "roll out `/<locale>/t/*`"
- "UI parity 검증 완료했으니 public route로 전환"
- "preview route를 public route로 이동"

Also load it when reviewing a PR that claims to publish a preview route.

## Workflow

1. Identify the preview source route and public target route.
   - Example: `src/app/[locale]/t/page.tsx` -> `src/app/[locale]/page.tsx`.
   - Example: `src/app/[locale]/t/company/news/page.tsx` -> `src/app/[locale]/company/news/page.tsx`.

2. Move route-local files with `git mv` whenever possible.
   - Move `page.tsx`, locale modules (`page.en.tsx`, `page.ko.tsx`, `page.ja.tsx`), route-local README/provenance notes, CSS modules, and route-only helper components together when they belong only to the page being promoted.
   - Do not leave the old preview `page.tsx` behind unless the user explicitly requests a temporary compatibility route.

3. Update imports after the move.
   - The public `page.tsx` should import colocated locale modules from the new public route directory.
   - Avoid imports from `src/app/[locale]/t/**` in the public route after rollout unless a deliberate compatibility plan is documented.

4. Update metadata and canonical URLs.
   - Preview canonical paths such as `/ko/t` must become public canonicals such as `/ko`.
   - Tests should assert the public canonical, not the old preview canonical.

5. Remove preview-only route registry/index entries.
   - Internal preview indexes, route risk dashboards, preview navigation, or source/backing-file tests should no longer list a preview route whose page file was promoted.

6. Audit middleware and redirect/rewrite rules for the promoted route.
   - Preview-route rollouts can leave hidden routing behavior outside `src/app/**`, especially default-locale rewrites for `/t` or production redirects for locale roots.
   - When promoting the locale home preview `/{locale}/t` to `/{locale}`, exact `/t` should not rewrite to a removed preview page. Redirect or rewrite it to the public locale home according to the repo's locale policy.
   - Do not accidentally break other preview subroutes such as `/t/blog`: if only the exact home preview is removed, narrow middleware matches from `/t` to `/t/` (or equivalent) so subroutes keep their intended behavior.
   - Preserve existing production redirects unless the user explicitly includes them in the rollout scope. Do not assume a locale-root redirect such as production `/ja -> external site` should be removed just because a local public route now exists; keep or change it only when the requested rollout contract requires that route to become directly reachable.
   - Keep slash-sensitive route predicates simple. If only exact `/t` is special and `/t/*` should keep default-locale rewrite behavior, prefer a direct condition such as `pathname.startsWith('/t/')` rather than introducing a separate one-off prefix collection solely for `/t/`.

7. Move or rewrite tests so they mirror the public route path.
   - Example: `src/__tests__/app/[locale]/t/page.test.tsx` -> `src/__tests__/app/[locale]/page.test.tsx`.
   - Add a narrow absence assertion for the old preview route file when removal is intentional.
   - Update CI test-group mappings if the repo partitions tests by path.

8. Update route-local README/provenance notes.
   - Remove text saying the public route is intentionally unchanged.
   - State that the preview route entrypoint was removed as part of rollout.

9. Grep for stale preview-route contracts before committing.
   - Old source paths such as `src/app/[locale]/t/page.tsx`.
   - Stale canonical assertions such as `canonical: '/ko/t'`.
   - Preview route labels such as `Home preview` when the promoted page was the home page.
   - Middleware branches or tests that still route exact `/t` to the removed preview entrypoint.
   - Production-only external redirects that still intercept the newly public locale route.

10. Update PR body to describe final state only.
   - Do not say the preview route remains canonical unless the user explicitly requested that compatibility exception.
   - Mention if UI parity was already completed by the user, but do not use that as justification to keep the preview route.

## When the public target already exists

Some rollouts start with both a reviewed `/<locale>/t/*` preview route and an older public target route already present. In that case, do not keep or wrap the older public implementation. Treat the reviewed preview route as the source of truth: remove or overwrite the existing public route files, move the preview route-local files into the public target with `git mv` where possible, and then remove the old preview entrypoint. After the move, inspect the diff against `HEAD` (not only `git diff` unstaged output) because replacing an existing target directory can appear as staged modifications plus deletions.

Test updates for this shape:

- Prefer one public-route test file mirroring the final route path.
- Delete or replace the old preview-route test instead of keeping parallel preview and public tests for the same page.
- Add an absence assertion for the removed preview page file.
- Update preview navigation and internal preview-index tests so they no longer map the promoted public path back to `/<locale>/t/*`.

## Compatibility exception

Only keep the old preview route when the user explicitly asks for a temporary compatibility route after rollout.

If that exception is requested:

- Document the reason in the PR body.
- Keep the public route canonical.
- Make the preview route non-canonical or redirecting if appropriate for the repo.
- Add tests that prevent the preview route from being treated as the canonical public route.

Do not infer this exception from generic words like "publish", "rollout", or "promote".

## Verification checklist

Run the lightest checks that prove the route contract:

- Targeted route tests for the public route and any internal preview index affected.
- Test-group assertion script if the repo has one.
- `git diff --check`.
- A grep for stale preview paths/canonicals.
- PR file list verification to ensure files were moved/deleted rather than duplicated.

## Pitfall from prior correction

A previous rollout mistake was to add `src/app/[locale]/page.tsx` while leaving `src/app/[locale]/t/page.tsx` and preserving `/ko/t` canonical tests. The user correctly flagged this as a guideline violation. For rollout tasks, move the existing preview page files and remove the promoted preview entrypoint instead.

## References

- `references/corp-web-app-home-rollout-correction.md` records the concrete correction pattern from the corp-web-app home page rollout.
- `references/corp-web-app-certifications-rollout.md` records the target-already-exists rollout pattern from promoting certifications: replace the older public route with the reviewed preview implementation, remove preview navigation/index entries, collapse tests to the public route, and inspect `git diff HEAD` before commit.