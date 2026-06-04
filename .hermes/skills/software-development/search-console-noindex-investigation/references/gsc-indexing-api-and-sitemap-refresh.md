# GSC indexing API limits, sitemap refresh, and issue validation automation

Session-derived notes for Google Search Console indexing work.

## Key API facts

- There is no public Google Search Console API/CLI endpoint that performs the UI action `Request indexing` for ordinary web pages in bulk.
- URL Inspection API (`urlInspection.index.inspect`) is for status inspection only.
- Search Console API supports sitemap operations such as `sitemaps.list` and `sitemaps.submit`.
- Google Indexing API `URL_UPDATED` is officially limited/recommended for pages with `JobPosting` or `BroadcastEvent` embedded in `VideoObject`; do not use it as a general website recrawl API for marketing/docs pages.

## Safe automation path: sitemap refresh

For ordinary docs/marketing/public website pages, the safe public-API substitute for “update indexing requests” is:

1. List owned Search Console properties.
2. For URL-prefix properties, list registered sitemaps.
3. Re-submit each registered sitemap with `sitemaps.submit`.
4. Treat domain properties (`sc-domain:*`) carefully because they can overlap URL-prefix properties and may duplicate work.

## User-preferred workflow: issue-level validation restart

If the user refers to the Search Console Page indexing screen, “Why pages aren’t indexed”, issue rows, or URLs like:

```text
/search-console/index?resource_id=...
/search-console/index/validation?resource_id=...&item_key=...
```

then the intended action is usually not URL-by-URL Request indexing. Use the GSC issue-validation workflow:

1. Open the exact Page indexing property URL.
2. Read the “Why pages aren’t indexed” table rows:
   - Reason
   - Source
   - Validation
   - Pages
3. Select actionable candidates, usually rows with `Validation = Failed` and `Pages > 0`.
4. For each row:
   - click the row to reach `/index/drilldown?...&item_key=<key>` or derive the `item_key` from the drilldown URL;
   - open `/index/validation?...&item_key=<key>`;
   - click `START NEW VALIDATION` if present;
   - verify the validation detail page says `Validation started` and the summary table row becomes `Started`.
5. Report by issue reason and page count, not by dumping every affected URL.

Observed issue rows for `https://docs.querypie.com/` after applying this workflow:

- Blocked by robots.txt: Started, 209 pages
- Not found (404): Started, 204 pages
- Page with redirect: Started, 187 pages
- Alternate page with proper canonical tag: Started, 1 page
- Crawled - currently not indexed: Started, 633 pages
- Duplicate, Google chose different canonical than user: Started, 6 pages
- Duplicate without user-selected canonical: Passed, 2 pages
- Redirect error: Passed, 0 pages
- Discovered - currently not indexed: Passed, 25 pages

## Browser / CDP pitfalls

- GSC is a single-page app. After navigation, do not treat any body text containing `Validation` as ready. Wait for the `Validation details` heading plus either the `START NEW VALIDATION` button or a clearly terminal/started validation status.
- Multiple Search Console tabs may be open. A CDP helper that selects the first matching tab can attach to a stale/background tab and see only partial `Examples` content, missing the start button. Prefer a fresh tab, or choose the newest matching Search Console target and activate/bring it to front.
- `wait_for("started")` can time out even after the page updates; take a fresh snapshot before concluding the action failed.
- Chrome remote debugging on this machine can expose only the `DevToolsActivePort` browser WebSocket while `/json/list` or `/json/version` are unavailable. CDP clients should fall back to reading `~/Library/Application Support/Google/Chrome/DevToolsActivePort` and use browser-level `Target.getTargets` / `Target.attachToTarget`.
- Browser-level CDP can also lack `Network.getAllCookies` even after target attach. For frontend session export, try cookie retrieval in this order: browser-level `Network.getAllCookies`, browser-level `Storage.getCookies`, then target-session `Network.getCookies({ urls: [currentGscUrl] })`.

## OAuth scope pitfall

- `sitemaps.list` works with readonly scope:
  - `https://www.googleapis.com/auth/webmasters.readonly`
- `sitemaps.submit` requires write scope:
  - `https://www.googleapis.com/auth/webmasters`
- A stored OAuth token originally granted only readonly scope is still `valid=True` for read commands, but it is insufficient for `sitemaps.submit`.
- Write commands such as `submit-sitemap` and `refresh-sitemaps` should call the shared credential loader with an explicit required scope (`https://www.googleapis.com/auth/webmasters`) so the CLI automatically starts OAuth re-auth when a valid readonly token is present.
- Do not rely on a separate local preflight that only prints “move/delete token and rerun”; that blocks a fixable command before OAuth has a chance to request the required write scope.
- If Google still returns HTTP 403 `Request had insufficient authentication scopes` after automatic re-auth, then report the exact scope requirement and ask before manually backing up/removing the token.

## CLI UX recommendation

A GSC CLI that supports indexing refresh workflows should:

- include a command explaining that ordinary Search Console `Request indexing` is not public API-accessible;
- expose explicit `submit-sitemap <site_url> <sitemap_url>` and bulk `refresh-sitemaps` commands;
- expose a browser-session command for Page indexing issue validation, e.g. `validate-index-issues-browser <site_url> [--submit]`;
- default issue validation to `Failed` rows and require explicit flags for `Started` or all statuses;
- request the write OAuth scope automatically for sitemap submit commands and only surface manual token recovery instructions if re-auth/submit still fails with insufficient-scope errors;
- avoid deleting or moving existing OAuth tokens without user approval.
