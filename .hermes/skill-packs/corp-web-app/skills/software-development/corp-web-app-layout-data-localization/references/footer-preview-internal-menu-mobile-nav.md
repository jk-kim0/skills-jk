# Footer preview Internal menu mobile nav regression

## Context

In corp-web-app, a preview-only footer `Internal` menu section was added to the locale-authored footer modules:

- `src/components/layout/footer.en.tsx`
- `src/components/layout/footer.ja.tsx`
- `src/components/layout/footer.ko.tsx`

The section was intentionally appended as the last footer navigation column and rendered only when `props.previewModeEnabled` is true. It linked:

- `Internal` -> `/{locale}/internal`
- `Archived` -> `/{locale}/archived`
- `Preview` -> `/{locale}/internal/preview`

## Symptom

The user reported that the footer content disappeared at mobile device widths even though it appeared on desktop.

## Root cause

The new `Internal` section lived inside the footer navigation `<nav className={styles.nav}>`. Existing CSS hid the entire footer nav on tablet/mobile:

```css
@media (max-width: 1260px) {
    .nav {
        display: none;
    }
}
```

So the bug was not in the conditional JSX; it was a responsive CSS contract mismatch. Desktop inspection alone was insufficient.

## Fix pattern

Keep footer navigation visible on narrower widths and adapt the list layout instead:

```css
@media (max-width: 1260px) {
    .nav > ul {
        flex-wrap: wrap;
        gap: var(--rem-40px) var(--rem-60px);
    }
}

@media (max-width: 920px) {
    .nav > ul {
        flex-direction: column;
        gap: var(--rem-32px);
        padding: var(--rem-32px) 0 var(--rem-40px) 0;
    }
}
```

Tune exact spacing to the current design system, but avoid restoring `display: none` when footer links are expected on mobile.

## Regression test pattern

Add a source-level test under the layout/footer test family that checks both the preview-only menu and the responsive CSS guard:

```ts
const readFooterStyles = () => {
  return readFileSync(join(layoutDirectory, 'footer/ui/footer.module.css'), 'utf8');
};

it('keeps footer navigation visible and stacked on mobile widths', () => {
  const styles = readFooterStyles();

  expect(styles).not.toContain('.nav {\n        display: none;');
  expect(styles).toContain('flex-wrap: wrap;');
  expect(styles).toContain('flex-direction: column;');
});
```

Then run the narrow test and test-group assertion:

```bash
npx vitest run src/components/layout/footer/__tests__/footer-preview-internal-menu.test.ts
node scripts/ci/assert-test-groups.mjs
```

## PR workflow note

If the initial PR has already been pushed, amend the same PR branch rather than creating a new PR for this responsive follow-up. Update the PR body so it mentions the mobile footer nav fix and the added regression coverage.
