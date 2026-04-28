---
name: corp-web-japan-production-inline-link-parity
description: Align corp-web-japan publication/article inline text links with the production querypie.com/ja behavior, including color policy, strong-inside-link handling, and link-only hover/focus underlines.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Corp Web Japan: production-style inline text link parity

Use this when article or publication body links in `corp-web-japan` should match the production `querypie.com/ja` reading UX rather than generic blue-underlined blog styling.

## When to use

- A user says inline text links in blog/article body should match production
- Some inline links appear blue while others appear black
- `strong` inside links causes inconsistent color/weight
- Hovering the paragraph/container causes all nested links to underline instead of only the hovered link

## Core findings

### 1. Production does NOT use generic blue inline links for most article references
On production `querypie.com/ja` article pages:
- most inline reference links render in body text color
- most do not show underline by default
- only some self-promotional / next-action style links are blue + underlined

So the safest parity baseline for publication/article body copy is:
- default inline link color = body text color
- default inline link underline = none
- hover/focus-visible = underline for affordance

### 2. `strong` inside a link can override the link styling
If the article body uses rules like:
- `[&_a]:text-...`
- `[&_strong]:text-slate-950`

then markup such as:
- `<a ...><strong>NIST ...</strong></a>`

will appear differently from:
- `<a ...>JFrog ...</a>`

because the nested `strong` overrides the anchor styling.

Fix this by adding link-scoped inheritance rules such as:
- `[&_a_strong]:font-inherit`
- `[&_a_strong]:text-inherit`

This keeps link-wrapped strong text visually aligned with the surrounding link treatment.

### 3. Do NOT use container-hover arbitrary variants for this affordance
This pattern is wrong for article body links:
- `hover:[&_a]:underline`

Why it fails:
- it responds to hover on the container/paragraph block
- moving the pointer anywhere inside the paragraph can underline the nested link
- users see underlines even when not directly hovering the link

Use link-element hover/focus selectors instead:
- `[&_a:hover]:underline`
- `[&_a:focus-visible]:underline`

This ensures only the hovered/focused link gets the underline.

## Recommended implementation in `src/components/PublicationPostPage.tsx`

For the publication body class list, prefer a rule shaped like:

```tsx
"[&_a]:font-inherit [&_a]:text-slate-950 [&_a]:no-underline [&_a:hover]:text-slate-950 [&_a:hover]:underline [&_a:hover]:decoration-[1px] [&_a:hover]:underline-offset-[3px] [&_a:focus-visible]:underline [&_a:focus-visible]:decoration-[1px] [&_a:focus-visible]:underline-offset-[3px]"
```

And keep strong inside links from breaking parity:

```tsx
"[&_strong]:font-medium [&_strong]:text-slate-950 [&_a_strong]:font-inherit [&_a_strong]:text-inherit"
```

## Verification workflow

### Source-level regression test
Add a focused test that checks for:
- default body-color links
- no default underline
- `a:hover` underline rules
- `a:focus-visible` underline rules
- no generic blue article-link rule
- `a strong` inheritance rules

Example assertions:

```js
assert.match(source, /\[&_a\]:text-slate-950/);
assert.match(source, /\[&_a\]:no-underline/);
assert.match(source, /\[&_a:hover\]:underline/);
assert.match(source, /\[&_a:focus-visible\]:underline/);
assert.match(source, /\[&_a_strong\]:font-inherit/);
assert.match(source, /\[&_a_strong\]:text-inherit/);
assert.doesNotMatch(source, /\[&_a\]:text-\[#2563EB\]/);
```

### Browser verification
Open a production-parity article page such as `/blog/28/...` and confirm:
- non-hover computed `textDecorationLine` is `none`
- body reference links like `JFrog Security Research報告` and `NIST ...` use the same body-color link treatment
- hovering the paragraph/container but NOT the link does not underline the link
- hovering the link itself does underline it

Useful browser console probe:

```js
(() => {
  const a = Array.from(document.querySelectorAll('main a[href^="http"]'))
    .find(el => (el.textContent || '').includes('JFrog'));
  const s = getComputedStyle(a);
  return {
    text: a.textContent.trim(),
    color: s.color,
    textDecorationLine: s.textDecorationLine,
  };
})()
```

## Pitfalls

- Assuming production uses blue inline links everywhere
- Leaving `[&_strong]:text-slate-950` without compensating `a strong` inheritance
- Using `hover:[&_a]:underline` and accidentally triggering underline from paragraph hover
- Treating related-content cards and inline text links as the same UX surface

## Scope note

This skill is for inline text links inside article/publication body copy.
It should not automatically be applied to:
- CTA buttons
- related-content cards
- footer nav links
- header nav links

Those surfaces should keep their own interaction model.
