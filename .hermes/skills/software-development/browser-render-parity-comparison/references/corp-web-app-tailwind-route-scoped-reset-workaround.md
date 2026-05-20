# corp-web-app Tailwind route-scoped reset workaround

Use when a Tailwind-based page port renders with the right class names and generated Tailwind rules, but browser computed styles show reset-driven values such as:

- `padding: 0px` or `margin: 0px` from a global `*` reset
- `border: 0px none` on Tailwind `border border-*` buttons because a later unlayered `button { border: none; }` rule wins
- dark inherited link/text color on Tailwind `text-white` CTA anchors because an unlayered or CSS Module rule outranks the utility

Common corp-web-app reset examples:

```css
* {
  box-sizing: border-box;
  padding: 0;
  margin: 0;
}

button {
  border: none;
}
```

## Lesson

In Tailwind v4, utilities live in `@layer utilities`. Existing unlayered CSS in `globals.css` can outrank layered utilities, so a port from a sibling repo with a proper `@layer base` reset can visually fail even when JSX/class names match.

If the task is an existing page/PR migration, do not silently convert the global reset to `@layer base` inside that page PR. That is a broad cascade change for all CSS Modules surfaces and should be a separate visual-risk PR.

## Safe interim pattern

1. Keep the sibling repo's Tailwind `className` contract in the component for future cleanup.
2. Add a stable route-local selector, e.g. `data-publication-post` on the page shell.
3. Add a page-specific CSS Module that restores only the reset-overridden margin/padding values for this route.
4. Import the CSS Module into the route component and combine its class with the Tailwind class string.
5. Verify in the browser with computed style, not class presence.

Example:

```tsx
import styles from './blog-detail-post-page.module.css';

<section
  data-publication-post
  className={`${styles.publicationPostRoot} mx-auto max-w-[1920px] bg-white px-[30px] pb-[120px] pt-[112px] lg:px-[30px] lg:pb-[160px] lg:pt-[144px]`}
>
```

```css
.publicationPostRoot {
  margin-left: auto;
  margin-right: auto;
  padding: 112px 30px 120px;
}

@media (min-width: 1024px) {
  .publicationPostRoot {
    padding: 144px 30px 160px;
  }
}
```

For body/prose areas, patch only the properties the reset invalidates:

```css
.publicationBody :global(h2) {
  margin-top: 2.5rem;
}

.publicationBody :global(ul),
.publicationBody :global(ol) {
  margin-top: 1rem;
  padding-left: 1rem;
}
```

For interactive elements, do not rely on Tailwind utility class presence when a global element rule exists. Add route-local CSS Module classes to the affected element and explicitly restore the computed properties the reference requires:

```tsx
<button
  type="button"
  className={`${styles.shareButton} inline-flex h-10 w-10 items-center justify-center rounded-full border border-[#e5e7eb] text-slate-400`}
>
  <Icon className={`${styles.shareIcon} h-4 w-4`} />
</button>

<Link
  href={`/${locale}/t/company/contact-us`}
  className={`${styles.contactCta} inline-flex w-full items-center justify-center rounded-[6px] bg-[#24292F] text-white`}
>
  Contact Us
</Link>
```

```css
.shareButton {
  border: 1px solid #e5e7eb;
  color: #94a3b8;
}

.shareButton:hover,
.shareButton:focus-visible {
  border-color: #020617;
  color: #020617;
}

.shareIcon {
  width: 16px;
  height: 16px;
}

.contactCta,
.contactCta:hover,
.contactCta:focus-visible {
  color: #ffffff;
}
```

This pattern is especially important for article share buttons and right-sidebar contact CTAs: the visual failure may be a missing border or wrong text/icon color even when layout, size, and class names appear correct.

## Verification probe

Compare exact reference and preview URLs in the browser. For the migrated route, record at least:

- root/html font size
- section computed `padding`, `margin`, `width`, `max-width`, and top offset
- heading/body/sidebar/contact CTA computed margins, padding, border, text color, icon color, and background
- social/share button computed border, color, width/height, icon SVG size, hover/focus state colors
- generated Tailwind rule presence only as supporting evidence, never as final proof

Success means computed values match or intentionally differ. It is not enough that DOM class names match.