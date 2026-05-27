# Sitemap E2E required-public-URLs fixture

Use this note when a corp-web-app sitemap availability E2E misses real 404s because the failing routes are not listed in `https://www.querypie.com/sitemap.xml`.

## Problem pattern

A sitemap-derived test only covers URLs present in the production sitemap snapshot/live sitemap. It can miss important production/stage regressions for:

- unprefixed public entrypoints that are expected to rewrite or redirect, such as `/privacy-policy`, `/terms-of-service`, and `/pricing`
- legacy or inbound routes that should still resolve through middleware/redirect behavior, such as `/chat/publication/...`
- content links discovered from real traffic or repository content, such as broken whitepaper links inside blog MDX
- runtime-log candidates that are valid user/bot traffic but intentionally absent from the sitemap

## Durable improvement

Keep the sitemap-derived URL set, but merge in a small explicit fixture of critical public URLs, for example:

- `tests/e2e/fixtures/required-public-urls.txt`

Fixture rules:

1. One path or absolute URL per line.
2. Allow blank lines and `#` comments.
3. Normalize relative paths against the production origin for source reporting.
4. Convert each source URL to the configured stage/base origin before probing.
5. Dedupe after combining sitemap URLs and fixture URLs.
6. Report whether each checked URL came from the sitemap, the required fixture, or both if the test already tracks source metadata.

## Candidate discovery workflow

When expanding this fixture from Vercel/runtime logs:

1. Review the relevant runtime-log wiki/report pages or exported logs.
2. Exclude scanner/probe/feed noise, image-directory probes, favicon/mobile icon noise, and obviously invalid attack payloads.
3. Keep app/content/publication requests that should resolve for real users or crawlers.
4. Before committing a new required URL, verify the intended target behavior against stage with a bounded redirect-following `HEAD`/`GET` probe.
5. Include only URLs that are expected to end at final HTTP 200, unless the E2E intentionally asserts a different final status.
6. Separately confirm that the added fixture URLs are not already in the live sitemap; otherwise the fixture is redundant.

## Common checks

- `https://stage.querypie.com/<path>` should end in final 200 after allowed redirects.
- `https://www.querypie.com/sitemap.xml` absence is not a reason to skip a required public URL when the URL is an important entrypoint, redirect, or real inbound path.
- For MDX/content links, fix the source link and add/keep the resolved URL in the fixture only if it remains a critical public route.

## PR communication

In the PR body, explicitly distinguish:

- sitemap-derived coverage
- required-public-URLs fixture coverage
- fixture entries confirmed absent from live sitemap
- fixture entries confirmed final-200 on stage

This prevents reviewers from assuming the sitemap E2E is complete simply because all sitemap `<loc>` entries pass.
