# News list mobile card order

Use when fixing or reviewing `/<locale>/news` list card ordering in `corp-web-app`.

## Durable lesson

The public news list uses `NewsListItems` in:

`src/components/sections/resource-list/resource-list-section.component.tsx`

A mobile-only thumbnail-before-text regression can be caused by Tailwind flex direction, not JSX DOM order. In the observed case, the article markup had text first and image second, but `className="flex flex-col-reverse ... md:flex-row ..."` made the thumbnail render above the date/title/description on mobile.

## Preferred fix

For the news list card layout:

- Use `flex flex-col items-start gap-7 md:flex-row md:gap-10` on the `<article>`.
- Preserve `md:flex-row` so desktop keeps the existing text-left / image-right layout.
- Do not reorder JSX children unless the desktop/mobile visual contract requires a different source order.

## Regression guard

Add or update the focused route test in:

`src/__tests__/app/[locale]/news-public-route.test.tsx`

Useful source-shape expectations:

```ts
expect(source).toContain('flex flex-col items-start gap-7 md:flex-row md:gap-10');
expect(source).not.toContain('flex-col-reverse');
expect(source).toContain('md:flex-row md:gap-10');
```

Targeted verification is sufficient for this narrow layout contract:

```sh
npm test -- --run 'src/__tests__/app/[locale]/news-public-route.test.tsx'
```

Follow the user's repo-work preference: avoid local full builds/dev servers unless explicitly requested; push the branch and let CI/preview attach after the focused check.
