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

## May 19 and May 20, 2026 snapshot pattern

Observed command shape remained the same:

```bash
vercel logs --project corp-web-japan --environment production \
  --since '<YYYY-MM-DD>T00:00:00+09:00' \
  --until '<YYYY-MM-DD+1>T00:00:00+09:00' \
  --json --no-branch --scope querypie --limit 1000
```

May 19 findings:
- broad query emitted 104 JSON rows and deduped to 50 unique rows; status mix `307`: 9, `200`: 36, `404`: 5
- direct `307` emitted 71 JSON rows and deduped to 50 unique rows
- direct `404` emitted 20 JSON rows and deduped to 20 unique rows
- direct `500`/`502`/`503`/`504` and `--level error` filtered for 5xx returned 0 rows
- representative `307`: `/solutions/aip/integrations` -> local `/platforms/aip/integrations`; `/solutions/acp/integrations` -> upstream; `/plans` appeared as historical `307` but later live checked as `200`; whitepaper 24 typo `/ai-tranformation-japan` canonicalized to `/ai-transformation-japan`; legacy `/features/...` forwarding rows
- representative `404`: config/API/secret probes (`/actuator/env`, `/api/env`, `/secrets.json`, `/appsettings.json`, `/api/config`), WordPress/XML-RPC (`/xmlrpc.php`), `/.well-known/traffic-advice`, legacy `/posts/event/*`, `/demo/1`, `/t/platforms/aip/integrations`, malformed smart-quoted legacy use-case URL

May 20 findings:
- broad query emitted 121 JSON rows and deduped to 50 unique rows; status mix `200`: 47, `307`: 3
- direct `307` emitted 66 JSON rows and deduped to 50 unique rows
- direct `404` emitted 14 JSON rows and deduped to 14 unique rows
- direct `500`/`502`/`503`/`504` and `--level error` filtered for 5xx returned 0 rows
- representative `307`: intro deck aliases such as `/features/documentation/acp-introduction-download`, `/features/documentation`, `/features/demo`, legacy use-case/whitepaper/blog routes, whitepaper 24 typo/null canonicalization
- representative `404`: `/posts/event/6`, `/events/6/kansai-ai-meetup-vol-3`, `/api/og/ja/company/news`, config/API/secret probes, XML-RPC/WordPress-shaped paths, `/.well-known/traffic-advice`

Interpretation reminders:
- Treat `5xx` as clean when all explicit integer status checks and error-level client-side filters are zero.
- Keep scanner/probe rows out of redirect-review work unless first-party/current product evidence exists.
- For current-day partial reports, clearly state the day is incomplete and later recomputation may include manual live checks.
- For Korean wiki reports, translate structural labels as well as prose; run a quick grep for leftover English template fragments before committing.

## Reporting reminder

For current-day snapshots, explicitly say the day is not complete and manual live checks may pollute later same-day recomputation. Put manual `curl -I` rechecks in a separate section from log-derived counts.
