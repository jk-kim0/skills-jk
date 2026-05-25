# Chrome-specific parity probe

Use this reference when a task compares shared header/footer chrome between a reference page and a target page. The goal is to avoid accepting broad visual similarity when exact chrome contracts differ.

## Required method

1. Run the same probe on both pages at the same viewport width after `window.scrollTo(0, 0)`.
2. Compare the resulting JSON field-by-field before editing.
3. Treat missing or extra chrome controls as parity failures even when the overall screenshot looks similar.
4. After fixing source, re-run the probe on the final deployed or preview URL; do not rely only on source inspection.

## Probe

Run in DevTools / Browser MCP / Playwright evaluate:

```js
() => {
  const norm = value => (value || '').replace(/\s+/g, ' ').trim();
  const rect = el => {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {
      x: Math.round(r.x * 100) / 100,
      y: Math.round(r.y * 100) / 100,
      width: Math.round(r.width * 100) / 100,
      height: Math.round(r.height * 100) / 100,
      top: Math.round((r.top + scrollY) * 100) / 100,
      bottom: Math.round((r.bottom + scrollY) * 100) / 100,
    };
  };
  const style = el => {
    if (!el) return null;
    const cs = getComputedStyle(el);
    return {
      display: cs.display,
      position: cs.position,
      fontFamily: cs.fontFamily,
      fontSize: cs.fontSize,
      lineHeight: cs.lineHeight,
      fontWeight: cs.fontWeight,
      letterSpacing: cs.letterSpacing,
      color: cs.color,
      background: cs.background,
      backgroundColor: cs.backgroundColor,
      border: cs.border,
      borderColor: cs.borderColor,
      borderRadius: cs.borderRadius,
      boxShadow: cs.boxShadow,
      padding: cs.padding,
      margin: cs.margin,
      gap: cs.gap,
    };
  };
  const svgInfo = svg => {
    if (!svg) return null;
    const paths = [...svg.querySelectorAll('path')].map(path => ({
      d: path.getAttribute('d'),
      fillAttr: path.getAttribute('fill'),
      strokeAttr: path.getAttribute('stroke'),
      fill: getComputedStyle(path).fill,
      stroke: getComputedStyle(path).stroke,
    }));
    return {
      rect: rect(svg),
      viewBox: svg.getAttribute('viewBox'),
      className: String(svg.getAttribute('class') || ''),
      fill: getComputedStyle(svg).fill,
      stroke: getComputedStyle(svg).stroke,
      paths,
    };
  };
  const pick = el => {
    if (!el) return null;
    return {
      tag: el.tagName.toLowerCase(),
      text: norm(el.textContent),
      ariaLabel: el.getAttribute('aria-label'),
      href: el.href || el.getAttribute('href'),
      type: el.getAttribute('type'),
      className: String(el.className || ''),
      rect: rect(el),
      style: style(el),
      svg: svgInfo(el.querySelector('svg')),
    };
  };

  const header = document.querySelector('header');
  const footer = document.querySelector('footer');
  const headerLinks = [...document.querySelectorAll('header a')];
  const headerButtons = [...document.querySelectorAll('header button')];
  const footerLinks = [...document.querySelectorAll('footer a')];
  const findText = (els, text) => els.find(el => norm(el.textContent).includes(text));
  const findLabel = (els, pattern) => els.find(el => pattern.test(el.getAttribute('aria-label') || ''));
  const socialPattern = /LinkedIn|Youtube|YouTube|X|Twitter|Facebook|Instagram|GitHub|Discord/i;

  const headerCta = findText(headerLinks, 'Free Now') || findText(headerLinks, 'Contact Us') || findText(headerLinks, 'Make It Happen');
  const languageControl = findLabel([...headerButtons, ...headerLinks], /language|locale|日本語|한국어|English|언어/i);
  const searchControl = findLabel([...headerButtons, ...headerLinks], /search|검색/i);
  const menuControl = findLabel(headerButtons, /menu|hamburger|navigation/i);
  const headerLogo = findLabel(headerLinks, /home|go home/i) || header?.querySelector('a');
  const footerLogo = footer?.querySelector('svg');

  return {
    page: {
      url: location.href,
      title: document.title,
      viewport: { width: innerWidth, height: innerHeight },
      scrollY,
      rootFontSize: getComputedStyle(document.documentElement).fontSize,
      body: { rect: rect(document.body), style: style(document.body) },
    },
    header: {
      container: pick(header),
      logo: pick(headerLogo),
      navItems: [...document.querySelectorAll('header nav a, header nav button')].map(pick),
      languageControl: pick(languageControl),
      searchControl: pick(searchControl),
      menuControl: pick(menuControl),
      cta: pick(headerCta),
      ctaText: headerCta ? pick([...headerCta.querySelectorAll('span')].find(span => norm(span.textContent))) : null,
      ctaIcons: headerCta ? [...headerCta.querySelectorAll('svg')].map(svgInfo) : [],
    },
    footer: {
      container: pick(footer),
      logoSvg: svgInfo(footerLogo),
      socialLinks: footerLinks.filter(a => socialPattern.test(a.getAttribute('aria-label') || norm(a.textContent))).map(pick),
      navColumns: [...document.querySelectorAll('footer nav > ul > li')].map(column => ({
        text: norm(column.textContent),
        rect: rect(column),
        style: style(column),
        links: [...column.querySelectorAll('a')].map(pick),
      })),
      legalLinks: footerLinks.filter(a => /Cookie|Terms|Privacy|EULA|쿠키|개인정보/i.test(norm(a.textContent))).map(pick),
      addressText: norm(footer?.textContent).match(/(©|Headquarter|Seoul|Japan|Tokyo|Los Angeles).*/s)?.[0] || '',
    },
  };
}
```

## What to compare

### Header

- Header height, position, z-index/shadow, background, and wrapper max-width/gutters.
- Logo link href, SVG viewBox, displayed dimensions, and fill color.
- Navigation item labels, order, dropdown trigger state, and dropdown surface geometry.
- Language/search/menu controls by icon identity, not just size. Compare SVG `viewBox` and representative path `d` values.
- CTA structure: wrapper, text span, icon span/SVG, href, width/height, padding, gap, font weight, border radius, normal/hover/focus backgrounds.

### Footer

- Footer background, padding, wrapper width, borders, and section order.
- Logo SVG identity, dimensions, and color.
- Social links exact count, order, labels, hrefs, SVG viewBox/path identity, icon color, icon size, and spacing.
- Navigation column labels, link labels/order, link wrapping, column widths/gaps, legal links, and address/copyright text.

## Failure examples

These are parity failures even if screenshots look broadly similar:

- The target uses a rotated chevron/arrow where the reference uses a globe language icon.
- The target CTA has the same gradient but omits the chevron icon.
- The target CTA text computes to a different font weight or the icon path fill differs.
- The target footer has three social icons when the reference has five.
- The target social link has the same visual glyph but a different href or aria-label.
- Header/footer dimensions match at desktop but break in tablet/mobile breakpoint bands.
