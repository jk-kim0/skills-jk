# Stage sitemap RSS 404 diagnosis

Use this reference when a corp-web-app stage sitemap availability E2E fails only for RSS endpoints such as:

- `/rss.xml`
- `/rss-en-blog.xml`
- `/rss-en-learn.xml`
- `/rss-en-webinar.xml`
- `/rss-ja-blog.xml`
- `/rss-ja-learn.xml`
- `/rss-ja-webinar.xml`
- `/rss-ko-blog.xml`
- `/rss-ko-learn.xml`
- `/rss-ko-webinar.xml`

## Observed failure shape

The E2E rewrites production sitemap URLs from `https://www.querypie.com/...` to `https://stage.querypie.com/...` and reports:

```text
ERROR status=404 final=404 source=https://www.querypie.com/rss.xml stage=https://stage.querypie.com/rss.xml redirects=- finalUrl=https://stage.querypie.com/rss.xml
```

Production RSS may still be healthy:

```bash
curl -sS -I -L https://www.querypie.com/rss.xml
curl -sS -I -L https://www.querypie.com/rss-en-blog.xml
```

while stage RSS returns 404:

```bash
curl -sS -I -L https://stage.querypie.com/rss.xml
curl -sS -I -L https://stage.querypie.com/rss-en-blog.xml
```

## Root cause pattern

In corp-web-app, `/rss*.xml` is handled by middleware:

- `src/middleware.ts` detects `pathname.startsWith('/rss') && pathname.endsWith('.xml')`.
- It calls `src/utils/middleware/rss.ts` `generateRssXml(pathname)`.
- If `generateRssXml()` returns null, middleware returns 404.

The key pitfall is a production-only guard in `generateRssXml()`:

```ts
if (!isProduction()) {
  return null;
}
```

`isProduction()` is based on:

```ts
process.env.VERCEL_TARGET_ENV === 'production'
```

Therefore stage/preview can return 404 before attempting to read Blob-backed RSS files, even when corp-web-contents generated and uploaded the files.

## Why this conflicts with the stage sitemap E2E

`src/app/sitemap.xml/route.ts` serves Blob-backed `public/sitemap.xml` without the same production-only guard. corp-web-contents `scripts/generate-sitemap.js` includes all `public/rss*.xml` files in `public/sitemap.xml`.

So the inconsistent state can be:

- `https://stage.querypie.com/sitemap.xml` returns 200 and contains RSS locs.
- `https://stage.querypie.com/rss*.xml` returns 404 because RSS middleware is production-only.

This is a code policy mismatch, not necessarily missing corp-web-contents RSS files.

## Diagnosis checklist

1. Confirm repo and branch:

```bash
pwd
git rev-parse --show-toplevel
git status --short --branch
```

2. Verify production vs stage HTTP behavior:

```bash
for url in \
  https://www.querypie.com/rss.xml \
  https://www.querypie.com/rss-en-blog.xml \
  https://stage.querypie.com/sitemap.xml \
  https://stage.querypie.com/rss.xml \
  https://stage.querypie.com/rss-en-blog.xml; do
  echo "--- $url"
  curl -sS -I -L --max-redirs 3 "$url" | awk 'BEGIN{IGNORECASE=1} /^HTTP\// || /^content-type:/ || /^location:/ || /^cache-control:/ || /^x-vercel-cache:/ || /^server:/ {print}'
done
```

3. Extract RSS URLs from production and stage sitemaps:

```bash
python3 - <<'PY'
import urllib.request,re
for url in ['https://www.querypie.com/sitemap.xml','https://stage.querypie.com/sitemap.xml']:
    data=urllib.request.urlopen(url,timeout=20).read().decode('utf-8','replace')
    rss=re.findall(r'<loc>(https?://[^<]*rss[^<]*)</loc>',data)
    print('---',url,'rss_count',len(rss))
    for x in rss: print(x)
PY
```

4. Check sibling corp-web-contents generated files:

```bash
find ../corp-web-contents/public -maxdepth 1 -name 'rss*.xml' -print | sort
rg -n 'rss|addRssUrls|generate-rss' ../corp-web-contents/scripts ../corp-web-contents/docs
```

5. Inspect corp-web-app RSS serving code:

```bash
sed -n '45,65p' src/middleware.ts
sed -n '1,80p' src/utils/middleware/rss.ts
sed -n '1,20p' src/utils/env/is-production.ts
```

## Preferred fix direction

If the E2E is intended to verify that production sitemap URLs are available on stage before deploy, prefer allowing stage to serve Blob-backed RSS files too:

- Remove or relax the non-production early return in `src/utils/middleware/rss.ts`.
- Keep returning 404 when the Blob-backed RSS file is truly missing.

This aligns `/sitemap.xml` and `/rss*.xml` stage behavior.

## Implementation pattern

Keep the code change narrow:

1. In `src/utils/middleware/rss.ts`, remove the `isProduction` import and the early return:

```ts
if (!isProduction()) {
  return null;
}
```

2. Do not change `src/middleware.ts` unless the RSS path matching itself is wrong. The middleware can continue to return 404 when `generateRssXml()` returns `null`.
3. Add a focused utility test under `src/utils/middleware/__tests__/rss.test.ts` that mocks `FileQuery`, `getBaseUrl`, and `getResourceBranch`.
4. The regression test should set `process.env.VERCEL_TARGET_ENV = 'preview'`, provide a mock file such as `main/public/rss-en-blog.xml`, and assert that `generateRssXml('/rss-en-blog.xml')` returns XML and calls `FileQuery.fetchTextFileData` with that file.
5. Add a missing-file assertion that still returns `null` so the existing middleware 404 path remains covered.

Verification used successfully:

```bash
# In a fresh worktree, if node_modules is only present in the root checkout:
ln -s /absolute/path/to/corp-web-app/node_modules /absolute/path/to/worktree/node_modules
npm run test:utilities -- --runInBand
node scripts/ci/assert-test-groups.mjs
rm -f /absolute/path/to/worktree/node_modules
```

Do not run a local dev server for this fix unless explicitly requested; CI/Preview deployment will prove the hosted endpoint behavior after merge/deploy.

## Alternative but less preferred fixes

Use only if product/deployment policy explicitly requires RSS to be production-only:

1. Exclude RSS locs from the stage sitemap availability E2E.
2. Generate/serve a stage sitemap that omits RSS locs.
3. Make sitemap production-only too.

These are less preferred because they either hide a stage readiness gap or contradict the current E2E goal of checking production sitemap coverage against stage.
