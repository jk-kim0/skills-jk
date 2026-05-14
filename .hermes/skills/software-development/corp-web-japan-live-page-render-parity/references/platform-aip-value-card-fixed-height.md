# `/t/platforms/aip` value-card fixed-height parity

Session-specific finding from comparing:
- stage: `https://stage.querypie.ai/t/platforms/aip`
- live: `https://www.querypie.com/ja/solutions/aip`

## What was observed

The live AIP value-card row renders three cards at the same visible card-wrapper height on desktop:

- `従量課金型の AIモデル`: about `549.63px`
- `統合型 AIゲートウェイ`: about `549.63px`
- `AI専門家伴走 サービス`: about `549.63px`

The stage page rendered the visible `AipValueCard` `<article>` wrappers at content-dependent heights:

- `従量課金型の AIモデル`: about `485.63px`
- `統合型 AIゲートウェイ`: about `459.63px`
- `AI専門家伴走 サービス`: about `433.64px`

The grid row / reveal wrapper still had the tallest row height, but the actual white card chrome did not fill that row. This made card bottoms and `詳細を見る` rows visibly misaligned.

## Diagnostic lesson

For card-grid parity, do not only measure the grid wrapper. Measure the element that owns the visible card chrome:

- white background
- border radius
- overflow clipping
- shadow
- body padding
- bottom/action row

In this case, the relevant stage element was the `AipValueCard` `<article>`, not only the grid item or reveal wrapper around it.

## Useful measurement snippet

```js
(() => {
  const valueImages = Array.from(document.querySelectorAll("main img")).filter((img) =>
    /従量課金型|統合型|AI専門家伴走/.test((img.alt || "").replace(/\s+/g, ""))
  );

  return valueImages.map((img) => {
    let el = img;
    const chain = [];
    for (let depth = 0; el && depth < 8; depth += 1, el = el.parentElement) {
      const r = el.getBoundingClientRect();
      chain.push({
        depth,
        tag: el.tagName.toLowerCase(),
        className: String(el.className || ""),
        width: Math.round(r.width),
        height: Math.round(r.height),
        text: (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 80),
        display: getComputedStyle(el).display,
        alignSelf: getComputedStyle(el).alignSelf,
      });
    }
    return { alt: img.alt, chain };
  });
})()
```

## Fix direction

When live uses equal-height cards, make the visible card wrapper fill the equal-height grid track.

Common fix candidates:

- add `h-full` or equivalent to the actual card wrapper (`article`, `li`, etc.)
- ensure any animation/reveal wrapper between the grid and card also allows full-height stretch
- keep the bottom link/action row using `mt-auto` after the card itself fills the row

Avoid fixing only the outer grid height; that can leave the visible card chrome content-height dependent.

## Reporting classification

Classify this as a major visual-parity defect when:

- live card wrappers are equal-height,
- stage/preview visible card wrappers are different heights,
- card bottoms or action rows no longer align,
- text content is otherwise present and correct.
