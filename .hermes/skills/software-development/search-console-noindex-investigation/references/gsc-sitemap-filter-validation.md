# GSC Page indexing sitemap-filtered validation

Context: the Search Console Page indexing screen has a filter dropdown with `All known pages`, `All submitted pages`, `Unsubmitted pages only`, and a `Filter to Sitemaps` section listing sitemap files such as `/sitemap.xml`.

## Key learning

The `Filter to Sitemaps` options are present in the Page indexing HTML as sitemap absolute URLs, for example:

```html
<div data-value="https://querypie.ai/sitemap.xml"
     data-url="https://querypie.ai/sitemap.xml"
     data-event-label="SITEMAP">
  <span>/sitemap.xml</span>
</div>
```

The filtered Page indexing report can be fetched directly by adding a `sitemap` query parameter with the absolute sitemap URL:

```text
https://search.google.com/search-console/index?resource_id=<site-url>&sitemap=<absolute-sitemap-url>
```

Example:

```text
/search-console/index?resource_id=https%3A%2F%2Fquerypie.ai%2F&sitemap=https%3A%2F%2Fquerypie.ai%2Fsitemap.xml
```

## Implementation pattern

For repo-local `bin/gsc`-style helpers:

1. Add CLI flags:
   - `--sitemap URL_OR_PATH` for one sitemap (`/sitemap.xml` should normalize against the site URL).
   - `--all-sitemaps` to first fetch the unfiltered Page indexing report, extract every `data-event-label="SITEMAP"` option, then process each sitemap separately.
2. Build the index URL with `URLSearchParams`, not string concatenation.
3. Reuse the same `Why pages aren’t indexed` row parser and validation-submit flow after fetching the filtered page.
4. Include `sitemap=<absolute-url>` in human-readable and JSON output so reviewers can tell whether rows came from the full report or a sitemap-filtered report.
5. Keep `--submit` semantics unchanged: dry-run by default; only send validation requests for filtered rows when explicitly submitted.

## Important interpretation

A sitemap-filtered report can legitimately return zero issue rows:

```text
GSC Page indexing issue report | mode=frontend-session | site=https://querypie.ai/ | sitemap=https://querypie.ai/sitemap.xml | submit=false
discovered=0 candidates=0
summary: total=0 started=0 skipped=0 failed=0
```

Treat this as “the selected sitemap scope has no `Why pages aren’t indexed` rows,” not as a parser failure or skipped validation. The full Page indexing report may still contain issue rows outside that sitemap scope.

## Verification checklist

- Syntax checks:
  - `python3 -m py_compile bin/gsc`
  - `node --check bin/gsc-frontend-indexing`
  - `node --check bin/gsc-browser-indexing`
- Unit tests for wrapper argument forwarding and table/JSON output markers.
- Dry-run one sitemap:
  - `./bin/gsc-frontend-indexing --site https://querypie.ai/ --index-issues --sitemap /sitemap.xml --delay-ms 0`
- Dry-run all sitemaps:
  - `./bin/gsc-frontend-indexing --site https://querypie.ai/ --index-issues --all-sitemaps --delay-ms 0`
- Wrapper smoke:
  - `./bin/gsc validate-index-issues-all --site https://querypie.ai/ --sitemap /sitemap.xml --delay-ms 0 --site-delay-ms 0`

## Pitfalls

- Do not infer the query parameter name from the UI label. Confirm from the loaded GSC HTML/session; in the observed case, `sitemap=<absolute-url>` worked.
- Do not pass only the displayed path label when fetching GSC directly; normalize `/sitemap.xml` to the absolute sitemap URL first.
- `&sitemap=...` can reduce table rows to zero. That can be correct for the filtered scope, so verify the page still contains `Page indexing` / `Why pages aren’t indexed` before calling it a login/session failure.
- For `--all-sitemaps`, the first unfiltered fetch should be used to discover sitemap options; avoid hard-coding site-specific sitemap lists.
