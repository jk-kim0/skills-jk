# `/t/platforms/aip` value-card and feature-copy parity notes

Session-specific rendered comparison between:
- stage: `https://stage.querypie.ai/t/platforms/aip`
- live: `https://www.querypie.com/ja/solutions/aip`

Use this as a concrete reference when auditing or fixing QueryPie Japan AIP preview route parity.

## 1. Value cards: visible card height must fill the row

The live AIP `IntroducingQueryPie` value cards render as equal-height cards in one row.
On a 1440px desktop viewport, measured live card wrapper heights were all about `549.63px`:

- `従量課金型の AIモデル`: `549.63px`
- `統合型 AIゲートウェイ`: `549.63px`
- `AI専門家伴走 サービス`: `549.63px`

The stage page rendered the visible white card wrappers at content-dependent heights:

- `従量課金型の AIモデル`: about `485.63px`
- `統合型 AIゲートウェイ`: about `459.63px`
- `AI専門家伴走 サービス`: about `433.64px`

Important diagnosis:
- the stage grid/reveal wrappers may have the row height, but the actual visible card element (`article`, `li`, or equivalent) can still shrink to its content height
- classify this as a parity defect even if the grid track height is equal
- fix the visible card chrome wrapper, not only the outer animation wrapper

Likely implementation direction in corp-web-japan:
- `AipValueCard` is the visible card wrapper in `src/components/sections/aip/page.tsx`
- make it fill the grid row height, for example with `h-full`, if the parent/reveal structure allows it
- if `RevealOnScroll` is the direct grid item, ensure the stretch contract reaches the semantic card wrapper

## 2. Feature rows: copy wrapper geometry is a separate parity target

For AIP feature rows, media width and the `80px` row gap can match while the copy column is still wrong.
Measure the copy wrapper itself, not only the image/media wrapper.

On a 1440px desktop viewport, observed copy wrapper widths:

| Feature | live copy width | stage copy width | delta |
| --- | ---: | ---: | ---: |
| `プロンプト自動生成` | `475.97px` | `417px` | `-59px` |
| `シンプルな統合` | `537.61px` | `380px` | `-158px` |
| `社内文書の学習機能` | `552.77px` | `407px` | `-146px` |
| `カスタムエージェント作成` | `460.81px` | `420px` | `-41px` |
| `ビジュアルレポート作成` | `383.81px` | `383.81px` | `0px` |
| `エージェントスケジューリング` | `420px` | `420px` | `0px` |

The first three stage copy columns were materially narrower and shifted inward compared with live.
That changed paragraph wrapping, copy block height, and the visual balance against media.

Important diagnosis:
- do not conclude a feature row is correct just because media width, row direction, and `gap: 80px` match
- inspect `copy.left`, `copy.top`, `copy.width`, `copy.height`, heading width, and paragraph line count
- route-local guessed values such as `AipFeatureCopy className="max-w-[380px]"` can be the source of the mismatch
- if a reveal wrapper is the flex child, verify whether the semantic copy component or the reveal wrapper owns the measured width

## Browser measurement pattern

```js
(() => {
  const titles = [
    "プロンプト自動生成",
    "シンプルな統合",
    "社内文書の学習機能",
    "カスタムエージェント作成",
    "ビジュアルレポート作成",
    "エージェントスケジューリング",
  ];
  const norm = (value) => (value || "").replace(/\s+/g, " ").trim();
  const rect = (el) => {
    const r = el.getBoundingClientRect();
    return {
      left: Math.round(r.left),
      top: Math.round(r.top + scrollY),
      width: Math.round(r.width),
      height: Math.round(r.height),
      right: Math.round(r.right),
      bottom: Math.round(r.bottom + scrollY),
    };
  };

  return titles.map((title) => {
    const heading = Array.from(document.querySelectorAll("main h2, main h3, main h4")).find(
      (node) => norm(node.textContent) === title
    );
    if (!heading) return { title, missing: true };

    let node = heading;
    const chain = [];
    for (let depth = 0; node && depth < 8; depth += 1, node = node.parentElement) {
      const box = node.getBoundingClientRect();
      if (box.width > 100 && box.height > 20) {
        chain.push({ depth, node, hasImage: Boolean(node.querySelector("img")), rect: rect(node) });
      }
    }

    const row = chain.find(
      (item) => item.hasImage && item.rect.width >= 900 && item.rect.width <= 1220 && item.rect.height >= 250
    )?.node;
    const image = row?.querySelector("img");
    const copy = row ? Array.from(row.children).find((child) => child.contains(heading)) : null;
    const media = row && image ? Array.from(row.children).find((child) => child.contains(image)) : null;

    return {
      title,
      row: row ? rect(row) : null,
      copy: copy ? rect(copy) : null,
      media: media ? rect(media) : null,
      heading: rect(heading),
      paragraph: copy?.querySelector("p") ? rect(copy.querySelector("p")) : null,
    };
  });
})()
```

## Reporting heuristic

For AIP feature/value sections, report separately:
1. media width and lazy-loading status
2. row direction and gap
3. copy wrapper position and size
4. visible card wrapper height
5. whether the measured wrapper is a semantic component or an animation/reveal wrapper

This separation prevents misclassifying copy-column defects as media-size defects or missing-image defects.
