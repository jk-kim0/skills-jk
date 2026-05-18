# corp-web-japan runtime-log interpretation patterns

Use these notes when preparing dated Vercel Runtime Log wiki snapshots for `querypie/corp-web-japan`.

## May 17, 2026 current-day snapshot pattern

Observed command shape:

```bash
vercel logs --project corp-web-japan --environment production \
  --since '2026-05-17T00:00:00+09:00' \
  --until '2026-05-18T00:00:00+09:00' \
  --json --no-branch --scope querypie --limit 1000
```

Findings:
- broad query emitted 1000 JSON rows but deduped to 50 unique IDs
- direct `307` emitted 1000 JSON rows but deduped to 50 unique IDs
- direct `404` emitted 1000 JSON rows but deduped to 50 unique IDs
- direct `500`/`502`/`503`/`504` and `--level error` filtered for 5xx returned 0 rows
- report these as sampled top-set evidence, not authoritative counts

Representative 404 pattern:
- `/contact`, `/our-team`, `/leadership`, `/legal`, `/team`, `/enterprise`, `/imprint`, `/sales`, `/people`, `/support`
- runtime messages had `referer: null` and `userAgent: python-requests/2.31.0`
- classify as scripted generic company/contact-path probing unless a separate link audit proves first-party emission
- do not convert these to redirects by default

Representative 307 pattern:
- `/api-docs.html` -> docs API reference redirect
- `/company/news` -> local `/news`
- `/platform/ai/aip/mcp-gateway` -> local `/platforms/aip/mcp-gateway`
- `/company` and `/solutions/aip/integrations` may still forward upstream depending on current route policy; treat as route-policy follow-up candidates only if public replacement scope requires them

## Reporting reminder

For current-day snapshots, explicitly say the day is not complete and manual live checks may pollute later same-day recomputation. Put manual `curl -I` rechecks in a separate section from log-derived counts.
