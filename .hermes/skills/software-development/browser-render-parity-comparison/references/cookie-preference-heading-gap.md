# Cookie preference H1/lead gap parity case

Session context: corp-web-app `/ko/cookie-preference` stage vs production visual mismatch between the main H1 and lead description.

Observed browser geometry at desktop viewport:

- Stage: H1 bottom `240px`, lead top `240px` -> gap `0px`.
- Production: H1 bottom `240px`, lead top `260px` -> gap `20px`.

Useful probe pattern:

```js
() => {
  window.scrollTo(0, 0);
  const h1 = document.querySelector('h1');
  const lead = Array.from(document.querySelectorAll('p')).find(p =>
    p.textContent.includes('저희는') || p.className.includes('StaticHeader'),
  );
  const h1Rect = h1.getBoundingClientRect();
  const leadRect = lead.getBoundingClientRect();
  return {
    h1: { top: h1Rect.top, bottom: h1Rect.bottom, height: h1Rect.height, className: h1.className },
    lead: { top: leadRect.top, bottom: leadRect.bottom, height: leadRect.height, className: lead.className },
    gap: leadRect.top - h1Rect.bottom,
    h1Parent: h1.parentElement?.className,
  };
}
```

Root cause pattern:

- The target/stage route used a plain `<section>` around `<StaticH1>` and `<StaticHeader>`, so the two block elements had no internal gap.
- The production/reference structure used the shared `Box`/layout primitive with `direction="column" gapSize="sm"`, producing a 20px gap.

Fix pattern:

```tsx
import Box from 'src/components/foundation/layout/box.component';

<Box as="section" direction="column" gapSize="sm">
  <StaticH1>...</StaticH1>
  <StaticHeader color="var(--text-body)">...</StaticHeader>
</Box>
```

Apply across locale siblings when the page family is locale-specific (`page.en.tsx`, `page.ko.tsx`, `page.ja.tsx`) so parity remains consistent and locale copy is not accidentally changed.

Pitfall:

- When patching multiple locale files, keep translated H1/copy unchanged. A broad replace can accidentally change JA/KO text while only intending layout parity.
