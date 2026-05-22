# corp-web-app runtime 404 investigation notes

Use this when auditing `querypie/corp-web-app` Vercel Runtime Log wiki pages and separating scanner noise from actionable content-route 404s.

## Durable investigation pattern

When historical `vercel logs` queries are unavailable or older rows have expired:

1. Treat the dated wiki pages as log-derived evidence, not exact totals.
2. Re-check representative paths live with `curl -I` / `curl -L -o /dev/null -w ...` against `https://www.querypie.com`.
3. Inspect current `origin/main` routing and middleware before recommending redirects.
4. Search current rendered HTML or source content for the exact broken path before classifying it as external/stale.
5. Separate:
   - scanner/probe noise
   - real 404 currently emitted by the app
   - content-internal broken links
   - stale external/bookmarked paths with a clear replacement
   - route-policy gaps that need product decision before redirects

## corp-web-app patterns observed in May 21/22 reports

### Middleware rewrite plus route-handler `request.url` mismatch

Some unprefixed paths are intended to be handled by localized route handlers through middleware rewrite, but the route handler reads the original `request.url` pathname and expects an explicit `/en`, `/ko`, or `/ja` prefix. In that case `x-matched-path` can show the localized route while the handler still returns 404.

Observed classes:

- `/privacy-policy`, `/terms-of-service`
  - middleware allowlist includes the unprefixed paths
  - localized handlers redirect correctly for `/en/privacy-policy`, `/ko/privacy-policy`, `/ja/privacy-policy`, etc.
  - unprefixed requests can still return 404 because the legal redirect helper extracts locale from `request.url`
  - fix pattern: make the handler accept unprefixed requests as default English, or convert the middleware behavior from rewrite to redirect for these paths

- `/chat/publication/...`
  - localized `/en/chat/publication/...` and `/ko/chat/publication/...` redirect to `https://app.querypie.com/chat/publication/...`
  - unprefixed `/chat/publication/...` can 404 because the redirect route regex only accepts locale-prefixed paths in `request.url`
  - fix pattern: allow the unprefixed path in the route handler and redirect directly to `app.querypie.com`

### Unprefixed default-locale route not allowlisted

If a route handler exists under `[locale]` but the unprefixed path is not in `DEFAULT_LOCALE_REWRITE_PATHS`, English/default-locale users can see a 404 even though `/en/...` works.

Observed example:

- `/pricing` returns 404 while `/en/pricing`, `/ko/pricing`, and `/ja/pricing` redirect to `/plans`.
- fix pattern: add `/pricing` to the middleware default-locale handling or add an explicit unprefixed redirect.

### Content-internal broken links

Do not assume all old-looking content paths are external stale traffic. Search source content and current production HTML for the exact URL.

Observed example:

- `/features/documentation/white-paper/2-shell-native-command-control` returned 404.
- The broken source was an MDX link to `/resources/discover/white-paper/2-shell-native-command-control`, which redirects into the 404 path.
- The valid target was `/features/documentation/white-paper/2/shell-native-command-control-ssh-proxy-architecture` (or the equivalent `/resources/discover/white-paper/2/shell-native-command-control-ssh-proxy-architecture`).
- fix pattern: update the MDX link first; do not add a broad redirect unless legacy traffic volume warrants it.

### Route-policy gaps versus simple bugs

Some repeated paths are not necessarily bugs in the current code; they represent missing public route policy or legacy landing-page decisions.

Observed examples:

- `/blog` 404 while legacy canonical blog content is under `/features/documentation/blog/:id/:slug` and preview/new content may exist under `/t/blog`.
- `/solutions` 404 while `/solutions/aip` and `/solutions/acp` are live.

Recommended classification:

- If current HTML/sitemap emits the path, treat it as an implementation bug.
- If only an adjacent or future route exists, report it as a route-policy/product decision before adding redirects.

### Current-live versus historical transient rows

If a dated runtime report shows a 404 but current live check is 200, avoid opening redirect work from the old row alone.

Observed example:

- `/ja/features/documentation/white-paper/8/secure-login-token-management` appeared in a May 22 404/mismatch mix but later returned 200 and had MDX content present.
- classify as transient/deployment-state evidence unless it recurs.

## Noise buckets seen in corp-web-app reports

Usually do not recommend redirects for:

- WordPress and reader probes: `/wp-json/wp/v2/posts`, `/feed`, `/rss`, `/feed.xml`
- sitemap probes: `/post-sitemap.xml`, `/sitemap-news.xml`, `/news-sitemap.xml`, `/sitemap_index.xml`
- legacy blog image directory probes: `/blog/content/images/...` or `/content/images/...` without a concrete asset filename
- web-standard or enterprise auto-discovery probes: `/.well-known/traffic-advice`, `/AutoDiscover/autodiscover.xml`

Treat `/apple-touch-icon.png` and `/apple-touch-icon-precomposed.png` as browser asset auto-requests rather than scanner noise. Add real assets only if mobile/PWA presentation matters or the team wants to reduce runtime 404 noise.