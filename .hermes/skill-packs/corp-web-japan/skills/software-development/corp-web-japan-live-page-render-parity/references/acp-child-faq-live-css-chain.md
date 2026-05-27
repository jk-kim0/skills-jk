# ACP child FAQ live CSS-chain parity note

## Trigger

Use this note when a corp-web-japan ACP child page under `/platforms/acp/{database-access-controller,system-access-controller,kubernetes-access-controller,web-access-controller}` visually differs from the live QueryPie Japan reference in the FAQ/bottom section.

## Lesson

For these pages, `corp-web-contents` is not enough to recover the FAQ UI. The MDX page body only declares:

```yaml
layout: "WithFAQBottomLayout"
```

The concrete live FAQ rendering contract lives in `corp-web-app`, not in the MDX body.

## Source chain to inspect

Quick rule: when MDX only declares a `layout`, inspect the app renderer and widget/CSS chain before rebuilding the UI locally. Do not stop at text parity or MDX frontmatter parity.

1. `../corp-web-contents/pages/solutions/acp/<route>/ja/content.mdx`
   - Confirms `layout: "WithFAQBottomLayout"`.
2. `../corp-web-app/src/app/dynamic-page.tsx`
   - Wraps matching frontmatter layouts with `<FAQBottom data={faqBottomData} />`.
3. `../corp-web-app/src/components/layout/bottom/faq-bottom.component.tsx`
   - Renders `<CenterSection className={styles.section}>` and `<QnA items={data.list} />`.
4. `../corp-web-app/src/components/layout/bottom/faq-bottom.module.css`
   - Sets FAQ section padding: `var(--rem-120px) 0 var(--rem-200px) 0`.
5. `../corp-web-app/src/components/widget/qna/qna.component.tsx`
   - Renders closed-by-default `<details>` rows with `<summary>` and answer text.
6. `../corp-web-app/src/components/widget/qna/qna.module.css`
   - Owns the row borders, summary flex layout, plus/minus `summary::after` icons, summary padding, and answer typography.

## Live contract captured from WAC comparison

Live URL checked:
`https://www.querypie.com/ja/solutions/acp/web-access-controller`

Important computed styles:

- `details.open`: `false` by default
- FAQ section padding: `120px 0 200px`
- summary:
  - `display: flex`
  - `justify-content: space-between`
  - `align-items: center`
  - `gap: 10px`
  - `padding: 10px 20px 20px 0`
  - `font-size: 20px`
  - `font-weight: 500`
  - `line-height: 28px`
  - `color: #24292f`
- summary icon:
  - `summary::after` has a 24px data-URI plus icon when closed
  - `details[open] summary::after` switches to a 24px minus icon
- row borders:
  - first row top border: `1px solid #353c45`
  - row separators: `1px solid #dae1e7`
- opened answer typography:
  - `margin-top: 20px`
  - `font-size: 16px`
  - `font-weight: 300`
  - `line-height: 26px`
  - `letter-spacing: 0.36px`
  - `color: #57606a`

## Failure pattern observed

A local implementation can look plausible but still be wrong when it:

- hardcodes FAQ text directly from JSON/MDX but misses the upstream widget CSS
- renders every `<details>` row as `open`
- uses plain browser `summary` rendering without the plus/minus icon
- uses `border-y` on the whole list instead of the first-row dark top border plus light row separators
- uses `100px` vertical section padding instead of `120px 0 200px`
- validates only text presence rather than `details.open`, `summary::after`, borders, and padding

## Recommended check

For FAQ parity, collect browser computed style from both live and stage for:

```js
const d = [...document.querySelectorAll('details')]
  .find((node) => node.textContent.includes('QueryPie'));
const summary = d.querySelector('summary');
const section = d.closest('section');
const li = d.closest('li');

({
  open: d.open,
  sectionPadding: getComputedStyle(section).padding,
  liBorderTop: getComputedStyle(li).borderTop,
  liBorderBottom: getComputedStyle(li).borderBottom,
  summary: {
    display: getComputedStyle(summary).display,
    justifyContent: getComputedStyle(summary).justifyContent,
    padding: getComputedStyle(summary).padding,
  },
  summaryAfter: {
    content: getComputedStyle(summary, '::after').content,
    width: getComputedStyle(summary, '::after').width,
    height: getComputedStyle(summary, '::after').height,
    backgroundImage: getComputedStyle(summary, '::after').backgroundImage,
  },
});
```

If answers are hidden on live, explicitly open one row only for a second answer-typography pass; do not compare hidden answer geometry as if it were visible.
