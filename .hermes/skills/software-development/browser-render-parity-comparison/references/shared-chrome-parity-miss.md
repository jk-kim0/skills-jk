# Shared chrome parity miss: header/footer looked close but was not equivalent

Context: a corp-web-app Tailwind route-group chrome update initially made header/footer appear broadly similar to the legacy `/company/about-us` page, but a later screenshot review found concrete mismatches.

Missed differences:

- Header language control used the wrong icon identity: a rotated GNB arrow instead of the legacy globe/language icon.
- Header `Free Now` CTA had the same broad gradient but missed the legacy chevron, used a different font weight, and therefore had different visual width/feel.
- Footer social links rendered only three icons instead of the legacy five-icon set: LinkedIn, Youtube, X, Facebook, Instagram.
- Footer/logo area looked superficially close because the dark background and white logo were present, but the social-link inventory still failed parity.

Reusable lesson:

Do not treat shared chrome as passed after checking only that header/footer are present and screenshots look broadly similar. Build a header/footer-specific inventory and compare exact icon identity, link count/order, aria labels, hrefs, SVG/viewBox, nested CTA structure, chevron/icon presence, font weight, spacing, and computed dimensions.

Recommended probe shape:

- Capture synchronized screenshots of the reference and target.
- For `header`, collect logo anchor/SVG rect, language/search/tool icons, CTA anchor, CTA text span, CTA icon/SVG, and computed `fontFamily`, `fontSize`, `lineHeight`, `fontWeight`, `color`, `background`, `padding`, `gap`, and `borderRadius`.
- For `footer`, collect logo SVG, social anchors filtered by aria-label, social icon SVG dimensions/viewBox, footer columns, legal links, address block, and computed padding/background/borders.
- Compare the source contract as well: whether the Tailwind/shared chrome uses the same underlying icon components or intentionally equivalent replacements.

Good completion statement:

- Report both screenshot evidence and exact DOM/source deltas.
- If a mismatch is found after an earlier PR, update the governing parity skill or reference immediately so the next chrome parity pass starts with this checklist.