# GSC browser validation batch attach pattern

Use this when maintaining a CLI that starts Search Console `START NEW VALIDATION` actions through a logged-in browser session.

## Problem observed

A wrapper that enumerates sites and then launches a separate browser helper subprocess for each property can cause:

- repeated Chrome remote-debugging approval prompts
- CDP WebSocket connect hangs/timeouts between sites
- partial execution where early sites run and later sites fail before reaching GSC

## Durable fix pattern

For browser/CDP mode, build one helper command that accepts repeated `--site` arguments and processes every selected property inside the same Node process and same browser WebSocket attach.

Shape:

```bash
gsc-browser-indexing \
  --index-issues \
  --submit \
  --port 9333 \
  --site https://docs.querypie.com/ \
  --site https://querypie.ai/ \
  --site-delay-ms 500
```

The outer `bin/gsc validate-index-issues --browser` wrapper should:

1. discover/select sites once
2. construct a single browser-helper command with all selected `--site` values
3. apply a batch timeout for the whole helper
4. avoid per-site subprocess retries in browser mode unless the helper itself supports retrying without reconnecting

## Chrome profile recommendation

Pair this with a dedicated persistent debug profile to avoid approval prompts and keep GSC login state:

```bash
open -na "Google Chrome" --args \
  --remote-debugging-port=9333 \
  --remote-allow-origins='*' \
  --user-data-dir="$HOME/.chrome-hermes-gsc" \
  --no-first-run \
  --no-default-browser-check \
  "https://search.google.com/search-console"
```

Then run the GSC command with `--port 9333`.

## Validation URL pitfall

When moving from a drilldown URL to a validation URL, preserve the exact `resource_id` from the drilldown URL. Do not reconstruct it with a different encoding form. Safer pattern:

```js
const url = new URL(drilldownHref);
url.pathname = '/search-console/index/validation';
const validationUrl = url.toString();
```

Also prefer clicking the GSC `SEE DETAILS` control when available before falling back to direct URL construction.
