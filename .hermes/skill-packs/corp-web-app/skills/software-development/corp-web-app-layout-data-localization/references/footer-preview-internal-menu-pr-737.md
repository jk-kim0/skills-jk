# Footer preview-only Internal menu pattern

Session pattern from corp-web-app PR #737.

Use this when adding review/internal navigation to the site-wide footer that should only appear while Preview Toggle / preview navigation mode is enabled.

## Current footer authoring shape

- Footer authoring lives in locale-specific TSX modules:
  - `src/components/layout/footer.en.tsx`
  - `src/components/layout/footer.ja.tsx`
  - `src/components/layout/footer.ko.tsx`
- The shared selector is `src/components/layout/footer/ui/footer.component.tsx`.
- `FooterLocaleProps` includes:
  - `currentLocale`
  - `previewModeEnabled`
- Use direct JSX in the locale files for footer copy/link composition. Do not add a JSON registry for this class of footer change.

## Preview-only menu pattern

Append preview-only footer sections at the end of the existing `navigation` fragment so they render as the final footer column.

Example:

```tsx
{props.previewModeEnabled ? (
  <FooterMenuColumn label="Internal" width={105}>
    <FooterMenuLink label="Internal" href={`/${props.currentLocale}/internal`} />
    <FooterMenuLink label="Archived" href={`/${props.currentLocale}/archived`} />
    <FooterMenuLink label="Preview" href={`/${props.currentLocale}/internal/preview`} />
  </FooterMenuColumn>
) : null}
```

Use explicit locale-prefixed internal URLs when the destination itself is locale-scoped internal infrastructure. Do not pass these through `footerHref()` unless you specifically want preview-route rewriting behavior.

## Verification pattern

Add a colocated shell-group source test under:

- `src/components/layout/footer/__tests__/...test.ts`

Useful assertions:

- each locale footer source contains `props.previewModeEnabled ?`
- `Internal` appears after the existing `Plans` column
- required locale-prefixed links are present in the TSX source

Run targeted verification:

```bash
npx vitest run src/components/layout/footer/__tests__/<test-name>.test.ts
node scripts/ci/assert-test-groups.mjs
```

The test group matcher already includes `src/components/layout/**` in the `shell` group, so colocated footer tests should be assigned automatically.
