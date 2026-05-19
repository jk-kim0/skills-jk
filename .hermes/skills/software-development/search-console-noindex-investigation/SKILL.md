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
- `references/gsc-indexing-api-and-sitemap-refresh.md` — API capability limits, sitemap refresh workflow, issue-level validation restart workflow, and OAuth/browser-session pitfalls.
- `references/gsc-all-site-validation-cli.md` — pattern for a CLI that discovers all managed GSC properties and runs Page indexing issue validation across them safely.
- `references/gsc-frontend-session-cli.md` — pattern for replacing repeated Chrome/CDP control with a one-time cookie/WIZ-token export and direct frontend HTTP calls.
- `references/gsc-validate-cli-regression.md` — regression checklist for exact `validate-index-issues` CLI UX, actionable status filtering, browser-click reliability, and partial-success reporting.

## Goal

Prove the root cause with live evidence, not just Search Console wording. When the task is an indexing-refresh request, first clarify whether the user wants URL-level Request indexing or issue-level validation restart. For this user, do not default to URL-by-URL bulk Request indexing for docs/sites; prefer the Page indexing issue table workflow when they refer to “Why pages aren’t indexed” or validation pages.

## GSC site-by-site indexing status audit workflow

When the user asks for indexing error/status by site/property (without asking to start validation):

1. Enumerate the accessible properties before summarizing.
   - Open the Search Console property selector and capture both URL-prefix and `sc-domain:*` properties.
   - Treat Domain properties as aggregate/overlapping views; prefer URL-prefix properties for actionable site-by-site counts, and label Domain rows as aggregate to avoid double-counting.

2. Visit each property’s Page indexing report directly.
   - Use `https://search.google.com/search-console/index?resource_id=<encoded property>` for each property.
   - Wait for `Why pages aren’t indexed` / `Not indexed` and capture: Last update, Indexed, Not indexed, reason, source, validation, pages.
   - Report reason-level counts instead of exporting or listing huge URL samples unless root-cause verification is requested.

3. Prioritize findings in the summary.
   - Call out high-volume `Not found (404)`, `Page with redirect`, `Crawled - currently not indexed`, `Blocked by robots.txt`, and any `Excluded by ‘noindex’ tag` rows.
   - Distinguish `Started` validations from `Failed`/`Not Started`; do not restart validations unless the user explicitly asks for action.
   - For app/private/support/trust-style properties with tiny counts or intentionally non-public content, note that they may be lower priority rather than treating every exclusion as equally urgent.

## GSC issue-level validation workflow

When the user points to `https://search.google.com/search-console/index?...`, mentions the “Why pages aren’t indexed” table, or asks to update indexing by issue/status:

1. Treat this as issue-level validation, not URL-level bulk submission.
   - Open the exact Page indexing property URL.
   - Read the “Why pages aren’t indexed” table rows: Reason, Source, Validation, Pages.
   - Select candidates by validation state, usually `Failed` first; do not re-trigger `Started` unless explicitly requested.

2. For each candidate issue row, use the row’s `item_key` validation flow.
   - Clicking the row opens `/index/drilldown?...&item_key=<key>`.
   - “SEE DETAILS” or direct navigation opens `/index/validation?...&item_key=<key>`.
   - If `START NEW VALIDATION` is present, click it and verify the issue changes to `Validation started` / table state `Started`.
   - If the start button is absent, report it as non-actionable for the current state rather than falling back to URL-level Request indexing.

3. Browser automation pitfalls.
   - GSC is a SPA; after navigation, wait for the `Validation details` heading and either `START NEW VALIDATION` or a terminal/started validation state, not just any text containing “Validation”.
   - If using Chrome DevTools Protocol, multiple old Search Console tabs can be open. Prefer a fresh tab or activate/bring the selected target to front; otherwise a background/stale tab may show only partial “Examples” content and hide the start button.
   - `wait_for` text can time out even when the page updates; take a fresh snapshot before concluding failure.
   - DOM `button.click()` is not always equivalent to a user click in GSC. Prefer a CDP/Playwright-style mouse click at the `START NEW VALIDATION` button center, then verify the post-click state.

4. CLI regression checks when maintaining automation.
   - Preserve the exact user-facing command name the user tried, such as `validate-index-issues`; do not force them onto only longer internal subcommands.
   - Keep action runs limited to actionable validation states (`Failed`, `Not Started`) unless the user explicitly asks for already-passed or non-actionable rows.
   - Propagate nested per-issue failures to a non-zero process exit. Never summarize a site as OK if one of its issue validations failed.
   - See `references/gsc-validate-cli-regression.md` for a compact regression checklist.

5. Verification.
   - Return to the Page indexing table and confirm every intended issue row is `Started`, `Passed`, or otherwise intentionally skipped.
   - Report issue reasons and page counts, not a huge URL list.
   - If a bulk/all-site run was partial, explicitly separate confirmed `Validation started` rows from CLI/browser failures; do not present a partial run as all-site success.

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

3. For Page indexing issue validation across all managed sites, prefer an all-site wrapper rather than a hard-coded site list.
   - Discover properties with `sites().list()` / the local `gsc sites` implementation.
   - Default to URL-prefix properties; make `sc-domain:*` opt-in with a flag.
   - Keep the wrapper dry-run by default and require `--submit` for actual validation-start actions.
   - Add smoke-test controls such as `--site`, `--limit-sites`, and `--issue-limit` before running the full account.
   - If repeated browser/CDP control makes the CLI impractical, split the implementation into a one-time `frontend-session export` step plus direct frontend HTTP calls that reuse saved cookies/WIZ tokens. Keep the browser helper as an explicit fallback, not the default automation path.
   - See `references/gsc-all-site-validation-cli.md` and `references/gsc-frontend-session-cli.md` for reusable CLI shapes and verification recipes.

4. Preflight OAuth scopes before submitting.
   - `sitemaps.list` can work with `https://www.googleapis.com/auth/webmasters.readonly`.
   - `sitemaps.submit` requires `https://www.googleapis.com/auth/webmasters`.
   - If an existing token was granted readonly only, code changes that request broader scopes will not upgrade it automatically. Back up/remove the token and re-auth, but ask before moving/deleting an existing working token.

5. CLI UX expectations.
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
