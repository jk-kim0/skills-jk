# Demo use-cases source parity notes

Session-derived facts from corp-web-app PR #637 follow-up.

## Correct source root

Use the full demo use-cases source root:

```text
../corp-web-contents/pages/features/demo/use-cases/<id>/<slug>/<locale>/content.mdx
```

Do not use this as the full source:

```text
../corp-web-contents/page-archives/customers/customer-success-cases/<id>/<slug>/<locale>/content.mdx
```

That archive root covers only IDs 1-5 and caused an incomplete migration when treated as the whole use-case collection.

## Corpus counts verified

`corp-web-contents/pages/features/demo/use-cases` contains:

- IDs: 1-29
- EN: 29 records
- JA: 29 records
- KO: 6 records, IDs 1-6
- Total MDX records: 64

`corp-web-japan/src/content/use-cases` had 29 Japanese files whose normalized bodies matched the JA source records from `pages/features/demo/use-cases`.

## ID families

- IDs 1-5: customer-success-style use cases; assets commonly under `public/customer-success-cases/...`.
- ID 6: QueryPie AI Agent demo; EN/JA/KO exist.
- IDs 7-29: AIP use-case records; EN/JA exist, KO does not currently exist in source.

## Test contract that caught the corrected scope

The corp-web-app migration test should assert:

- all IDs 1-29 exist across records
- total records = 64
- list coverage EN = 1-29
- list coverage JA = 1-29
- list coverage KO = 1-6
- route-aligned assets exist under `public/demo/use-cases/<id>/...`

## Docs that needed updating

When this source correction is made, update docs in the same PR:

- `docs/inventories/mdx-collection-migration-matrix.md`
- `docs/inventories/content-collection-inventory.md`

The stale wording to remove/reframe is any statement that the use-cases source is the `page-archives/customers/customer-success-cases` archive or that the current source has full KO coverage.
