# Legal effective-date provenance notes

Session-derived rules for corp-web-japan legal MDX effective dates.

## Source priority
1. Prefer explicit effective-date text in `../corp-web-contents` source MDX body.
2. If the body has no effective-date text, use a clear source metadata/title/version date.
3. If no explicit source date exists, use the date the source file first entered git history.

Useful first-add command:

```bash
git -C ../corp-web-contents log --all --follow --diff-filter=A \
  --date=short --format='%ad %h %s' -- <source-path>
```

## Terms of Service example
- Source inspected: `../corp-web-contents/pages/terms-of-service-en/en/content.mdx`
- No explicit body effective-date line was present.
- First-add fallback identified `2025-06-05` at commit `123398b3`.
- Local body line used: `**Effective from Jun 5, 2025**`.

## Privacy Policy examples
- Versioned source paths under `../corp-web-contents/pages/privacy-policy-en/<version>/en/content.mdx` may already contain effective-date body lines.
- Preserve the source date text while normalizing Markdown shape when requested, e.g. bullet item to EULA-style bold body line.
- Older source versions can have no body effective-date line but still have date in title/meta/path, e.g. `QueryPie Privacy Policy (Nov 29, 2019)` and `19-11-29`.
- In those cases, insert the local body line from the metadata/title/version date, placed after the opening preamble and before the first heading.

## Regression checks
- Assert every local `src/content/privacy-policy/*.mdx` has `^\*\*Effective from .+\*\*$` in the body.
- Assert no local privacy-policy effective date remains as `^- Effective from` or `^* Effective from`.
