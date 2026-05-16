---
name: search-console-noindex-investigation
description: Investigate Google Search Console indexing exclusions and indexing-refresh workflows by verifying the exact GSC issue/API capability, checking live HTML/headers/sitemaps, mapping results back to source metadata, and using sitemap refresh rather than unsupported bulk Request Indexing APIs.
---

# Search Console noindex investigation

Use this when:
- the user shares a Search Console drilldown URL
- Search Console reports `Excluded by 'noindex' tag`
- the user asks whether Search Console indexing requests can be updated through API/CLI
- the user asks to refresh indexing for managed websites or documents
- you need to distinguish a real deployed noindex signal from a misleading dashboard interpretation

References:
- `references/gsc-indexing-api-and-sitemap-refresh.md` — API capability limits, sitemap refresh workflow, and OAuth scope pitfalls.

## Goal

Prove the root cause with live evidence, not just Search Console wording. When the task is an indexing-refresh request, first prove what Google exposes through public APIs, then use the safest supported automation path.

## GSC API / CLI indexing-refresh workflow

When the user asks to “request indexing”, “update indexing requests”, or bulk-refresh managed website documents:

1. Verify API capability before promising the action.
   - General Search Console UI `Request indexing` for ordinary URLs is not exposed as a public bulk API.
   - URL Inspection API is inspect/read-only for status, not a submit endpoint.
   - Indexing API is limited/recommended for special short-lived content types such as `JobPosting` and `BroadcastEvent` in `VideoObject`; do not use it as a generic docs/marketing recrawl mechanism.

2. Use sitemap refresh as the supported automation path for ordinary pages.
   - List managed Search Console properties.
   - List registered sitemaps for URL-prefix properties.
   - Re-submit registered sitemaps with `sitemaps.submit`.
   - Treat `sc-domain:*` properties as potentially overlapping with URL-prefix properties; skip by default unless the user explicitly wants domain properties included.

3. Preflight OAuth scopes before submitting.
   - `sitemaps.list` can work with `https://www.googleapis.com/auth/webmasters.readonly`.
   - `sitemaps.submit` requires `https://www.googleapis.com/auth/webmasters`.
   - If an existing token was granted readonly only, code changes that request broader scopes will not upgrade it automatically. Back up/remove the token and re-auth, but ask before moving/deleting an existing working token.

4. CLI UX expectations.
   - Provide an explicit explanation command or message for unsupported general Request Indexing API.
   - Add/write commands such as `submit-sitemap` and `refresh-sitemaps` when maintaining a repo-local GSC CLI.
   - Fail fast with a clear scope error rather than attempting many sitemap submissions that all return 403.

See `references/gsc-indexing-api-and-sitemap-refresh.md` for condensed session notes and exact pitfalls.

## Noindex investigation workflow

1. Open the exact Search Console drilldown URL in a new browser tab.
   - Do not rely on an already-open Search Console tab; it may be showing a different issue/property state.
   - First verify the issue heading exactly (`Excluded by 'noindex' tag`, `Crawled - currently not indexed`, etc.).

2. Capture the affected URL examples.
   - Extract example URLs from the affected-pages table.
   - If browser text extraction adds UI glyphs or stray characters, sanitize the URLs before testing them.

3. Check the live site directly for several examples, then verify whether the pattern holds for all examples.
   For each URL, inspect:
   - HTTP status
   - `X-Robots-Tag` response header
   - HTML `<meta name="robots">`
   - canonical URL
   - presence in `sitemap.xml`

4. Check `robots.txt` separately.
   - `robots.txt` may allow crawling while the page still sends `noindex`.
   - If `robots.txt` is permissive, do not misattribute the exclusion to robots.txt.

5. Map the live finding back to source code.
   - In Next.js/App Router projects, inspect route `generateMetadata` / `metadata.robots` and sitemap generation code together.
   - Common bad pattern:
     - detail page emits `robots: { index: false, follow: false }`
     - sitemap still includes the same detail URLs

6. Report the outcome as one of two cases:
   - Intended noindex:
     - Search Console exclusion is expected
     - sitemap should usually stop listing those URLs
   - Unintended noindex:
     - metadata/header must be changed to allow indexing
     - then Search Console validation can be retried

## Strong evidence pattern

If all of the following are true:
- Search Console says `Excluded by 'noindex' tag`
- live HTML contains `<meta name="robots" content="noindex, nofollow">` (or equivalent header)
- the same URL appears in `sitemap.xml`
- canonical points to the same URL

then the issue is almost certainly a real deployed metadata/config problem, not a Search Console false positive.

## Practical notes

- Search Console drilldown pages can be inspected effectively with browser automation plus page snapshots.
- For bulk verification, use a small script to test all example URLs and summarize the robots pattern.
- When reporting, separate `robots.txt` findings from page-level noindex findings so the user sees which layer actually caused the exclusion.
