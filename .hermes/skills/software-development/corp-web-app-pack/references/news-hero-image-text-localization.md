# News hero image text localization

Use this when a localized news MDX record already points to `public/news/<id>/hero-<locale>.png`, but the localized hero assets are still duplicates of the Korean/source image or need translated text over the same visual design.

## Workflow

1. Locate the source and target hero assets from the MDX frontmatter (`heroImageSrc`) or `public/news/<id>/`.
2. Verify the target files are either duplicates or intentionally replaceable before overwriting them. Compare dimensions and hashes/pixel diffs; do not modify the source locale image unless requested.
3. Determine the original text region from the source image rather than guessing:
   - Use image dimensions and a rough dark/edge-pixel scan to find headline/subline bounding boxes.
   - If existing localized assets differ only by metadata, treat them as placeholders and generate the real localized variants from the source image.
4. Remove only the original text area. Preserve the surrounding graphic, gradient, and decorative elements.
   - Use a slightly larger erase rectangle around the text glyphs to cover antialiasing.
   - Reconstruct the light background from nearby edge colors/gradients instead of painting an arbitrary flat rectangle when the original has subtle gradients.
5. Draw localized text with centered alignment matching the original visual hierarchy:
   - Keep the first line as the larger headline and the second line as the smaller support line.
   - Fit font size to the available width for longer English copy.
   - Use a font that supports the locale (e.g. system Japanese/Korean fonts for CJK, Helvetica/Inter-like fonts for English) and keep the original dark text tone.
6. Save to the locale-specific filenames already referenced by MDX, usually `hero-en.png` and `hero-ja.png`.
7. Verify:
   - Dimensions and image mode remain compatible with the original, e.g. `1280x720` RGBA/PNG when that was the source format.
   - `git status` shows only the intended localized image files changed.
   - The source hero image remains unchanged.
   - A pixel diff or visual inspection confirms the changed region is limited to the text area.

## Pitfalls

- Do not assume `hero-en.png` / `hero-ja.png` already contain localized text just because the files exist. They may be byte-different only due to metadata while pixel-identical to the Korean source.
- Before editing, verify the intended news/article ID from the user's wording, the source image path, and MDX frontmatter. If the requested translated copy is for a different article than the currently found `hero-ko.png`, use the article that owns the copy, not the first matching hero image. Example: NotePie copy belongs to news 27, not an earlier Lingo news 26 image.
- If localized target files do not exist and EN/JA MDX still point to `hero-ko.png`, create `hero-en.png` / `hero-ja.png` from the Korean source and update only the EN/JA `heroImageSrc` frontmatter to the locale-specific image paths; keep KO pointed at `hero-ko.png`.
- Do not place customer-facing copy such as translations into MDX or filenames if the task is specifically to edit the raster hero image.
- Avoid large visual redesigns. For press-release hero images, preserve the established composition and make only the text-localization change.
- Avoid committing a change to `hero-ko.png` when the user asked to base new localized versions on it.
- If a PR was opened against the wrong news ID, correct the existing PR rather than creating confusion: verify the live PR file list, restore the wrong article files from `origin/main`, apply the change to the correct article ID, update the PR title/body, amend the commit, and force-push with lease.
