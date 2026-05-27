# Introduction deck MDX gating in corp-web-app

Use this when fixing or extending gated introduction-deck pages under `src/app/(tailwind)/[locale]/t/introduction-deck/[id]/[slug]`.

## Proven pattern

- Introduction deck MDX records can already carry `gated: true`, `downloadCta`, and an explicit `<GatingCut />` marker.
- The route must not render the whole MDX body in one `evaluate()` call with `GatingCut: () => null`; that makes the post-cut content and PDF CTA visible without a form.
- Split the raw MDX body at `<GatingCut />` before rendering:
  - render the preview segment as the normal visible body
  - render the gated segment separately
  - build the TOC from the preview segment only
  - wrap the gated segment and download CTA in `GatingFormWrapper` from `src/components/mdx-layout/article/ui/gating-form-wrapper.component`
- For authoring safety, throw if `gated: true` is set but no `<GatingCut />` exists.

## Useful implementation shape

- Add or reuse a small helper such as `src/lib/repo-content/gating.ts` with:
  - `GATING_CUT_MARKER`
  - `splitMdxSourceAtGatingCut(source)`
  - `assertGatedMdxHasGatingCut({ gated, source, sourcePath })`
- Keep the fix scoped to the preview `/t/introduction-deck` route unless the task explicitly asks for public route release.
- Prefer reusing the existing legacy `GatingFormWrapper`/`Form` submit path for this repo rather than porting the full corp-web-japan cookie/API gating architecture unless cookie persistence is explicitly required.

## Regression checks

Add or update `src/lib/repo-content/__tests__/introduction-deck-migration.test.ts` to assert:

- a target gated intro deck body splits into preview and gated segments
- the preview segment excludes the post-cut download copy
- the detail page imports/renders `GatingFormWrapper`
- the route renders `previewSource` and `gatedSource` separately

## Stage Playwright E2E pattern

When the task asks for an E2E check against the deployed/stage introduction-deck gating form:

- Put the spec under `tests/e2e/` in the nested tests workspace, not under `src/__tests__`.
- Add a `tests/package.json` script such as `test:e2e:introduction-deck-gating-form:stage` that sets `BASE_URL=https://stage.querypie.com` and runs the narrow spec with `--retries=0`.
- Add a manual `workflow_dispatch` workflow under `.github/workflows/` with `defaults.run.working-directory: tests`, `actions/setup-node` cache path `tests/package-lock.json`, `npm ci`, Playwright browser install, and artifact upload for `tests/playwright-report/` plus `tests/test-results/`.
- Keep the default E2E mode non-mutating: verify the form renders, required fields enable submit, and post-cut body/download CTA are hidden before unlock. Make the real hosted submit action opt-in via an input/env such as `INTRODUCTION_DECK_GATING_FORM_SUBMIT_MODE=submit` so routine workflow runs do not create leads.
- To verify the unlocked state without submitting the hosted form, set the repo’s `force_hide_gating_form=1` cookie for the stage origin in the Playwright context, then assert `data-introduction-deck-gated-body` and the PDF CTA become visible while `data-introduction-deck-gating-form` is absent.
- Include the same Vercel Security Checkpoint diagnostic pattern used by other stage E2E specs: if the response is 403, the title is `Vercel Security Checkpoint`, or the checkpoint text is visible, fail with an edge/WAF/bot-protection message rather than a selector failure.
- Verification before PR: `actionlint <workflow>`, `git diff --check`, `npx playwright test --config=e2e/playwright.config.ts <spec> --list`, and if browsers are installed (or after `npm run install:browsers`) run the narrow stage spec. A normal default result is `2 passed, 1 skipped` when the explicit submit-mode test is skipped.

## Fresh worktree verification note

A fresh linked worktree may not have `node_modules`. If the root checkout already has compatible dependencies and the user wants fast repo work, a temporary symlink can run targeted checks without `npm install`:

```bash
ln -s /path/to/root/node_modules node_modules
npm run test -- src/lib/repo-content/__tests__/introduction-deck-migration.test.ts
status=$?
rm node_modules
exit $status
```

Use this only as a local verification shortcut; do not commit the symlink.