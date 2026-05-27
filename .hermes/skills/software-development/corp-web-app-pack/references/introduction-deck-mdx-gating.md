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