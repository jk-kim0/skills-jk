---
name: corp-web-japan-image-asset-webp-replacement
description: Replace a corp-web-japan PNG asset with a same-directory WebP while preserving resolution, updating refs, and removing obsolete alternate optimized assets when appropriate.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, image, webp, assets, optimization, pr-followup]
---

# corp-web-japan image asset -> WebP replacement

Use this when the user asks to convert an existing PNG/JPG asset to `.webp`, keep the same resolution, place it in the same directory, and update code references.

## When to use
- "`public/.../foo.png`를 해상도 유지한 채 webp로 바꿔줘"
- PR follow-up where an older `public/optimized/*.jpg` should be replaced by a route-local or component-local `.webp`
- Marketing/diagram assets in `corp-web-japan`

## Core rules
- Keep the output next to the source file unless the user explicitly wants another asset root.
- Preserve pixel dimensions.
- Prefer updating existing callers to the new same-directory `.webp` instead of keeping a separate `/optimized/...jpg` unless that split is still necessary.
- If the old optimized asset becomes unused, delete it in the same change.

## Recommended workflow

1. Identify current references first.
```bash
git grep -n 'value-diagram\.png\|value-diagram\.webp\|optimized/.*jpg' -- src public
```

2. Inspect the source asset.
```bash
file public/path/to/asset.png
ls -lh public/path/to/asset.png
```

3. Convert to WebP at the same resolution.
- For diagram/text-heavy assets, try lossless first.
```bash
cwebp -lossless public/path/to/asset.png -o public/path/to/asset.webp
```
- If lossless remains too large for practical web use, prefer a high-quality lossy WebP while keeping dimensions unchanged.
- In practice, `cwebp -q 95` was a good default for a large AI Dashi diagram asset: it preserved `2469x2160` while shrinking a 5.1 MB PNG to about 390 KB.
```bash
cwebp -q 95 public/path/to/asset.png -o public/path/to/asset.webp
```
- If the user requests a target byte range for the new WebP (for example a hero asset around `100KB~200KB`), do not guess one quality value and stop. Sweep several `cwebp` quality values and choose the highest quality that still lands inside the requested size window.
- Practical example from `public/top-hero.png` in `corp-web-japan`:
  - source PNG resolution `2814x1536`
  - `q=75` -> about `146KB`
  - `q=80` -> about `175KB`
  - `q=85` -> about `215KB` (too large for a `100KB~200KB` target)
  - so `q=80` was the best fit because it preserved the full `2814x1536` resolution and stayed within the requested size band.
```bash
for q in 50 55 60 65 70 75 80 85 90; do
  out="/tmp/asset-q${q}.webp"
  cwebp -q "$q" -m 6 -sharp_yuv public/path/to/asset.png -o "$out"
  stat -f '%z %N' "$out"
done
# then copy the highest-quality candidate that falls inside the requested byte range
```
- After choosing the candidate, verify both:
  1. the final WebP dimensions still match the source PNG exactly
  2. the final byte size is inside the requested target window

4. Verify dimensions after conversion.
```bash
file public/path/to/asset.webp
ls -lh public/path/to/asset.png public/path/to/asset.webp
```
If needed, parse headers or use another tool to confirm the width/height exactly match.

5. Update references.
- Prefer both thumbnail/display `src` and modal/high-resolution `modalSrc` to use the new `.webp` if the user asked to reference the new file directly and the preserved-resolution WebP is suitable for both uses.
- If the previous implementation used `src=/optimized/...jpg` and `modalSrc=/original.png`, switch both to the same-directory `.webp` when that makes the old optimized asset unnecessary.

6. Remove obsolete assets.
- If `git grep` shows the old `optimized/*.jpg` is no longer referenced, delete it in the same commit.

7. Verify final refs.
```bash
git grep -n 'asset\.webp\|old-optimized-name\.jpg\|asset\.png' -- src public
```
Make sure only the intended new refs remain.

## PR follow-up note
If this is on an existing open PR branch, use a fresh worktree from the PR branch tip and push back to the same branch.

## Practical heuristics
- For photos/heroes, compare against any already-existing `.webp` before assuming a new `.jpg` or `.webp` is valuable.
- For diagrams with text/lines, a same-resolution high-quality WebP is often a better final asset than a separate `optimized/*.jpg` derivative.
- Keep the diff minimal: add the new `.webp`, update refs, remove now-unused alternate assets, and stop.

## Done criteria
- New `.webp` exists in the same directory as requested.
- Width/height match the source asset.
- Callers reference the new `.webp`.
- Any now-unused alternate optimized asset is removed.
- The existing PR branch or current work branch is updated and pushed.
