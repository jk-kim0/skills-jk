# Confluence Space MDX Sync PR Notes

Use this reference when a querypie-docs task is a Confluence Space synchronization update that changes Korean MDX source content and needs a PR.

## PR framing

- Title should start with `mdx:`.
- Describe the content synchronization, not just the mechanical file rename.
- Body should be content-change focused: what Confluence content changed, which docs were synchronized, and which locales were updated.
- Keep PR text in Korean for this repo.

## Localized content parity checklist

When a Korean source MDX file is renamed or its release-note range changes:

1. Apply the same filename change under `src/content/en/...` and `src/content/ja/...`.
2. Update `_meta.ts` in all affected locales.
3. Update product/version or cross-document links in all affected locales.
4. Translate newly added Korean content into English and Japanese without changing markdown structure.
5. Search all locale trees for stale slugs/titles and placeholders, for example:
   - old release-note slug such as `11.5.0-11.5.5`
   - old display title such as `11.5.0 ~ 11.5.5`
   - temporary placeholders such as `#link-error`
6. If a skeleton comparison reports a structure mismatch due to Korean source punctuation/spacing (for example `[공통]External` without a space), fix the Korean source formatting when it is clearly an original formatting typo, then re-run localized skeleton checks.

## Verification pattern

From `confluence-mdx`, use `target/{lang}/...` paths, not `../src/content/{lang}/...`, for skeleton checks:

```bash
python3 bin/skeleton/cli.py --use-ignore target/en/path/to/file.mdx
python3 bin/skeleton/cli.py --use-ignore target/ja/path/to/file.mdx
python3 bin/skeleton/cli.py --reset target/ko target/en target/ja
```

Also run:

```bash
git diff --cached --check
```

For repo-work speed preferences, do not spend time on local build/test unless explicitly requested; rely on PR CI after push.
