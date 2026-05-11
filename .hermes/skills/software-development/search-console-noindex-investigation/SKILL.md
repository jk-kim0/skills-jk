---
name: search-console-noindex-investigation
description: Investigate Google Search Console indexing exclusions such as "Excluded by 'noindex' tag" by verifying the exact drilldown issue, checking live HTML/headers/sitemaps, and mapping the result back to source metadata.
---

# Search Console noindex investigation

Use this when:
- the user shares a Search Console drilldown URL
- Search Console reports `Excluded by 'noindex' tag`
- you need to distinguish a real deployed noindex signal from a misleading dashboard interpretation

## Goal

Prove the root cause with live evidence, not just Search Console wording.

## Workflow

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
