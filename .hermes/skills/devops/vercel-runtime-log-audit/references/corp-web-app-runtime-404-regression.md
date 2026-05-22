# corp-web-app Runtime Log 404 regression investigation pattern

Use this reference when `corp-web-app` Vercel Runtime Log wiki snapshots show repeated 404s that look like real content/application paths rather than scanner noise.

## Observed class of issue

A repeated 404 can come from a split routing contract rather than a missing page:

1. `middleware.ts` rewrites an unprefixed public URL to a locale-prefixed App Router route, for example `/privacy-policy` -> `/en/privacy-policy` or `/chat/publication/...` -> `/en/chat/publication/...`.
2. Vercel/Next shows the request as matching the locale route via headers such as `x-matched-path: /[locale]/privacy-policy`.
3. The route handler still reads `new URL(request.url).pathname`, which may be the original unprefixed path.
4. If the handler extracts locale only from `request.url`, it can return 404 even though middleware tests prove the rewrite header exists.

This was observed for:
- `/privacy-policy` and `/terms-of-service`: locale-prefixed `/en/...` worked, unprefixed returned 404.
- `/chat/publication/...`: locale-prefixed `/en/chat/publication/...` redirected to `app.querypie.com`, unprefixed returned 404.
- `/pricing`: the root `/pricing` page had been removed and only `/:locale/pricing` route handler existed; middleware allowlist did not include `/pricing`.

## Investigation recipe

1. Read the dated wiki pages and list repeated 404s.
2. Classify scanner noise separately from real application/content paths.
3. For each real path, probe both stage and production exactly:
   - `https://stage.querypie.com/<path>`
   - `https://www.querypie.com/<path>`
4. For each failing unprefixed path, also probe the locale-prefixed counterpart:
   - `/en/<path>` or another expected locale-prefixed form.
5. Capture status, final URL, `x-matched-path`, `location`, and content type.
6. If unprefixed fails but locale-prefixed works, inspect:
   - `src/middleware.ts` default-locale rewrite allowlists/prefixes
   - the matching `src/app/**/route.ts` handler
   - whether the handler depends on `request.url` containing the rewritten locale prefix
7. Review git history for both middleware and route handlers, not only middleware:
   - `git log --oneline -- src/middleware.ts <route-handler> <tests>`
   - inspect PR bodies for stated routing intent.
8. Check tests for split coverage gaps:
   - middleware tests may only assert `x-middleware-rewrite`
   - route tests may call handlers directly with already-locale-prefixed URLs
   - neither proves the real runtime chain from unprefixed request -> middleware -> route handler.

## Fix pattern: redirect when the route handler needs pathname locale

For `corp-web-app`, do not blindly add every unprefixed English path to `DEFAULT_LOCALE_REWRITE_PATHS`.

Use two buckets in `src/middleware.ts`:

- `DEFAULT_LOCALE_REWRITE_PATHS` / `DEFAULT_LOCALE_REWRITE_PREFIXES` for page routes where preserving the clean public unprefixed English URL is safe, because the target page does not need `request.url.pathname` to include `/en`.
- `DEFAULT_LOCALE_REDIRECT_PATHS` / `DEFAULT_LOCALE_REDIRECT_PREFIXES` for route handlers or aliases that parse locale from the actual URL pathname. These should redirect to `/en/...` first so the handler receives a locale-prefixed URL instead of seeing the original unprefixed pathname and returning 404.

Observed redirect bucket examples:
- `/pricing`
- `/privacy-policy`
- `/privacy-policy-en`
- `/privacy-policy-ko`
- `/terms-of-service`
- `/chat/publication/**`

Keep rewrite-only examples in the rewrite bucket when their public URL should remain unprefixed and tests show they do not need a pathname locale, e.g. `/plans`, `/company/*`, `/archived`, `/t/*`, `/eula`.

Regression test shape:
- middleware tests should assert `location: https://www.querypie.com/en/...` and no `x-middleware-rewrite` for redirect-bucket routes.
- keep route-handler tests for the locale-prefixed handler behavior, but do not rely on route-handler tests alone because direct handler calls with `/en/...` do not reproduce the unprefixed middleware chain.
- run the narrow middleware plus affected handler tests, then `git diff --check` and the repo's test-group assertion if a test file was added or moved.

## Post-fix live verification pattern

After opening a middleware/route fix PR, verify the suspected paths against both environments with direct HTTP probes. Do not infer production behavior from a PR Preview/Vercel check alone.

Recommended probe shape:

```bash
python3 - <<'PY'
import subprocess
paths = [
    '/pricing',
    '/terms-of-service',
    '/privacy-policy',
    '/privacy-policy-en',
    '/privacy-policy-ko',
    '/chat/publication/<id>/<slug>',
]
for base in ['https://stage.querypie.com', 'https://www.querypie.com']:
    print('BASE', base)
    for path in paths:
        cmd = [
            'curl', '-sS', '-L', '-H', 'Accept-Language: en-US,en;q=0.9',
            '-o', '/dev/null', '-w', '%{http_code}\t%{url_effective}\t%{num_redirects}',
            base + path,
        ]
        res = subprocess.run(cmd, text=True, capture_output=True, timeout=30)
        out = res.stdout.strip() if res.returncode == 0 else f'ERR rc={res.returncode} {res.stderr.strip()}'
        print(f'{path}\t{out}')
PY
```

Interpretation notes:
- `stage.querypie.com` can already show the fixed behavior while `www.querypie.com` still returns 404 if production has not received the same code yet.
- A PR `Deploy` / `Vercel` success can mean the preview deployment completed; it does not by itself prove `www.querypie.com` production has been updated.
- If production is expected to update soon, either wait for the actual production deployment signal or schedule a short delayed re-probe (for example 3 minutes later) before concluding the fix failed.
- Also probe the locale-prefixed counterpart such as `/en/privacy-policy` and `/en/chat/publication/...`: if prefixed paths are 200 while unprefixed paths are 404, the handler exists and the remaining issue is the unprefixed middleware/production rollout path, not missing content.

## Reporting pattern

Separate these causes in the report:

- `middleware allowlist gap`: unprefixed route never reaches the localized handler, e.g. `/pricing` after root page removal.
- `rewrite/handler URL contract gap`: middleware rewrites to a localized handler, but handler reads original unprefixed `request.url` and rejects it.
- `content broken link`: current rendered HTML/MDX emits a URL whose canonical target differs, e.g. a whitepaper link missing the numeric slug segment.
- `route-policy decision`: repeated path is real but no current public route exists, e.g. a list route not yet rolled out.

Do not attribute the regression to a later route-group move unless the logic actually changed. A route-group PR can preserve and redeploy an already-broken contract without being the root cause.
