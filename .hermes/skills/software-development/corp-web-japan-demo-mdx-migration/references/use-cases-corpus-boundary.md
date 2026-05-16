# use-cases corpus boundary investigation (May 2026)

## Finding

For corp-web-japan use-case migrations, the authoritative full source corpus is:

```text
../corp-web-contents/pages/features/demo/use-cases/<id>/<slug>/<locale>/content.mdx
```

The archive path below is only the customer-success subset for IDs 1-5 and must not be treated as the full use-cases source:

```text
../corp-web-contents/page-archives/customers/customer-success-cases/<id>/<slug>/<locale>/content.mdx
```

## Counts observed

In `corp-web-contents`:

- `pages/features/demo/use-cases/*/*/ja/content.mdx`: 29 records
- `pages/features/demo/use-cases/*/*/en/content.mdx`: 29 records
- `pages/features/demo/use-cases/*/*/ko/content.mdx`: 6 records

In `corp-web-japan` after migration PR #187:

- `src/content/use-cases/*.mdx`: 29 JA records
- Each local JA body normalized-equal to the matching `pages/features/demo/use-cases/<id>/<slug>/ja/content.mdx` source body
- Route-aligned thumbnails live under `public/use-cases/<id>/thumbnail.png`

## ID groups

- IDs 1-5: customer-success-style records; source `ogImage` commonly points under `public/customer-success-cases/`; these records also exist in the old `page-archives/customers/customer-success-cases/**` archive.
- ID 6: `querypie-ai-agent-demo`; has EN/JA/KO in the full use-cases source, but is not in the customer-success archive.
- IDs 7-29: AIP use-case records; EN/JA in source, no KO observed in this investigation.

## Pitfall from corp-web-app PR #637

A PR can look like a use-cases migration while actually migrating only the customer-success subset. In PR #637, tests asserted:

```text
ids.size === 5
records.length === 15
```

That made IDs 6-29 invisible to regression coverage. For full use-case parity, tests should derive or assert the full source coverage (for example expected IDs 1-29 for JA, and locale-specific source counts), not only the 5 customer-success IDs.

## Recommended validation commands

```bash
# Source counts by locale
find ../corp-web-contents/pages/features/demo/use-cases -path '*/content.mdx' | awk -F/ '{print $(NF-1)}' | sort | uniq -c

# JA source IDs
find ../corp-web-contents/pages/features/demo/use-cases -path '*/ja/content.mdx' | sed -E 's#.*/use-cases/([0-9]+)/.*#\1#' | sort -n

# Local corp-web-japan IDs
find src/content/use-cases -name '*.mdx' | sed -E 's#.*/([0-9]+)-.*#\1#' | sort -n
```
