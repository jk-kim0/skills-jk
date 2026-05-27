# Sitemap stage availability E2E — corp-web-app PR #783

Session date: 2026-05-21
Repo: `querypie/corp-web-app`
PR: https://github.com/querypie/corp-web-app/pull/783
Branch: `test/e2e-sitemap-stage`

## User request

Add an E2E test for production pre-deploy validation:
- archive `https://www.querypie.com/sitemap.xml` at PR creation time as `sitemap.2026-05-21.xml`
- at test runtime, fetch the live production sitemap too
- use the union of archived + live sitemap URLs
- test the corresponding URLs on `https://stage.querypie.com`, not production
- allow 30x only if the followed final response is 200
- print readable text logs, one URL per line
- collect final Non-200 entries under an `Errors:` section
- fail the E2E if `Errors` has any entries

## Implementation shape used

Files changed:
- `tests/e2e/fixtures/sitemap.2026-05-21.xml`
- `tests/e2e/sitemap-stage.spec.ts`
- `tests/package.json`
- `tests/README.md`

The spec:
- reads the archived XML fixture
- fetches `https://www.querypie.com/sitemap.xml` live at runtime
- extracts `<loc>` entries with a regex and basic XML entity decoding
- filters to `https://www.querypie.com/`
- dedupes and sorts the union
- rewrites each URL to `https://stage.querypie.com` while preserving path/query
- checks with Node `http`/`https` requests rather than browser navigation
- follows redirects manually up to a limit
- prints one URL per line and a final `Summary:`/`Errors:` block
- asserts `errors.length === 0` to keep the assertion output compact

## Important logging lesson

The first version asserted the full errors array equals `[]`. That produced an enormous Playwright object diff and made the useful human-readable log harder to scan. Prefer:

```ts
expect(
  errors.length,
  'Every archived/live sitemap URL should return 200 on stage, allowing redirects only when the final response is 200. See the Errors section above.'
).toBe(0);
```

## Verification result at PR creation

Local hosted-stage run command from `tests/`:

```bash
npm run test:e2e:sitemap:stage
```

The test intentionally failed against current stage because it found real Non-200 URLs:

```text
Summary: total=182 direct200=171 redirectTo200=0 errors=11
Errors:
- ERROR status=404 final=404 source=https://www.querypie.com/eula stage=https://stage.querypie.com/eula redirects=- finalUrl=https://stage.querypie.com/eula
- ERROR status=404 final=404 source=https://www.querypie.com/rss-en-blog.xml stage=https://stage.querypie.com/rss-en-blog.xml redirects=- finalUrl=https://stage.querypie.com/rss-en-blog.xml
- ERROR status=404 final=404 source=https://www.querypie.com/rss-en-learn.xml stage=https://stage.querypie.com/rss-en-learn.xml redirects=- finalUrl=https://stage.querypie.com/rss-en-learn.xml
- ERROR status=404 final=404 source=https://www.querypie.com/rss-en-webinar.xml stage=https://stage.querypie.com/rss-en-webinar.xml redirects=- finalUrl=https://stage.querypie.com/rss-en-webinar.xml
- ERROR status=404 final=404 source=https://www.querypie.com/rss-ja-blog.xml stage=https://stage.querypie.com/rss-ja-blog.xml redirects=- finalUrl=https://stage.querypie.com/rss-ja-blog.xml
- ERROR status=404 final=404 source=https://www.querypie.com/rss-ja-learn.xml stage=https://stage.querypie.com/rss-ja-learn.xml redirects=- finalUrl=https://stage.querypie.com/rss-ja-learn.xml
- ERROR status=404 final=404 source=https://www.querypie.com/rss-ja-webinar.xml stage=https://stage.querypie.com/rss-ja-webinar.xml redirects=- finalUrl=https://stage.querypie.com/rss-ja-webinar.xml
- ERROR status=404 final=404 source=https://www.querypie.com/rss-ko-blog.xml stage=https://stage.querypie.com/rss-ko-blog.xml redirects=- finalUrl=https://stage.querypie.com/rss-ko-blog.xml
- ERROR status=404 final=404 source=https://www.querypie.com/rss-ko-learn.xml stage=https://stage.querypie.com/rss-ko-learn.xml redirects=- finalUrl=https://stage.querypie.com/rss-ko-learn.xml
- ERROR status=404 final=404 source=https://www.querypie.com/rss-ko-webinar.xml stage=https://stage.querypie.com/rss-ko-webinar.xml redirects=- finalUrl=https://stage.querypie.com/rss-ko-webinar.xml
- ERROR status=404 final=404 source=https://www.querypie.com/rss.xml stage=https://stage.querypie.com/rss.xml redirects=- finalUrl=https://stage.querypie.com/rss.xml
```

## Worktree verification workaround

Fresh worktree lacked `tests/node_modules`, producing:

```text
Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@playwright/test' imported from .../tests/e2e/playwright.config.ts
```

The root checkout already had `tests/node_modules`, so local verification used a temporary symlink:

```bash
ln -s /Users/jk/workspace/corp-web-app/tests/node_modules /Users/jk/workspace/corp-web-app/.worktrees/e2e-sitemap-stage/tests/node_modules
npm run test:e2e:sitemap:stage
rm -f tests/node_modules
rm -rf tests/test-results tests/playwright-report
```

Do not commit the symlink or generated outputs.
