# corp-web-japan OpenSpec platform feature documentation

Use this reference when documenting an already-implemented platform/reviewer/test capability in `corp-web-japan` as OpenSpec, especially when the repository does not yet have an `openspec/` tree.

## Pattern

1. Start from a latest-main worktree.
   - Fetch/prune first.
   - Create a repo-local `.worktrees/<topic>` branch from `origin/main`.
   - Do not edit the root checkout when it is behind or serving as the main workspace.
2. Inspect the implementation or source spec before writing the corp-web-japan spec.
   - For already-implemented corp-web-japan features, search for the feature name and adjacent implementation concepts.
   - Read source helpers, UI components, API routes, server components, and source-level tests.
   - Treat tests as implementation evidence, not as the only source of truth.
   - For migrations from another QueryPie repo, read the source OpenSpec directly from the source PR branch/worktree when available, then adapt it to corp-web-japan architecture instead of copying repo-specific wording verbatim.
3. Check whether `openspec/` already exists on latest `origin/main` before creating files.
   - If absent, add the minimal standard tree instead of inventing a large process layer:
     - `openspec/README.md`
     - `openspec/project.md`
     - `openspec/specs/README.md`
     - `openspec/specs/<platform-feature>/spec.md`
   - If present, reuse the existing tree and update only the relevant spec, `openspec/specs/README.md`, and any small cross-cutting `openspec/project.md` context needed.
4. Keep repository-internal OpenSpec docs in English for collaborator readability.
5. Write a `platform-*` spec for cross-cutting reviewer/test/runtime UI capabilities.
   - Include `Purpose`, implementation status, source/current implementation references as appropriate, and `Requirements`.
   - If the feature is not implemented in corp-web-japan yet, state that explicitly and write the document as the target implementation contract.
   - Use `SHALL`, `SHALL NOT`, `MAY`, and `SHOULD` for normative text.
   - Convert implementation behavior into `GIVEN` / `WHEN` / `THEN` scenarios.
6. Cover all surfaces that consume the same state.
   - For Preview Toggle this meant: production visibility, cookie/API state, header control UX, path helper behavior, footer/internal links, category sidebars, and gated-content preview unlock.
   - For Component Name Debug this means: build-time availability, `data-component-name` marker authoring, mode control, `Alt+Shift+N` cycle, shortcut suppression in editable controls, overlay collection, bottom-left/top-right label placement, Clipboard copy, and implementation verification expectations.
7. Verify with the lightest command that proves the docs are clean.
   - For docs-only OpenSpec additions, `git diff --check` plus a small phrase/conflict-marker check is sufficient unless the user asks for broader verification.
8. Commit, push, and open/update the PR automatically.
   - PR body should say it is documentation-only and list the implementation surfaces or source spec inspected.

## Preview Toggle evidence map

When documenting `platform-preview-toggle`, inspect these implementation anchors:

- `src/lib/preview-navigation.ts`
- `src/lib/is-production.ts`
- `src/app/api/preview-navigation/route.ts`
- `src/components/layout/preview-mode-toggle.tsx`
- `src/components/layout/site-header.tsx`
- `src/components/layout/site-header-client.tsx`
- `src/components/layout/site-footer.tsx`
- `src/components/sections/resource-category-sidebar.tsx`
- `src/components/sections/demo-category-sidebar.tsx`
- `src/app/api/gating-form/preview-unlock/route.ts`
- gated publication detail/PDF/internal pages that read `PREVIEW_NAVIGATION_COOKIE`
- source tests such as `tests/preview-navigation-path-helper.test.mjs`, `tests/footer-preview-navigation.test.mjs`, `tests/whitepaper-gating-source.test.mjs`, and `tests/src/app/api/gating-form/preview-unlock/route.test.mjs`

## Pitfalls

- Do not document a feature from its UI label alone. `Preview Toggle` was implemented through helpers, cookies, API routes, header UI, footer/internal links, sidebars, and gating bypasses.
- Do not assume `openspec/` already exists in corp-web-japan; create the minimal structure when absent.
- Do not run a local dev server or broad build for docs-only OpenSpec work unless specifically requested.
- Do not make customer-facing claims about internal terms such as MDX; keep them as implementation references only inside repository-internal docs.
