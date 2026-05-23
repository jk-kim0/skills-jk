# GSC Page indexing: `--all-sitemaps` vs unfiltered issue table

## Lesson

When a user says the GSC web console shows validation failures but the CLI reports `discovered=0 candidates=0`, first verify whether the CLI was run with a sitemap filter mode such as `--all-sitemaps`.

`--all-sitemaps` is not the same as “all Page indexing issues.” It means:

1. open the Page indexing report,
2. discover entries under **Filter to Sitemaps**,
3. re-run the Page indexing report once per sitemap URL with `sitemap=<absolute-sitemap-url>`.

A row visible in the unfiltered “Why pages aren't indexed” table may legitimately disappear under every sitemap filter. In that case the CLI did not miss the row; it inspected a narrower filtered screen than the screenshot/web console view.

## Diagnostic pattern

Run both scopes and compare:

```bash
# Unfiltered Page indexing issue table — matches the default web console table.
./bin/gsc validate-index-issues-all --site https://example.com/ --output-json

# Sitemap-filtered issue tables — only rows associated with each selected sitemap.
./bin/gsc validate-index-issues-all --site https://example.com/ --all-sitemaps --output-json
```

If the user provided a screenshot, check the top UI for active filter chips. A plain Page indexing table with only the filter icon visible and no sitemap chip should be treated as unfiltered.

## Example observed in skills-jk

For `https://docs.querypie.com/`:

- Unfiltered table showed 9 rows and 4 actionable `Failed` candidates:
  - `Blocked by robots.txt` / `Failed` / 210 pages
  - `Not found (404)` / `Failed` / 200 pages
  - `Page with redirect` / `Failed` / 180 pages
  - `Crawled - currently not indexed` / `Failed` / 624 pages
- `--all-sitemaps` checked sitemap-filtered pages and returned zero rows for `/en/sitemap.xml`, `/ja/sitemap.xml`, and `/ko/sitemap.xml`.

Correct user guidance for that case:

```bash
# To act on the 4 Failed rows visible in the screenshot/default table:
./bin/gsc validate-index-issues-all --site https://docs.querypie.com/ --submit

# Do not include --all-sitemaps unless the user explicitly wants only sitemap-filtered rows.
```

## Additional frontend-session pitfall

The direct `frontend-session` helper may parse sitemap options from static HTML with regex. GSC renders some controls dynamically, so frontend-session mode can under-detect sitemap options. In the observed case, API/browser evidence showed three registered sitemap options (`/en`, `/ja`, `/ko`), while frontend-session detected only `/en`.

When sitemap option completeness matters, cross-check with:

```bash
./bin/gsc sitemaps https://example.com/
./bin/gsc validate-index-issues-all-browser --site https://example.com/ --all-sitemaps --output-json
```

Interpretation:

- unfiltered rows present + filtered rows absent = scope mismatch, not row-parser failure.
- browser mode sees more sitemap options than frontend-session = frontend-session sitemap option parser limitation.
