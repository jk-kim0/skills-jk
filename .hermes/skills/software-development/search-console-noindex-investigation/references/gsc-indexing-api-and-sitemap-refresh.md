# GSC indexing API limits and sitemap refresh automation

Session-derived notes for Google Search Console indexing work.

## Key API facts

- There is no public Google Search Console API/CLI endpoint that performs the UI action `Request indexing` for ordinary web pages in bulk.
- URL Inspection API (`urlInspection.index.inspect`) is for status inspection only.
- Search Console API supports sitemap operations such as `sitemaps.list` and `sitemaps.submit`.
- Google Indexing API `URL_UPDATED` is officially limited/recommended for pages with `JobPosting` or `BroadcastEvent` embedded in `VideoObject`; do not use it as a general website recrawl API for marketing/docs pages.

## Safe automation path

For ordinary docs/marketing/public website pages, the safe automated substitute for “update indexing requests” is:

1. List owned Search Console properties.
2. For URL-prefix properties, list registered sitemaps.
3. Re-submit each registered sitemap with `sitemaps.submit`.
4. Treat domain properties (`sc-domain:*`) carefully because they can overlap URL-prefix properties and may duplicate work.

## OAuth scope pitfall

- `sitemaps.list` works with readonly scope:
  - `https://www.googleapis.com/auth/webmasters.readonly`
- `sitemaps.submit` requires write scope:
  - `https://www.googleapis.com/auth/webmasters`
- A stored OAuth token originally granted only readonly scope will continue to fail `sitemaps.submit` with HTTP 403 `Request had insufficient authentication scopes`, even if the CLI source code now requests both scopes.
- Fix by backing up/removing the old token and re-running OAuth so Google grants the write scope.

Example user-safe wording before changing tokens:

```text
현재 저장된 GSC 토큰은 조회 전용이라 사이트맵 재제출이 403으로 차단됩니다. 기존 조회용 토큰을 백업하고 쓰기 scope로 재인증해도 될까요?
```

## CLI UX recommendation

A GSC CLI that supports sitemap refresh should:

- include a command explaining that ordinary Search Console `Request indexing` is not public API-accessible;
- expose explicit `submit-sitemap <site_url> <sitemap_url>` and bulk `refresh-sitemaps` commands;
- preflight the OAuth token scopes before attempting bulk submit;
- print the required write scope and token backup/re-auth command when scope is missing;
- avoid deleting or moving existing OAuth tokens without user approval.
