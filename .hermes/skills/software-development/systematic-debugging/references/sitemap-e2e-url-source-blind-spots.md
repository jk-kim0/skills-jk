# Sitemap E2E URL-source blind spots

Use this when a sitemap/stage URL-health E2E passes but users report first-party 404s.

## Durable lesson

A sitemap E2E that only checks `<loc>` entries is a sitemap health check, not a whole-site dead-link check. It will miss:

- public entrypoints intentionally omitted from sitemap, such as legal pages, pricing aliases, legacy redirects, or app handoff routes
- first-party links embedded in MDX/TSX/JSON that are not sitemap-listed
- middleware rewrite chains where the middleware unit test validates only `x-middleware-rewrite`, but the downstream App Router route handler still fails

## Investigation checklist

1. Compare every reported broken URL against all sitemap inputs:
   - archived fixture XML
   - live production sitemap XML
   - any explicit E2E allow/critical URL lists
2. If the broken URL is absent from sitemap inputs, classify it as a test coverage gap, not as a false negative in URL checking logic.
3. Reproduce the exact URL on the target environment with headers, not only the final status:
   - final HTTP status
   - redirect count and final URL
   - `x-matched-path` / middleware-related headers when available
4. For Next.js middleware rewrites, inspect the downstream route handler:
   - route handlers may read `new URL(request.url).pathname`
   - after middleware rewrite, that pathname can still be the original unprefixed URL
   - handlers that parse locale from `request.url` can return 404 even though middleware rewrote to `/:locale/...`
5. For content links, extract first-party hrefs from MDX/TSX/JSON separately from sitemap URLs.

## Test design pattern

Split URL health tests into separate URL-source contracts:

1. `sitemap loc health`
   - checks archived/live sitemap `<loc>` entries only
2. `critical public entrypoint health`
   - checks known high-value entrypoints and aliases even when omitted from sitemap
   - examples: legal pages, pricing aliases, app handoff URLs, legacy publication URLs
3. `repo-authored first-party link health`
   - extracts internal absolute links from `src/content/**/*.mdx`, TSX navigation/footer data, and JSON config
   - excludes `mailto:`, `tel:`, hash-only links, and external hosts
   - follows redirects and requires final 200 unless the URL is explicitly allowlisted as an external handoff

## Fix pattern for App Router rewrite/handler mismatch

When a localized route handler fails only for unprefixed requests:

- Prefer using App Router params (`params.locale`, catch-all params) rather than reparsing locale from `request.url`.
- If request URL parsing is unavoidable, allow both prefixed and unprefixed forms explicitly.
- Add regression coverage that checks the real chain, not just the middleware rewrite header:
  unprefixed request -> middleware rewrite/redirect -> route handler behavior -> final 200/expected redirect.

## Reporting shape

Report the distinction clearly:

- "The sitemap E2E did not miss a sitemap URL; the broken URL was not in any sitemap input."
- "The failure class is an untested public-entrypoint/dead-link source."
- "The immediate fix is to add critical URL inputs; the durable fix is to add first-party link extraction and downstream route-handler coverage."
