# Corp-web-app live metric parity: certifications page

Use this as a concrete example when a migrated/static verification page looks close but has subtle typography, image, or line-spacing drift from the live public page.

## Scenario

Reference URL:
- `https://www.querypie.com/ko/company/certifications`

Target pattern:
- Preview deployment route such as `https://<vercel-preview>/ko/t/company/certifications`

The page had apparently minor differences that were only obvious after measuring rendered output:
- H1 size/line-height/letter-spacing drifted from the live page.
- Certification card/icon dimensions were slightly scaled down.
- A two-line CTA heading was rendered as one heading with `<br />`, producing different line rhythm from the live page's two stacked headings.

## Measurement probe pattern

Measure both pages in the same browser viewport and compare computed styles/geometry for these landmarks:

```js
() => {
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const rect = el => {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return {
      tag: el.tagName.toLowerCase(),
      text: norm(el.textContent).slice(0, 180),
      top: Math.round((r.top + scrollY) * 100) / 100,
      left: Math.round(r.left * 100) / 100,
      width: Math.round(r.width * 100) / 100,
      height: Math.round(r.height * 100) / 100,
      bottom: Math.round((r.bottom + scrollY) * 100) / 100,
      fontSize: cs.fontSize,
      lineHeight: cs.lineHeight,
      fontWeight: cs.fontWeight,
      letterSpacing: cs.letterSpacing,
      textAlign: cs.textAlign,
      marginTop: cs.marginTop,
      marginBottom: cs.marginBottom,
      paddingTop: cs.paddingTop,
      paddingBottom: cs.paddingBottom,
      transform: cs.transform,
      display: cs.display,
    };
  };

  const h1 = [...document.querySelectorAll('h1')]
    .find(el => norm(el.textContent).includes('Certifications'));
  const lead = [...document.querySelectorAll('p')]
    .find(el => norm(el.textContent).includes('QueryPie는 항상 앞서'));
  const cards = [...document.querySelectorAll('article, li')]
    .filter(el => norm(el.textContent).includes('SOC 2 Type II') || norm(el.textContent).includes('CSA-STAR'));
  const imgs = cards.slice(0, 3).map(card => {
    const img = card.querySelector('img, svg');
    return { card: rect(card), img: rect(img), attr: img && { src: img.getAttribute('src'), style: img.getAttribute('style'), width: img.getAttribute('width'), height: img.getAttribute('height') } };
  });
  const trustHeadings = [...document.querySelectorAll('h2,h3')]
    .filter(el => norm(el.textContent).includes('Want to dive') || norm(el.textContent).includes('compliance details'));

  return {
    page: { url: location.href, innerWidth, rootFontSize: getComputedStyle(document.documentElement).fontSize },
    h1: rect(h1),
    lead: rect(lead),
    h1ToLeadGap: h1 && lead ? Math.round((lead.getBoundingClientRect().top - h1.getBoundingClientRect().bottom) * 100) / 100 : null,
    imgs,
    trustHeadings: trustHeadings.map(rect),
    trustGap: trustHeadings.length > 1 ? Math.round((trustHeadings[1].getBoundingClientRect().top - trustHeadings[0].getBoundingClientRect().bottom) * 100) / 100 : null,
  };
}
```

## Example target values from the live page

At a desktop viewport around 1440 CSS px wide (Chrome window reported `innerWidth` around 1555 in this session), the live page measured:

- H1: `font-size: 60px`, `line-height: 72px`, `font-weight: 400`, `letter-spacing: normal`, left aligned.
- Lead paragraph: `font-size: 18px`, `line-height: 28px`, `font-weight: 300`, `letter-spacing: 0.36px`, H1-to-lead gap `20px`.
- First certification cards: `380px x 400px`.
- First icon/SVG badges: `120px x 120px` for SOC/CSA icons.
- CTA heading lines: two separate `h3` elements, each `40px / 48px`, with `20px` vertical gap.

## Durable lesson

For corp-web-app parity migrations, do not rely on visually similar copied values from corp-web-japan or on approximate scaled values such as `37.5px`, `112.5px`, or `9.375px` when the target is parity with an existing live `querypie.com` page. Measure the live page and match the source-owning shared primitives/components to those computed values.

If the live page uses two stacked headings to create a line gap, preserving that DOM structure can matter; replacing it with one heading and `<br />` may change line rhythm even when the visible text is identical.
