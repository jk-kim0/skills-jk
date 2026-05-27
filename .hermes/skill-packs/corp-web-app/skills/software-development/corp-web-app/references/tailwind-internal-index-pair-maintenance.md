# Tailwind internal index pair maintenance

Use this when updating `src/app/(tailwind)/[locale]/internal/tailwind/**` so the internal Tailwind index reflects current `main` accurately.

## Goal

Keep `/{locale}/internal/tailwind` aligned with the actual set of routes already moved under `src/app/(tailwind)/**`, with listing/detail families shown side by side when the UI already supports that layout.

## Source of truth

1. Run the inventory and filter to `(tailwind)` routes:

```bash
node scripts/inventory-tailwind-pages.ts --json | jq '[.[] | select(.page | startswith("src/app/(tailwind)/"))]'
```

2. Compare the inventory route list with the `routePattern` values in:

- `src/app/(tailwind)/[locale]/internal/tailwind/tailwind-pages.ts`

A quick parity check can compare the two route sets and report missing/extra patterns.

## Practical workflow

1. Confirm current `main` / `origin/main` first.
2. Inspect `page.tsx` before changing it. If it already renders `listing` and `detail` slots side by side, do not broaden the UI PR unnecessarily.
3. Patch only `tailwind-pages.ts` when the problem is missing family entries, sample links, or stale route metadata.
4. Re-run the route-set parity check and targeted lint:

```bash
npm run lint -- --file 'src/app/(tailwind)/[locale]/internal/tailwind/page.tsx' --file 'src/app/(tailwind)/[locale]/internal/tailwind/tailwind-pages.ts'
```

## Common cases from current main

- Some families move detail first, then listing later. The internal index data can lag behind even when the page UI is already pair-oriented.
- Demo families (`/t/demo/acp`, `/t/demo/aip`, `/t/demo/use-cases`) should usually be represented as listing/detail pairs once both routes are in `(tailwind)`.
- Publication/document families can include mixed states: some have listing + detail, some detail only.
- Standalone internal pages such as `/{locale}/internal/tailwind` should stay outside the pair sections.

## Pitfall

Do not rely only on the older hand-maintained sample list inside `tailwind-pages.ts`. The inventory script is the faster way to detect newly migrated `(tailwind)` routes that the internal index forgot to list.
