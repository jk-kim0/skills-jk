---
name: corp-web-japan-live-page-render-parity
description: Match a corp-web-japan preview/static page to a live reference page by comparing actual browser-rendered geometry, screenshots, and asset sizing instead of relying only on source code or text snapshots.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, browser, visual-parity, preview, static-pages, vercel, nextjs]
    related_skills: [existing-pr-followup-worktree, nextjs-local-preview-locks, corp-web-japan-static-page-convention-refactor]
---

# corp-web-japan live-page render parity workflow

Use this when the user says a local/preview corp-web-japan page should *look the same* as a live reference page, especially for static marketing/company pages like `/about-us`, and wants the rendered content body aligned rather than merely the text copied.

## Why this skill exists

For page-parity work, code inspection alone is not enough.

Reference notes:
- `references/about-us-parity-pitfalls.md` — concrete `/about-us` pitfalls for CTA-width interpretation and mixed-width team-card measurement.
- `references/pr-preview-stage-render-audit-pattern.md` — reusable pattern for auditing a PR Preview Deployment against `stage.querypie.ai` across affected routes using Playwright geometry, screenshot pixel diffs, and wrapper padding/gutter root-cause analysis.
- `references/certifications-mobile-gutter-audit.md` — concrete `/certifications` narrow-mobile gutter/card-width audit showing how `px-[30px]` behaves at 300/320/360/390px and when to prefer a card-gallery gutter preset.
- `references/platform-aip-hero-spacing-parity.md` — concrete `/t/platforms/aip` measurement showing how to distinguish header-to-H1 top offset from already-correct intra-hero rhythm, and why `PlatformPageSection` should own the family top offset.
- `references/platform-aip-mobile-overflow-parity.md` — concrete `/t/platforms/aip` desktop-vs-mobile comparison showing how desktop parity can hide mobile overflow: fixed 540–600px feature media plus non-stacking flex rows squeezed mobile text into 30px columns.
- `references/platform-aip-value-card-and-feature-copy-parity.md` — concrete `/t/platforms/aip` value-card equal-height and AipFeatureCopy width/placement parity measurements from stage-vs-live browser comparison.
- `references/aip-self-hosted-hero-video-pattern.md` — concrete `/t/platforms/aip` note for replacing the current YouTube hero iframe with QueryPie-hosted media while preserving the measured hero wrapper geometry.
- `references/platform-aip-value-card-fixed-height.md` — concrete `/t/platforms/aip` value-card row-height audit showing why the visible card wrapper, not only the grid/reveal wrapper, must fill the equal-height grid track.
- `references/platform-aip-parity-implementation-pattern.md` — concrete `/t/platforms/aip` implementation pattern for turning browser findings into a PR: mobile-stacked feature rows, mobile-fluid/desktop-fixed media via CSS variables, reveal wrapper width/height contracts, route-local feature copy widths, and equal-height value cards.
- `references/platform-preview-mobile-parity-batch.md` — concrete multi-page `/t/platforms/**` and `/t/services/fde` mobile parity batch notes: split one PR per page, batch stage-vs-live evidence collection, use `scrollWidth/clientWidth` to catch overflow, keep desktop-correct geometry stable, and apply mobile-first hero/feature-row fixes.
- `references/plans-widget-source-contract-parity.md` — concrete `/t/plans` failure mode showing why source-backed widget/application-contract pages should preserve the upstream component/CSS contract instead of being manually reinterpreted as local Tailwind primitives.

Important findings from real usage:
- Browser text snapshots can claim the structure is correct while the rendered layout still differs materially.
- Vision summaries can misread sparse/long pages and sometimes describe empty areas incorrectly.
- The most reliable method is to combine:
  1. actual browser navigation to both URLs,
  2. screenshots,
  3. DOM geometry from `getBoundingClientRect()`,
  4. measured image sizes/positions,
  5. local preview verification on the exact branch/worktree.
- For PR follow-up visual fixes, the exact Vercel preview deployment URL can be a more trustworthy final reference than local dev, because the preview may render spacing rhythm differently enough for users to notice.
- In particular, heading-spacing parity can fail if you optimize only against local dev measurements; always re-open the exact preview URL the user is looking at before concluding the spacing is fixed.
- `next start` / local preview can serve stale output if you forget to rebuild or restart after changes.
- Old background-process watchers can emit delayed `localhost:3456` notifications long after that specific process was killed; always inspect current process state rather than trusting delayed system notifications.

## When to use

Use this when the user says things like:
- "실제 렌더링 결과를 보고 live와 동일하게 맞춰줘"
- "스크린샷 기준으로 차이가 나지 않게 해줘"
- "layout, style 을 동일하게 맞춰줘"
- "브라우저에서 열어보고 visual parity 맞춰줘"

Especially applicable when:
- the target page is a static route like `/t/about-us`
- a live page exists at `querypie.com` or `stage.querypie.ai`
- the user cares about the *content body area* more than implementation details

## Core workflow

### 1. Compare the exact requested URLs first
Do not substitute a redirected/canonical variant unless the user asked for that.

Open:
- the exact live/reference URL
- the exact preview/local/Vercel URL

Important follow-up rule learned in PR review work:
- If the user points at a specific Vercel preview deployment URL and says the spacing/layout still looks wrong there, treat that exact preview deployment as the final rendering truth for the current review cycle.
- Do not assume a locally served `localhost` page is sufficient evidence that the problem is fixed.
- When local and preview differ, adjust based on the exact preview URL the user is reviewing, then push and wait for the refreshed preview.

Capture:
- title
- main content text snapshot
- screenshots
- DOM geometry for key sections

### 2. Use screenshots, but do not trust vision alone
Use `browser_vision()` to get a quick section-order/layout summary, but treat it as provisional.

Important lesson:
- On long pages with lots of whitespace, vision can misread the page as "mostly empty" even when the DOM contains the intended sections.
- When vision and DOM disagree, trust the DOM + browser console measurements.

### 3. Measure real geometry in the browser console
For parity work, always extract measured positions/sizes for the exact body elements you care about.

Useful patterns:

#### Headings / anchors
```js
Array.from(document.querySelectorAll('main h1, main h2, main h3, main h4, main h5, main h6')).map((h) => {
  const r = h.getBoundingClientRect();
  return {
    text: h.textContent?.trim(),
    left: Math.round(r.left),
    top: Math.round(r.top + window.scrollY),
    width: Math.round(r.width),
    height: Math.round(r.height),
  };
});
```

#### Images / logos / maps
```js
Array.from(document.querySelectorAll('main img')).map((img) => {
  const r = img.getBoundingClientRect();
  return {
    alt: (img.getAttribute('alt') || '').trim(),
    src: img.currentSrc || img.src,
    left: Math.round(r.left),
    top: Math.round(r.top + window.scrollY),
    w: Math.round(r.width),
    h: Math.round(r.height),
  };
});
```

#### Section boxes
```js
Array.from(document.querySelectorAll('main section')).map((s, i) => {
  const r = s.getBoundingClientRect();
  const cs = getComputedStyle(s);
  return {
    i,
    top: Math.round(r.top + window.scrollY),
    h: Math.round(r.height),
    w: Math.round(r.width),
    bg: cs.backgroundColor,
    pt: cs.paddingTop,
    pb: cs.paddingBottom,
    text: (s.innerText || '').trim().slice(0, 30),
  };
});
```

#### Links / CTA positions
```js
Array.from(document.querySelectorAll('main a')).map((a) => {
  const r = a.getBoundingClientRect();
  return {
    text: (a.textContent || '').trim(),
    left: Math.round(r.left),
    top: Math.round(r.top + window.scrollY),
    w: Math.round(r.width),
    h: Math.round(r.height),
  };
});
```

### 4. Verify local preview correctness before trusting it
If using a local preview server:
- do not assume `localhost:3456` is serving the latest build
- do not assume an existing server belongs to your current worktree state

Required checks:
- inspect listener with `lsof -nP -iTCP:<port> -sTCP:LISTEN`
- if the page serves stale content or 404s on the intended route, kill the existing process
- rebuild if using `next start`
- restart the preview server
- re-open the exact URL in the browser

Recommended sequence:
```bash
npm run typecheck
npm run build
lsof -nP -iTCP:3456 -sTCP:LISTEN -t | xargs -r kill || true
npm run start -- --port 3456
```

Important nuance:
- `next start` serves the last build output. If you change code without rebuilding, the browser can show old layout.

### 5. Prefer measured parity over generic CSS intuition
Do not guess that a page "looks close enough."

For key elements, compare live vs preview numbers directly.
Examples from real usage:
- hero visual was aligned by matching `640x360`
- investor logos were aligned by matching each live logo's measured width/height
- team portraits were aligned by matching natural rendered sizes per person instead of forcing a uniform card aspect
- location flags were aligned by matching measured `23x17`
- world map was aligned by removing a decorative padded card wrapper and matching measured `1200x480`
- section rhythm was aligned by tuning actual section padding and heights based on live measurements

Important caveat from heading-spacing fixes:
- raw geometry numbers and visual perception can disagree for headings because line-height, font rendering, and surrounding list rhythm affect what users perceive as the real gap.
- If console measurements suggest one side is larger but browser vision or the user's screenshot says the opposite on the exact preview URL, trust the rendered preview perception and iterate in small steps.
- For title-spacing fixes, it is often better to adjust only one side at a time (`padding-top` or list `margin-top`) so you can isolate which visible gap changed.

### 6. Scope the parity target carefully
When the user asks for body-area parity, focus on:
- hero split layout
- section spacing
- gray/white band rhythm
- logos/image sizes
- grid/list geometry
- CTA alignment

Do not spend time trying to match unrelated header/footer behavior unless the user explicitly asks.

## Practical heuristics from prior use

### A. Vision can misreport sparse sections
If `browser_vision()` says a section is empty but `browser_snapshot()` and DOM show the content exists:
- trust the DOM measurements
- inspect actual image/heading positions
- keep adjusting geometry rather than assuming the content failed to render

### B. Text snapshots do not prove visual parity
A page can have all the same headings and paragraphs yet still differ due to:
- wrong image sizes
- wrong column widths
- excess card chrome
- extra padding around maps/assets
- wrong section background rhythm
- uniformized image cards where live uses natural image sizes
- a left/right two-column feature band being mirrored relative to live even though the copied text and media assets are all correct
- source-backed widget/application-contract pages being manually reimplemented with local Tailwind primitives instead of preserving the upstream component/CSS contract

When upstream source exists for a widget page, inspect and preserve the source component chain first. Do not treat the source as merely a visual reference to approximate with new primitives unless a direct-port strategy has been explicitly rejected.

Important concrete lesson from `/t/solutions/aip/usage-based-llm` preview migration:
- a migrated page can look superficially correct in snapshots because all headings, paragraphs, and images are present in the right order
- however, one alternating feature band can still be structurally wrong if the preview renders `text-left / image-right` where live renders `image-left / text-right`, or vice versa
- this is easy to miss when the same content is present and the images themselves still look visually plausible in either column

Required verification pattern for alternating feature-band pages:
1. inspect the exact live page in the browser
2. list each major feature section in order
3. record for each section whether it is:
   - text-left / image-right
   - image-left / text-right
   - centered text + image below
4. compare the preview against that exact sequence after deployment, not only locally
5. if one band is mirrored, fix the grid order first, then re-measure the section geometry

### C. Remove decorative wrappers if live is flatter
If the preview wraps a map or media asset in a padded rounded panel but the live page presents the asset flat/full-width, remove the wrapper rather than endlessly tweaking padding.

### C2. For certification/logo galleries, separate intrinsic image size from intended rendered display size
A practical finding from `/t/certifications` follow-up work:
- restoring logo rendering by switching to intrinsic `width`/`height` alone was not enough
- the live page used per-item rendered sizes derived from source content definitions, and a shared `max-w`/`max-h` approach could still make some logos look wrong relative to others
- the reliable pattern was to keep both:
  - intrinsic image dimensions for the actual asset (`imageWidth` / `imageHeight`)
  - explicit rendered display dimensions for each item (`displayWidth` / `displayHeight`)
- then verify those display dimensions against the exact live page in the browser

Narrow-mobile gutter lesson from `/certifications` card/gallery review:
- when auditing certification cards, measure both outer section gutter and card internal padding at 300/320/360/390px, not only a standard 390px mobile viewport
- a `30px` outer gutter can be acceptable at 390px but visually conservative at 300–320px once card `px-8` is also applied
- at 300px, `30px` section gutters plus `32px` card padding can leave only about `176px` of actual card content width
- small changes can cross real wrapping thresholds: reducing the outer gutter from `30px` to `24px` made `Payment Card Industry Data` fit on one line in the audited PCI DSS card
- treat this as a card/gallery-specific policy question, not proof that the global company-page gutter is wrong
- if fixing it, prefer a named card-gallery gutter preset or dedicated wrapper over broad route-level class escape hatches; use `24px` as the safest compromise and `20px` when narrow-mobile card balance is the stronger priority
- see `references/certifications-mobile-gutter-audit.md` for the session-specific measurements and issue wording

Important clarification learned from the same task:
- when the user says "match the visible pixel size" they mean the final human-visible rendered size on the page, not the source site's author token values and not the preview site's own 16px-root reinterpretation of the source rems
- therefore, for logo/image parity tasks, prioritize the exact final browser-rendered geometry from the live page (`getBoundingClientRect()` / visual comparison) over abstract root-rem normalization rules
- use source rem values only as one clue; do not let a 16px-root policy override the user's explicit request to match what the live page actually looks like

Additional asset-format lesson from `/t/certifications`:
- preserve the original asset format when possible, especially when the source content definition explicitly used `svg`
- a migration that silently replaces an original SVG logo with a PNG can introduce blur even if the CSS display size is correct
- for certification badges and similar logos with thin text/linework, SVG should be preferred over PNG/WebP whenever the source page used SVG
- practical rule:
  1. inspect the source content definition to see whether each item was authored as `svg` or `png`
  2. keep SVG items as SVG in the migrated page instead of normalizing everything to raster files
  3. only consider WebP replacement for items whose original source asset was already raster

Useful workflow:
1. inspect the original source content definitions if they exist (for example a legacy MDX/JSON schema that already stores logo width/height per item)
2. inspect whether each item was authored as `svg` or `png`
3. measure the exact live rendered `<img>` geometry in the browser with `getBoundingClientRect()`
4. encode the item-level rendered sizes directly in the route-owned data
5. keep the shared card component thin: pass intrinsic dimensions to `next/image`, and apply the intended rendered size explicitly (for example via style)
6. avoid collapsing everything back to one responsive `max-w` rule unless the live page truly uses uniform logo sizing

Useful browser-console pattern:
```js
(() => {
  const items = Array.from(document.querySelectorAll('main li')).filter(
    (li) => li.querySelector('img') && li.querySelector('h6')
  );
  return items.map((li) => {
    const img = li.querySelector('img');
    const title = li.querySelector('h6')?.textContent?.trim();
    const r = img?.getBoundingClientRect();
    return {
      title,
      width: r ? Math.round(r.width * 100) / 100 : null,
      height: r ? Math.round(r.height * 100) / 100 : null,
      naturalWidth: img?.naturalWidth ?? null,
      naturalHeight: img?.naturalHeight ?? null,
      src: img?.currentSrc || img?.src,
    };
  });
})()
```

This is especially useful when some logos are square, some are wide horizontal badges, and some have visually important aspect differences that should remain distinct across the grid.

### C3. For certification/logo galleries, lock onto the final human-visible rendered size first, then use rem/root math only as supporting evidence
A practical correction learned from `/t/certifications` follow-up work:
- the user explicitly wanted the page to match what a person sees on the live page, not the source site's abstract rem intent and not a 16px-root reinterpretation of those rems
- therefore, the authoritative target for logo size parity is the final browser-rendered geometry on the live page (`getBoundingClientRect()` / visual review), even when the source content originally defined the sizes in rem and even when corp-web-japan keeps a 16px root
- in other words: for this page family, visible final size wins over root-rem normalization

Required review sequence for rem-sized certification/logo galleries:
1. read the source content/config and identify whether each item was authored in rem and whether the source asset type was `svg` or `png`
2. measure the live page's actual rendered size in the browser
3. inspect the live page's `html` root font-size only to understand *why* the numbers differ, not to override the live visible result automatically
4. inspect the preview/stage page's actual rendered size in the browser
5. if the user's goal is visual parity, copy the live page's final visible width/height into the route-owned display sizing
6. only use 16px-root rem conversion as a fallback when the user explicitly asks to preserve design-token intent instead of visual result

Practical certification example:
- source `PCI DSS`: `14.86rem x 4.5rem`
- live root `15px` -> rendered about `222.89px x 67.42px`
- corp-web-japan root `16px`
- if the task is visual parity, the correct target is still about `222.89px x 67.42px`, because that is what the user sees on the live page
- do not automatically enlarge it to the 16px-root rem-equivalent value just because the preview app keeps a 16px root

Related asset-format lesson from the same task:
- some gallery items may also differ by asset type, not just by size
- `PCI DSS` looked blurred because live used an SVG asset while corp-web-japan used a PNG copy of the same logo
- before blaming the size math, inspect the actual asset format on both sides (`svg` vs `png/webp`) and verify the live `img.currentSrc`
- wide horizontal badges with text/line detail are especially sensitive to raster blur on high-DPR screens
- if the source content defined an item as SVG, prefer restoring SVG in corp-web-japan rather than normalizing it to PNG/WebP

Heuristic:
- for corp-web-japan certification/logo parity work, treat live visible geometry as the primary contract unless the user explicitly re-prioritizes token-level rem consistency
- for logo galleries, check both the live measured size and the asset format before finalizing parity judgments

### D. Natural image sizes may matter more than neat symmetry
For people/team sections, live may intentionally use different portrait sizes per column. If the preview forces equal card widths/heights, parity can look wrong even though the grid is technically cleaner.

Important override rule learned from `/t/about-us` follow-up work:
- treat live parity as the default goal, not as a hard constraint against the user's explicit direction
- if the user explicitly asks for a normalized invariant such as "all executive profile image boxes must use one fixed size," follow that request even when the live page currently uses mixed widths
- in that case, still use the live page to compare surrounding layout structure (text/icon row layout, spacing rhythm, list structure, section spacing), but let the user's explicit invariant win for the targeted element

Additional decision rule from the same page family:
- if the user or repo already defined a stable page-policy rule, do not reopen it as a fresh design choice just because the live page renders differently
- practical examples from `/t/about-us`:
  - if the rule is "non-split wide text blocks default to 1200px", do not keep presenting a live-narrower CTA or intro width as an open choice; treat the policy as authoritative and classify the live width as a source-site inconsistency or non-target quirk
  - if the site policy prefers a uniform card grid, do not frame live mixed card widths as something that must be restored unless the user explicitly asks for pixel-parity over site consistency
- in reports, separate these categories explicitly:
  1. actual implementation defects vs the agreed local policy
  2. differences from live that are intentional local-policy adaptations
  3. live-side inconsistencies or non-authoritative quirks that should not drive the migration

Practical heuristic:
- if the user says an element should be standardized, do not keep arguing from live-page variation
- normalize the requested element intentionally, then re-check that the rest of the section still harmonizes with the live page
- once the user has already given the governing layout rule, do not rephrase that rule as "choose A vs B" in an audit or issue write-up; apply the rule and report the conclusion directly

### E. Cross-axis stretch can make a supposedly small frame expand to full card width
For icon/frame parity work inside vertical flex cards, do not trust `inline-flex` alone.

### E2. For `/about-us`, compare actual layout structure before tweaking spacing
A key lesson from `/ja/company/about-us` vs `/t/about-us` parity work:
- some visible mismatches are not spacing bugs but **wrong layout structure choices** in the preview
- if you only tweak margins/padding, you can miss that the live page uses a different row/column model entirely
- also, do not jump from a measured live/stage difference straight to "preview bug"; first decide whether the live page may itself be using an inconsistent or legacy implementation pattern

Important concrete findings:
- team leader cards on live were **not** uniform full-width cards; rendered card/image widths differed by person
  - examples observed on desktop live:
    - Brant/Jake about `264px`
    - Paul/Kris about `242px`
    - Sam/Keizo about `320px`
- the LinkedIn icon on live was **not** a separate full-width bottom row
  - it lived in the same horizontal row as the text block (`justify-content: space-between`), aligned to the right of the name/role block
  - a preview implementation using `w-full justify-end` on the link made the icon look like a bottom-aligned footer row instead of a side-aligned social action
- the timeline on live was **not** a vertical divider table
  - it was a `flex` row with:
    - fixed year width around `94px`
    - horizontal gap around `18.75px`
    - a normal bullet list with `list-style: disc` and padding-left around `20px`
  - the subtle vertical divider was **not on each row**; it lived on the outer timeline list container itself
    - real live CSS pattern observed: the timeline list wrapper (`timeline_ul`) carried `border-left: 1px solid ...` plus left padding around `30px`
    - if the preview shows a `border-left` on the second column inside each row, that is the wrong structure
  - if the preview shows no divider at all, check the outer timeline wrapper before changing the row markup again

Required parity workflow for this page family:
1. inspect the exact live page in the browser
2. measure the real card widths, icon link box, and timeline row/list geometry
3. compare structure first, not just distances
4. if preview structure differs, rewrite the JSX/layout model to match live before fine-tuning spacing

Useful live-page measurement patterns:
```js
// team card widths and LinkedIn placement
Array.from(document.querySelectorAll('li, article'))
  .filter(el => el.querySelector('a[href*="linkedin.com"]'))
  .slice(0, 6)
  .map(card => {
    const img = card.querySelector('img');
    const link = card.querySelector('a[href*="linkedin.com"]');
    const r = card.getBoundingClientRect();
    const ir = img?.closest('div')?.getBoundingClientRect();
    const lr = link?.getBoundingClientRect();
    return {
      name: card.querySelector('h6,h3')?.textContent?.trim(),
      cardW: Math.round(r.width),
      imageW: ir ? Math.round(ir.width) : null,
      linkW: lr ? Math.round(lr.width) : null,
      linkLeft: lr ? Math.round(lr.left) : null,
      cardRight: Math.round(r.right),
    };
  });

// timeline structure
Array.from(document.querySelectorAll('h4,h3'))
  .filter(h => /^20\d{2}$/.test(h.textContent?.trim() || ''))
  .slice(0, 8)
  .map(h => {
    const row = h.closest('li, div');
    const ul = row?.querySelector('ul');
    const rr = row?.getBoundingClientRect();
    const ur = ul?.getBoundingClientRect();
    return {
      year: h.textContent?.trim(),
      rowW: rr ? Math.round(rr.width) : null,
      ulW: ur ? Math.round(ur.width) : null,
      listStyle: ul ? getComputedStyle(ul).listStyleType : null,
      paddingLeft: ul ? getComputedStyle(ul).paddingLeft : null,
      borderLeft: ul ? getComputedStyle(ul).borderLeft : null,
    };
  });
```

Preferred fix patterns when the preview is structurally wrong:
- team cards:
  - first measure every live card individually before claiming the layout is uniform or intentionally varied
  - record card width, image-wrapper width, and LinkedIn icon placement per person
  - if live widths differ (for example 242 / 264 / 320), report that as a factual live-rendering observation
  - do not automatically recommend reproducing those mixed widths; classify separately whether that is required for strict live parity or whether a uniform preview grid may be the more intentional design choice
  - keep the image wrapper width equal to the intended card width
  - place the LinkedIn link in the same horizontal row as the text block
  - use a tiny fixed-width icon/link box on the right, not a full-width footer row
- timeline:
  - remove fake divider borders if live does not use them
  - use a fixed-width year column and a bullet list rather than a table-like bordered second column

Heuristic:
- if the preview seems "close" but the icon feels vertically wrong or the timeline divider feels arbitrary, stop adjusting spacing and verify whether the live DOM/CSS is using a completely different layout primitive.

Additional audit lesson from a later `/t/about-us` review-only session:
- do not let `browser_vision()` alone convince you that middle-page sections are missing; it can judge a long page from the current viewport and incorrectly describe the body as mostly empty even when the DOM/snapshot clearly contains investor, timeline, team, office, and map sections
- for parity review reports, verify section presence from `browser_snapshot()` or DOM queries first, then use vision only as a secondary note about above-the-fold impression
- on this page family, the more meaningful remaining parity gaps were not missing content but:
  - typography scale differences caused by `html` root size differences (`15px` live vs `16px` preview)
  - CTA container width/left offset differences
  - uniformized team-card widths in preview versus varied live widths
  - semantic heading-level drift (`H4/H6` on live becoming `H3` in preview)
- before turning a browser-parity review into an issue/report, re-check the current repo source for explicit width constraints and route-local overrides. A browser-visible paragraph that currently fits on one line can still be implementation-wise wrong if the code narrows it to a fragile max-width that only barely avoids wrapping in the current environment.
- concrete `/t/about-us` rule learned from user correction: wide body/introduction paragraphs should default to the full `1200px` content width unless there is a clearly intentional narrower layout region such as the hero's left column. In this page family, `AboutUsSectionIntro className="max-w-[760px]"` on broad section intros was a bug, not a design virtue.
- practical implication: for the timeline intro sentence `AIが次のフロンティアになったとき、多くの企業が「莫大なコストと複雑な実装」という2つの壁に直面しました。`, do not accept "it happens to fit right now" as evidence that the width is correct. If the parent intro container is artificially narrowed (for example `760px`), treat that as a parity/robustness defect even if the current browser run keeps the first sentence on one line.

Practical review checklist for `/about-us` parity audits:
1. confirm all expected sections exist in DOM/snapshot before calling the page incomplete
2. compare `html` root font size on both sides
3. compare `h1` and ordinary body paragraph computed font-size/line-height
4. compare CTA heading width and left offset, not just text content
5. compare team card widths item-by-item; do not assume a normalized grid matches live
6. compare semantic heading tags for years, team names, and office names when structural fidelity matters
7. inspect the current route source for `max-w-*` constraints on broad intro/body text blocks before writing conclusions; on `/t/about-us`, broad section intros should normally be `1200px`, not `760px`

Important real finding from `/t/about-us` flag-frame follow-up:
- a frame wrapper inside `flex flex-col` can still stretch across the card width on the cross axis
- this can make a border that appears source-correct render as a full-width bar in the preview
- browser DOM measurement exposed this clearly:
  - flag image rendered at about `23x17`
  - parent frame rendered at about `273x19`
- the real cause was not border thickness but flex-item stretching

Required debug pattern when a small badge/icon frame looks too wide:
1. inspect the exact preview URL the user reported
2. measure both the image and its parent wrapper with `getBoundingClientRect()`
3. compare parent width vs image width
4. inspect computed styles such as `display`, `align-self`, `width`, and `line-height`

Useful browser-console pattern:
```js
(() => {
  const img = document.querySelector('img[alt="United States"]');
  const p = img?.parentElement;
  const ir = img?.getBoundingClientRect();
  const pr = p?.getBoundingClientRect();
  return {
    img: ir ? { w: ir.width, h: ir.height } : null,
    parent: pr ? { w: pr.width, h: pr.height } : null,
    parentStyles: p ? {
      display: getComputedStyle(p).display,
      width: getComputedStyle(p).width,
      alignSelf: getComputedStyle(p).alignSelf,
      lineHeight: getComputedStyle(p).lineHeight,
    } : null,
  };
})()
```

Reliable fix pattern:
- add `self-start` to stop cross-axis stretch inside `flex-col`
- add `w-fit` so the wrapper shrinks to its content width
- add `leading-none` on the wrapper and `block` on the image when you need to remove extra inline/line-box slack
- then re-measure the deployed preview until the wrapper is only slightly larger than the image because of the border

Practical example outcome:
- before fix: parent about `273x19`, image `23x17`
- after fix: parent about `25x19`, image `23x17`

### F. Keep hero title structure separate from body columns when live does
A frequent parity mistake is to put the page `h1` inside the left side of a two-column hero grid. If the live page visually reads as:
- full-width `h1` spanning the content container,
- then a second row with left body copy and right visual/media,

then reproduce that structure literally.

Practical rule:
- first render the `h1` as its own block across the full content width
- then place the explanatory paragraphs and hero visual in a two-column grid below it
- do not assume that because the hero is visually two-column, the headline itself belongs only to the left column

This matters a lot for perceived parity, because users notice immediately when the title width is constrained compared with the live page.

### F1. For hero-spacing audits, separate absolute page offset from internal hero rhythm
When the user asks specifically about `h1` position, GNB spacing, and the gap between `h1` and the first paragraph/content/box, do not collapse all deltas into one generic "hero spacing" finding.

Measure these as separate anchors on both URLs:
- header/GNB rect height and bottom
- `h1` top/bottom/height and computed font-size/line-height
- `header.bottom -> h1.top`
- `h1.bottom -> first paragraph.top`
- `first paragraph.bottom -> first media.top` when the hero contains a video/image
- `first media.bottom -> first major section.top`
- `h1.bottom -> first major section.top`

Then classify the result:
- if `h1 -> paragraph`, `paragraph -> media`, and `media -> first section` are identical, the internal hero rhythm is already faithful
- if only `header.bottom -> h1.top` differs, report it as a hero start / top-offset issue, not as a body-content spacing issue
- include both absolute viewport deltas and relative intra-hero deltas so the user can see whether the whole hero is shifted upward/downward versus internally mis-spaced

Practical example from `/t/platforms/aip` vs `/ja/solutions/aip`:
- stage header height was `64px`, live header height was `88px`
- stage `header.bottom -> h1.top` was `16px`, live was `80px`
- `h1.bottom -> first paragraph.top` was `20px` on both
- `first paragraph.bottom -> YouTube media.top` was `80px` on both
- `media.bottom -> first value-card section.top` was `120px` on both
- conclusion: the stage page's internal hero/content rhythm matched live, but the hero started too close to the GNB/header

### F2. Map spacing findings back to the family-level primitive before recommending fixes
After measuring a top-spacing mismatch, inspect the current route and identify which class-level/family-level primitive owns the spacing before recommending a patch.

Concrete corp-web-japan mapping from this session:
- Platform family routes such as `/t/platforms/aip` use `src/components/sections/platform/page-primitives.tsx`.
  - `PlatformPageSection` should own the GNB/header-to-page or GNB/header-to-h1 top offset for Platform-family hero/page starts, analogous to `CompanyPageSection` in the Company family.
  - `PlatformHeroSection` should delegate to `PlatformPageSection`; do not make hero-only spacing the only owner when the same top-offset responsibility is a page-family primitive.
  - Keep a separate `PlatformContentSection` (or equivalent body/content wrapper) for ordinary later sections so content sections do not accidentally inherit first-page/hero top padding.
  - `AipHeroCopy`, `AipHeroInner`, `AipHeroTitle`, and `AipHeroLead` own internal hero rhythm/typography and should not be changed when only `header.bottom -> h1.top` differs.
- Company family routes such as `/about-us`, `/contact-us`, `/certifications`, and `/news` use `src/components/sections/company/page-primitives.tsx`.
  - `CompanyPageSection` owns the GNB/header-to-content or GNB/header-to-h1 top offset via `pt-[100px] lg:pt-[120px]`.
  - `CompanyPageIntro` owns the h1-to-lead/body gap via `gap-10 lg:gap-[50px]` plus mobile-only `pt-[10px]`.
  - `CompanyPageTitle` owns h1 typography only; do not change it to fix GNB spacing.
  - `SiteHeader` / `site-header.module.css` owns the fixed header height (`--gnb-height: 64px`) but changing it affects the entire site chrome, so prefer family section primitives for body offset fixes unless the task is explicitly header-wide.

Recommended reporting pattern:
1. say whether the measured defect is a page absolute-offset issue or an internal hero/body rhythm issue
2. name the primitive that owns that exact axis
3. explicitly list nearby components that should not be touched because their measured rhythm already matches

### F. When matching a CTA section, compare every child element, not just the outer box
A recurring parity failure is to "mostly match" the CTA by changing only the background, button, or one text node.

For a CTA like the documentation footer block, measure all of these separately on both live and preview:
- outer CTA section
- inner text wrapper
- title heading
- body paragraph
- actions row
- button anchor
- button text span
- button icon wrapper

For each child, compare:
- width
- height
- top/bottom positions
- padding/margin
- gap
- font size
- font weight
- line height
- letter spacing
- wrapping behavior (`white-space` and actual rendered line count)

Practical lesson from the internal MDX demo CTA work:
- partial fixes created repeated confusion because one child would still differ and visually dominate the section
- the right method is to gather the full child geometry/style set first, then patch the whole section until all key children align

### G. Trust computed styles over class strings when utilities and base classes mix
Another strong lesson from CTA parity work:
- seeing the "right" utility classes in source does not prove the browser is using the intended values
- shared component base classes can keep winning in the final cascade, especially for padding, font size, and responsive variants
- if preview still looks wrong, inspect computed styles directly before assuming the fix landed

Useful verification pattern:
- compare live and preview `getComputedStyle()` values for the exact element
- if the class list still produces the wrong computed result, use a more reliable override (for example a stronger class, responsive override, or inline `style` where appropriate)

Important practical finding from corp-web-japan CTA parity debugging:
- a live page can appear to use a `52px` heading token in DevTools Styles while the actual rendered computed size is `48.75px`
- this happened because the site defined the heading token as `3.25rem` (`--rem-52px`) while the live page root `html` font-size was `15px`
- `3.25rem × 15px = 48.75px`, so the token name and the final used value differed

Practical rule:
- when a user says "DevTools shows 52px" and your computed-style measurement says `48.75px`, do not assume one of them is wrong yet
- inspect all of these together on the exact same element:
  - the matching CSS rule / token name
  - the CSS variable value if present
  - `html` root font-size
  - final `getComputedStyle(element).fontSize`
- for rem-based systems, explicitly compute `rem × root-font-size` before concluding there is a real mismatch
- if needed, explain the difference as `author/token value` vs `final computed value`

### G1. When a preview site intentionally keeps the standard `16px` root, do not copy a live site's shrunken computed px values if the live site uses a non-standard smaller root
A crucial follow-up lesson from the generic CTA refactor work:
- the live QueryPie documentation CTA used `52px` / `16px` / `14px`-style tokens expressed as rems
- but the live site root `html` font-size was `15px`, so those rem tokens produced smaller computed values such as `48.75px`, `15px`, `13.125px`, and `5.625px`
- a separate preview site that intentionally keeps the more standard `16px` root should not blindly copy those computed values into its own component tokens
- doing so makes the preview look slightly undersized, even if a first computed-style comparison seemed to "match" the live used values

Practical rule:
- first decide which environment is canonical for token semantics
- if the preview/product intentionally keeps a standard `16px` root, prefer matching the live page's author/token intent rather than its shrunken used values from a `15px` root
- in practice this means converting CTA primitives back to the `16px`-root token sizes, for example:
  - heading `52px / 62px`
  - body `16px / 26px`
  - button padding `14px 28px`
  - button radius `6px`
  - button gap `10px`
- only use the live computed values directly when the preview shares the same root font-size strategy as the live site

Verification pattern:
1. inspect the exact live element's CSS rule/token values
2. inspect the live `html` root font-size
3. inspect the preview `html` root font-size
4. if the roots differ, decide whether parity should follow:
   - final rendered used values, or
   - the live design tokens normalized for the preview's root scale
5. if the preview is intended to remain standards-based, normalize to token-level values for that root before changing the component

Additional practical cookie-preference lesson:
- even after matching token-level sizes, heading wrap can still differ because the preview shell width and font rendering environment are not identical to the live site
- when the exact requested preview deployment still wraps differently from live, use in-browser experimentation on the deployed preview DOM before editing code again
- a fast pattern is to temporarily set candidate `font-size` / `line-height` values in the browser console, measure the resulting bounding box, and identify the smallest visual change that flips the heading from 2 lines to 1 line (or vice versa)
- after finding that threshold, encode only that minimal value change in code and re-check the exact preview URL after deploy

Example browser-console pattern:
```js
const h = [...document.querySelectorAll('main h2')].find((el) => /まずは小さく/.test(el.textContent || ''));
[48.75, 47, 46, 45].map((size) => {
  h.style.fontSize = `${size}px`;
  h.style.lineHeight = `${size * 1.1923}px`;
  const r = h.getBoundingClientRect();
  return { size, width: Math.round(r.width), height: Math.round(r.height) };
});
```
This is especially useful when a value that looks "correct" from live computed styles still wraps differently in the preview shell.

Related CTA-button lesson:
- if live and preview already share the same horizontal padding and label size, but the preview button still renders shorter, test `min-height` directly in the browser before rewriting the whole button
- in cookie-preference CTA parity work, `min-height: 47px` was enough to match the live button height once padding was already aligned
- prefer the smallest property that closes the geometry gap instead of rebuilding the entire primitive too early
### H. Sticky failures often come from an unexpected scroll container, not from the sticky element itself
A sticky sidebar can look correctly coded yet still fail because one ancestor became the real scroll container.

Important practical finding from internal MDX demo work:
- `overflow-x-hidden` on `main` can compute as `overflow-y: auto` in the browser
- that makes `main` the sticky containing scroll container
- as a result, the sidebar may scroll away even though `position: sticky` and `top` are set on the sidebar itself

Required diagnosis steps when sticky does not work:
1. inspect the sticky element's computed `position` and `top`
2. inspect every important ancestor (`aside` parent row, section, `main`, `body`, `html`) for
   - `overflow`, `overflow-x`, `overflow-y`
   - `position`
   - `height`
3. scroll and record the sticky element's `getBoundingClientRect().top` before and after scrolling

If the sticky element's top becomes negative instead of clamping to the expected offset, suspect an ancestor scroll container first.

Practical fix pattern:
- remove or relocate the ancestor overflow rule that creates the unintended scroll container
- then re-test sticky in a real browser by scrolling and confirming the top clamps to the expected offset

### F. Sticky parity can fail because an ancestor became the scroll container
For left-side sticky navigation parity, do not stop at checking whether the target element has `position: sticky`.

Important finding from `internal/mdx-list-demo` parity work:
- a parent like `main` can accidentally become the scroll container even when the author only intended horizontal clipping
- for example, `overflow-x-hidden` on `main` can produce computed style `overflow-y: auto`
- once that happens, a sidebar with `position: sticky` may anchor against the wrong scroll container and appear broken during normal page scroll

Required debug steps:
- inspect the sticky element and all relevant ancestors (`aside`, row wrapper, section, `main`, `body`, `html`)
- read computed `overflow`, `overflowX`, `overflowY`, `position`, and `top`
- scroll the page and compare `getBoundingClientRect().top` before/after scroll

Practical rule:
- if sticky should follow the viewport, keep ancestor overflow visible on the vertical axis
- if a wrapper only needs horizontal clipping, confirm it does not accidentally create vertical scrolling behavior
- verify with browser measurements like:
  ```js
  const aside = document.querySelector('main aside');
  ({
    top: aside?.getBoundingClientRect().top,
    pos: getComputedStyle(aside).position,
    mainOverflow: getComputedStyle(document.querySelector('main')).overflow,
  })
  ```

### G. Utility classes may not be enough when shared defaults still win
For pixel-accurate parity work, do not assume appending more Tailwind utility classes will change the final rendering if a shared component already sets competing defaults.

Important finding from CTA parity work:
- code can look "correct" while browser computed styles still reflect shared defaults
- section padding/background values can stay wrong because earlier utility classes from a shared wrapper still win in the merged output

Practical rule:
- always compare browser computed styles after each change, not just source code
- if utility layering keeps losing and the task is narrow route-specific parity, use a route-local `style={{ ... }}` override for the exact value, then verify again in the browser
- this is especially useful for final CTA padding/background alignment where the live page has exact decimal pixel values

### F. Old process notifications can be misleading
If the system later emits watch-pattern or exit notifications for older background processes:
- inspect `process(action='list')`
- identify the currently running preview session
- ignore delayed completion notifications for already-killed sessions

### G. Verify the exact preview deployment commit before trusting any visual report
When the user gives a specific Vercel preview URL and says the rendered result is wrong, first verify that URL is actually serving the commit you think it is.

Practical pattern:
```bash
vercel inspect <preview-url> --logs
```

Then check:
- the Git branch name shown in the build log
- the exact commit SHA shown in the clone step
- whether it matches the current PR head SHA from `gh pr view <pr-number> --json headRefOid`

Why this matters:
- users often keep an older preview URL open while the PR branch has already moved on
- a visual mismatch may come from the preview not yet containing the latest commit, not from the latest code itself
- this verification should happen before you chase styling differences that may already be fixed on a newer deployment

### H. Sticky failures can come from an unintended scroll container, not from the sticky element itself
For sidebar/list parity work, if a sticky sidebar looks correctly authored in code but still scrolls away, inspect ancestor computed styles before changing the sticky target repeatedly.

Important real finding:
- an ancestor with `overflow-x: hidden` can compute to `overflow-y: auto` in the browser, effectively turning that ancestor into the scroll container
- when that happens, `position: sticky` stops using the viewport as expected and can appear broken even though `top` and `position: sticky` are set correctly

Useful browser-console check:
```js
(() => {
  const aside = document.querySelector('main aside');
  const main = document.querySelector('main');
  return {
    aside: {
      position: getComputedStyle(aside).position,
      top: getComputedStyle(aside).top,
    },
    main: {
      overflow: getComputedStyle(main).overflow,
      overflowX: getComputedStyle(main).overflowX,
      overflowY: getComputedStyle(main).overflowY,
    },
  };
})()
```

Practical fix pattern:
- if the sticky ancestor is unintentionally becoming a scroll container, remove that overflow behavior first
- for example, replacing `overflow-x-hidden` on the route `main` wrapper with a non-scrolling wrapper can restore correct viewport-based sticky behavior
- re-measure after scrolling; the sticky element's top should clamp to the intended offset (for example `128px`) instead of continuing upward into negative coordinates

### I. If Tailwind utility overrides still do not change computed styles, use inline styles for parity-critical numeric values
For exact visual parity tasks, utility class stacking can leave older base classes winning in the final computed style, especially when a reusable primitive already bakes in default spacing.

Important real finding:
- adding more Tailwind padding classes to a reusable component did not reliably change the computed preview padding
- the browser still reported the old spacing values until route-level inline styles were used

Use this when the task is explicitly to match measured live values, not to preserve a pure utility-only code style.

Practical pattern:
```tsx
<ResourceListContentSection style={{ paddingBottom: "187.5px" }}>
  ...
</ResourceListContentSection>

<ResourceListCtaSection style={{ backgroundColor: "#F6F8FA", padding: "112.5px 22.5px" }}>
  ...
</ResourceListCtaSection>
```

This is appropriate when:
- you already measured the exact live values in the browser
- utility classes are not producing the same computed styles
- the scope is a narrow parity fix on a specific route or demo page

## Good implementation pattern for `/t/*` company-info parity pages

Recommended browser-console check:
```js
const aside = document.querySelector('main aside');
const main = document.querySelector('main');
({
  asidePos: getComputedStyle(aside).position,
  asideTop: getComputedStyle(aside).top,
  mainOverflow: getComputedStyle(main).overflow,
  mainOverflowX: getComputedStyle(main).overflowX,
  mainOverflowY: getComputedStyle(main).overflowY,
})
```

If the supposed sticky ancestor shows `overflow: hidden auto` or similar, remove or relocate that overflow behavior before continuing to tweak sticky offsets.

Practical verification loop:
- measure sidebar `getBoundingClientRect().top` at scroll 0
- scroll down
- measure it again
- if sticky works, the value should settle at the configured top offset (for example `128px`) instead of continuing to move upward

This is a better first check than blindly changing `top`, `self-start`, or wrapper nesting.

### G. Old process notifications can be misleading

- shared section primitives already include base padding/background classes
- the route adds more Tailwind utility classes that look like they should override those defaults
- but the browser still computes the old values, so the preview keeps looking wrong

Important practical lesson:
- do not trust the class string alone
- always verify the browser's computed style on the exact preview/local URL
- if the computed style still shows the old padding/background values, stop adding more utility classes and switch to a stronger route-local override

Reliable recovery pattern:
- measure the live page's actual values in the browser (`padding`, `backgroundColor`, element height, margins)
- inspect the preview/local page's computed style for the same elements
- if the shared primitive's default classes still win, add a narrowly scoped `style={{ ... }}` override at the route callsite or extend the primitive with an explicit `style` prop
- re-check the computed style again before concluding the fix worked

This is especially useful for CTA/footer-adjacent sections where perceived parity depends on exact section padding and background bands, and where multiple inherited Tailwind classes can obscure which value actually wins.

### F. Old process notifications can be misleading
If the system later emits watch-pattern or exit notifications for older background processes:
- inspect `process(action='list')`
- identify the currently running preview session
- ignore delayed completion notifications for already-killed sessions

### G. Verify the exact preview deployment commit before trusting any visual report
When the user gives a specific Vercel preview URL and says the rendered result is wrong, first verify that URL is actually serving the commit you think it is.

Practical pattern:
```bash
vercel inspect <preview-url> --logs
```

Then check:
- the Git branch name shown in the build log
- the exact commit SHA shown in the clone step
- whether it matches the current PR head SHA from `gh pr view <pr-number> --json headRefOid`

Why this matters:
- users often keep an older preview URL open while the PR branch has already moved on
- a visual mismatch may come from the preview not yet containing the latest commit, not from the latest code itself
- this verification should happen before you chase styling differences that may already be fixed on a newer deployment

### H. Sticky failures can come from an unintended scroll container, not from the sticky element itself
For sidebar/list parity work, if a sticky sidebar looks correctly authored in code but still scrolls away, inspect ancestor computed styles before changing the sticky target repeatedly.

Important real finding:
- an ancestor with `overflow-x: hidden` can compute to `overflow-y: auto` in the browser, effectively turning that ancestor into the scroll container
- when that happens, `position: sticky` stops using the viewport as expected and can appear broken even though `top` and `position: sticky` are set correctly

Useful browser-console check:
```js
(() => {
  const aside = document.querySelector('main aside');
  const main = document.querySelector('main');
  return {
    aside: {
      position: getComputedStyle(aside).position,
      top: getComputedStyle(aside).top,
    },
    main: {
      overflow: getComputedStyle(main).overflow,
      overflowX: getComputedStyle(main).overflowX,
      overflowY: getComputedStyle(main).overflowY,
    },
  };
})()
```

Practical fix pattern:
- if the sticky ancestor is unintentionally becoming a scroll container, remove that overflow behavior first
- for example, replacing `overflow-x-hidden` on the route `main` wrapper with a non-scrolling wrapper can restore correct viewport-based sticky behavior
- re-measure after scrolling; the sticky element's top should clamp to the intended offset (for example `128px`) instead of continuing upward into negative coordinates

### I. If Tailwind utility overrides still do not change computed styles, use inline styles for parity-critical numeric values
For exact visual parity tasks, utility class stacking can leave older base classes winning in the final computed style, especially when a reusable primitive already bakes in default spacing.

Important real finding:
- adding more Tailwind padding classes to a reusable component did not reliably change the computed preview padding
- the browser still reported the old spacing values until route-level inline styles were used

Use this when the task is explicitly to match measured live values, not to preserve a pure utility-only code style.

Practical pattern:
```tsx
<ResourceListContentSection style={{ paddingBottom: "187.5px" }}>
  ...
</ResourceListContentSection>

<ResourceListCtaSection style={{ backgroundColor: "#F6F8FA", padding: "112.5px 22.5px" }}>
  ...
</ResourceListCtaSection>
```

This is appropriate when:
- you already measured the exact live values in the browser
- utility classes are not producing the same computed styles
- the scope is a narrow parity fix on a specific route or demo page

### J. Reveal/animation wrappers can silently shrink supposedly full-width hero media
A practical failure mode from `/t/solutions/aip/fde-services` parity work:
- the page route rendered a hero visual through a client `RevealOnScroll` wrapper
- the hero section and inner media container looked source-correct (`w-full`, large max-width, centered layout)
- but the rendered hero image still came out narrower than expected
- browser DOM measurement showed the real width bottleneck was the reveal wrapper itself, not the image component

Symptoms:
- browser text/snapshot suggests the page is correct
- the hero image still renders noticeably narrower than the live page
- `img`, parent container, and wrapper all report the same unexpectedly small width in `getBoundingClientRect()`

Required diagnosis pattern:
1. measure the target image width
2. measure its immediate parent width
3. walk up through 2-3 ancestors and compare widths
4. inspect whether a transition/reveal wrapper is the first ancestor that stops stretching to the intended width

Useful browser-console pattern:
```js
(() => {
  const img = Array.from(document.querySelectorAll('main img')).find(i => i.alt === 'Custom AI Agents');
  const nodes = [img, img?.parentElement, img?.parentElement?.parentElement, img?.parentElement?.parentElement?.parentElement].filter(Boolean);
  return nodes.map((n, i) => ({
    i,
    tag: n.tagName,
    className: n.className,
    rectWidth: Math.round(n.getBoundingClientRect().width),
    computedWidth: getComputedStyle(n).width,
  }));
})()
```

Reliable fix pattern:
- if the reveal wrapper is narrower than the intended media width, give the wrapper explicit stretching responsibility at the route callsite
- examples:
  - `className="w-full"` on the reveal wrapper invocation
  - `self-stretch` on the hero visual section when it lives inside a column flex container
  - `mx-auto w-full max-w-[...]` on the immediate hero media container
- then re-measure the deployed preview URL, not just local source

This is especially important for static marketing pages where the hero visual should span the full content width and a narrow wrapper makes the page feel materially different from live.

### K. If chrome-devtools MCP is unavailable, fall back to browser DOM measurement plus source HTML/CSS inspection
Another practical lesson from the same task:
- the chrome-devtools MCP server can become unreachable after repeated timeouts
- this should not block parity work if the page is otherwise accessible through the normal browser tool and terminal/web fetches

Fallback workflow:
1. use `browser_navigate()` on the exact live URL and exact preview URL
2. use `browser_console()` to extract DOM geometry and computed styles
3. if browser visual tools are misleading or incomplete, fetch the live HTML and linked CSS in the terminal and inspect the actual source tokens/classes
4. compare live computed geometry against preview computed geometry numerically

Useful fallback sources:
- `browser_console()` for `getBoundingClientRect()` and `getComputedStyle()`
- `requests`/`curl` in terminal for live HTML
- live CSS scraping to recover token values such as `--rem-60px`, `--rem-52px`, `--text-body`, layout gaps, and section paddings

Important nuance:
- browser vision can incorrectly describe the page body as blank or mostly empty even when the DOM and CSS confirm the content is present
- when that happens, trust DOM geometry and fetched source over the vision summary

### K2. For lazy media/GIF pages, scroll and wait before classifying images as missing
A practical finding from `/t/platforms/aip` parity work:
- on the hosted preview, route-aligned GIF assets returned `200 OK` via `curl -I`, and the files existed in `public/services/aip/*`
- however, an initial top-of-page browser measurement reported the feature GIF `<img>` elements as `0x0`, `complete: false`, and `currentSrc: ""`
- after scrolling down to the sections and waiting, the same images loaded and measured correctly
- the initial `0x0` state was lazy-loading / viewport timing, not proof that the assets were missing

Required media-parity workflow for long lazy-loaded pages:
1. verify the asset URLs directly with `curl -I -L <preview-url>/path/to/asset.gif` or equivalent
2. verify the files exist in the worktree under the intended route-aligned asset namespace
3. navigate the browser to the exact preview deployment URL
4. scroll to the media-heavy sections, wait several seconds, then re-measure `complete`, `naturalWidth`, `naturalHeight`, `currentSrc`, and `getBoundingClientRect()`
5. only classify an image as missing if it still has no natural dimensions after it has entered or approached the viewport and the asset URL itself fails or points to the wrong file

Useful browser-console pattern:
```js
new Promise((resolve) => {
  window.scrollTo(0, document.body.scrollHeight);
  setTimeout(() => {
    resolve(Array.from(document.querySelectorAll('main img'))
      .filter((img) => img.src.includes('/services/aip/'))
      .map((img) => {
        const r = img.getBoundingClientRect();
        return {
          alt: img.alt,
          complete: img.complete,
          naturalWidth: img.naturalWidth,
          naturalHeight: img.naturalHeight,
          currentSrc: img.currentSrc,
          width: Math.round(r.width),
          height: Math.round(r.height),
          top: Math.round(r.top + scrollY),
        };
      }));
  }, 8000);
})
```

### K3. Feature media can be oversized because the wrapper lacks the source image width
A practical finding from `/t/platforms/aip` parity work:
- the source live page rendered AIP feature GIFs at fixed widths such as `540`, `580`, `520`, and `600` px from `MainFeatureDescription imageWidth`
- the preview passed `width`/`height` to `next/image`, but the immediate wrapper had only `max-w-full`; inside the flex row this allowed media to stretch much wider, e.g. about `920px`
- fixing only the image's intrinsic props was insufficient; the wrapper that owns the visual chrome also needed an explicit width
- after media width is fixed, still measure the copy column separately: in one `/t/platforms/aip` audit, the first three `AipFeatureCopy` wrappers were about `59px`, `158px`, and `146px` narrower than live even though media width and the `80px` row gap matched
- do not treat route-local `max-w-*` values on feature copy as authoritative until they are checked against live/source layout

Reliable desktop fix pattern:
- make the feature media wrapper `flex-none` / non-stretching
- set the wrapper width to the route-authored/source-derived media width, for example `style={{ width }}`
- keep the inner image `className="h-auto w-full"`
- re-measure on the exact preview deployment URL after the PR deploy

Important mobile follow-up from a later `/t/platforms/aip` audit:
- a desktop-correct fixed media width can become the mobile bug if the same row remains `flex-row` / `flex-row-reverse` at `390px`
- in that state, images can keep `540`, `580`, or `600px` desktop widths while the text column collapses to `30px`-wide vertical strips and the mobile scroll height nearly doubles
- when applying this desktop-width pattern, also add an explicit mobile contract: stack the feature row on small screens and constrain the media wrapper to the content column before restoring the source fixed width at desktop breakpoints
- see `references/platform-aip-mobile-overflow-parity.md` for the measured stage-vs-live example

This mirrors the source `MainFeatureDescription` behavior where the media wrapper owns `style={{ width: `${props.imageWidth}px` }}` rather than letting the flex row stretch the media, but the responsive breakpoint behavior must still be checked separately.

### K4. JSX marker components in an interactive preview section may disappear across a client boundary
A practical finding from `/t/platforms/acp` parity work:
- the route authored ACP feature categories/items as JSX marker components so `page.tsx` kept the real copy/composition readable
- the interactive feature browser was initially a single `"use client"` component that both parsed the marker children and rendered the carousel UI
- on the deployed preview, the browser rendered only empty controls: no category labels, no feature title/body, and `Learn More` fell back to `#`
- root cause: the marker components returned `null`; across the server/client boundary the client parser saw already-rendered `null` children rather than the original marker element tree

Reliable fix pattern:
1. keep route-authored marker JSX in `page.tsx`
2. make the parser module a server component (no `"use client"`)
3. parse marker elements on the server into plain serializable data such as `{ label, items: [{ title, bodyLines, imageSrc, learnMoreHref }] }`
4. pass only that data into a narrow client component that owns `useState`, category switching, carousel dots, previous/next controls, and lazy media rendering
5. update the mirrored structure test to assert both halves of the contract: server parser imports the client widget, and the client widget owns the interactive controls
6. verify the exact Preview Deployment URL in a browser; check that category labels, visible feature title/body, external docs link, and lazy-loaded GIF natural dimensions appear after scrolling

This preserves route-local authoring without losing server-authored semantic children inside a client-only parser.

### K5. When replacing a preview-page YouTube hero embed, preserve measured wrapper geometry and move large video off the repo
A practical finding from `/t/platforms/aip` review/planning work:
- the current stage page uses a YouTube iframe inside `AipHeroVideo()` at `src/components/sections/aip/page.tsx`
- the measured stage hero media box was already stable at `1024x576`
- the risky part was not the layout wrapper, but the media delivery choice (`iframe` to YouTube)

Reliable replacement pattern:
1. measure the current wrapper and iframe/video geometry before proposing changes
2. keep the approved hero wrapper classes, aspect ratio, rounding, and shadow stable unless the user explicitly asks for a layout change
3. replace only the inner media implementation (`iframe` -> self-hosted player)
4. keep only lightweight poster images in the repo under the route-aligned asset root, for example `public/services/aip/hero-video-poster.jpg`
5. host the actual video on a QueryPie-owned storage/CDN origin rather than committing large `.mp4` files into the repo or serving them from generic Vercel-traced public paths
6. prefer HLS (`.m3u8`) with `hls.js` plus MP4 fallback for long-term operation; MP4-only is acceptable for a fast first pass
7. prefer poster-first click-to-play UX with `preload="metadata"`, `playsInline`, normal controls, and no forced sound autoplay by default

Why this matters:
- removes YouTube branding and third-party embed dependence
- avoids bloating git history and deployment artifacts with large binary video files
- preserves the already-accepted hero layout while changing only the delivery mechanism
- generalizes to other corp-web-japan preview routes that may later replace YouTube or external media embeds

See `references/aip-self-hosted-hero-video-pattern.md` for the concrete AIP baseline and the recommended storage/player split.

### L. After parity is proven, clean up by moving layout responsibility into shared primitives instead of stacking more route-level wrappers
A recurrent trap in parity follow-up work:
- first you achieve the right pixels by adding route-local wrappers, duplicated utility classes, or inline styles
- then the rendered result looks correct, but the implementation becomes structurally messy and hard to maintain
- if you keep stacking overrides on top of shared primitives, later cleanup can accidentally re-break computed styles

Important lesson from PR follow-up on shared company page primitives:
- if the target is to remove custom `className` hooks from a shared primitive, do not fix parity regressions by adding new route-level `className`, `contentClassName`, or `contentWidthClassName` overrides
- instead, rename/generalize the primitive to match its real responsibility and encode the allowed differences as semantic presets
- concrete pattern:
  - prefer `CompanyPageLayout` over `CompanyPageBodyLayout` when the wrapper can own hero, form, list, or main content layout, not just post-intro body content
  - prefer `preset="single" | "equalColumns" | "aboutUsHero"` over redundant `columns={...}` plus `layoutPreset="..."`
  - remove primitive-level escape-hatch props like `className?: string`, `contentClassName?: string`, and `contentWidthClassName?: string` once callsites no longer need them
  - if section padding differs for a known layout case, use a narrow semantic prop such as `padding="compactHero"` rather than a raw padding class override
- parity regressions caused by component composition should be fixed by moving JSX structure, not by patching CSS classes:
  - for `/about-us`, keep the H1 and hero body/image layout in the same intro stack so the 50px H1-to-body gap is preserved
  - for `/contact-us`, make the two-column `CompanyPageLayout` wrap the left intro/checklist column and the right form column; do not render a full-width intro above the form grid

Important real finding from the internal MDX list CTA cleanup:
- route-level `className` overrides on top of a shared CTA/button primitive produced duplicated utility classes in the final DOM
- even when computed styles happened to match, the markup/layout quality was still not acceptable
- the clean fix was to move the true default responsibility into the shared primitive and expose narrow hooks for the variant-specific geometry

Important real finding from PR 461 company-page wrapper audit:
- a PR can have zero callsite `className=...` overrides while still leaving the shared primitive API too permissive (`className`, `contentClassName`, `contentWidthClassName` escape hatches)
- when the user's goal is to remove custom className settings, audit both:
  1. actual route callsites that pass custom classes
  2. shared component props that still allow future ad-hoc custom classes
- do not fix structural regressions by adding another custom `className`; first check whether the JSX composition changed relative to the reference layout
- concrete examples:
  - `/about-us`: moving `CompanyPageBodyLayout` outside `CompanyPageIntro` removed the original 50px H1-to-body/image gap; the fix is to restore the composition so the body layout is inside the same stacked intro/hero wrapper, not to add a margin class
  - `/contact-us`: splitting title/lead into a full-width intro above a separate 2-column body pushed the form down about 168px on desktop; the fix is to put the left intro/checklist and right form inside the same 2-column body layout, not to offset the form with custom classes
  - minor differences such as `/certifications` mobile gutter or `/news` 8px bottom padding should be classified separately as common-wrapper policy choices vs strict parity defects

Important real finding from `/t/platforms/aip` value-card parity:
- source components can place major content visually inside an image/card chrome even when the browser snapshot flattens that content into headings and paragraphs
- on live AIP, the `IntroducingQueryPie` value cards used:
  - a gradient parent section
  - white rounded cards with subtle shadow and overflow hidden
  - a title container positioned over the top image
  - white multi-line card titles authored inside that overlay
  - body copy and learn-more action inside the card body
- a preview implementation that simply renders image -> heading below -> paragraph can pass text/section-order checks but still fail visual parity
- another AIP value-card pitfall: the grid row/reveal wrapper can have equal row height while the actual visible white card wrapper still shrinks to content height; measure and fix the `article`/`li` that owns the card chrome, not only the outer grid item
- concrete measured example: live cards were all about `549.63px` high, while stage visible card wrappers were about `485.63px`, `459.63px`, and `433.64px`

Reliable fix pattern:
1. inspect the legacy/source component and CSS, not just the MDX source and browser text snapshot
2. identify whether the title/content is overlaid on media or lives below it
3. encode that ownership in section primitives, e.g. a value-card image component that accepts `children` for the overlay title
4. keep the route page as the copy/composition owner by authoring the multi-line title JSX in `page.tsx`
5. add a structure test that asserts the overlay primitive exists and that route-aligned assets are present under the intended `public/<route-family>/...` namespace

Preferred test assertions for this case:
- source has the route-local CTA links to sibling preview pages
- source does not link back to the upstream URL when a local preview sibling exists
- section module contains the gradient section, value-card link primitive, and overlay class/pattern
- every referenced value/feature media asset exists under the route-aligned public directory

Preferred cleanup pattern after a parity fix stabilizes:
1. identify which values are truly route-specific and which are actually the primitive's responsibility
2. move stable section-level responsibility into the shared primitive itself
   - example: CTA section background, padding, text alignment
3. move stable layout shells into shared helper primitives
   - example: dedicated `ResourceListCtaContent` and `ResourceListCtaCopy`
4. prefer semantic variants/presets over raw class override props when variation is genuinely needed
   - example: `preset="aboutUsHero"` / `preset="equalColumns"` rather than `className="grid ..."`
5. remove unused or unnecessary `className`/`contentClassName`/`contentWidthClassName` props from the shared primitive API after confirming callsites do not need them
6. simplify the route so it authors copy and composition only

Practical heuristic:
- use inline style as a fast parity-debugging tool
- but if the user explicitly asks for markup/layout quality cleanup or custom className removal, do not stop at the working visual result
- refactor the primitive defaults or composition so the final route no longer needs nested anonymous wrappers, duplicated utility stacks, or future escape-hatch class props just to hold the same geometry

## Good implementation pattern for `/t/*` company-info parity pages

For static company-info preview pages such as `/t/about-us`:
- keep copy in `page.tsx`
- use local route-aligned assets under `public/<slug>/...` if that is the repo convention requested by the user
- match the live page's visual structure using browser-measured geometry
- keep the public non-preview redirect route untouched unless explicitly requested

### L2. For pricing/plans widget pages, preserve the upstream component contract, not only route-local copy
A practical finding from `/t/plans` parity work:
- the local route could pass source-structure tests because the visible copy lived in `page.tsx` and the comparison rows were authored directly in JSX
- however, browser-rendered parity still failed because the implementation reinterpreted the upstream pricing widget into generic Tailwind marketing-card/table chrome
- the missed contract came from `../corp-web-app/src/components/widget/pricing/{pricing,product,plan-card}.module.css` and `../corp-web-app/src/components/widget/compare-table/compare-table.module.css`, not from the route page alone

Symptoms:
- text snapshots and route-local tests look correct
- product tabs render as narrow buttons or a generic tab row instead of 50/50 underline tabs
- plan cards render as rounded bordered/shadow cards instead of upstream gradient cards with top-only radius
- plan price is grouped with the title/description when upstream composes it as a separate card child
- feature lists are full-width or border-separated instead of centered at the upstream list width
- comparison table is wrapped in a rounded/shadow panel instead of the upstream flat fixed-width overflow table
- vertical rhythm is much tighter than the upstream widget even though all sections are present

Required workflow for `/ja/plans` / `/t/plans` and similar widget/application-contract pages:
1. classify the page as a widget/application-contract page before applying static marketing route-local authoring rules
2. inspect the upstream route and the full component/CSS chain in `../corp-web-app`, not just the route JSX
3. measure the exact live/stage rendering for tabs, card wrappers, title/price/button/features, and comparison table wrappers/cells
4. preserve the upstream authoring/composition boundary when it encodes visual semantics; route-local JSX readability is secondary to the widget contract
5. add structure tests that pin the visual contract patterns, including positive assertions for upstream-like tabs/card gradients/table shape and negative assertions against generic card/table chrome

Useful regression-test anchors for plans-style pricing pages:
- positive: `border-b-2 border-[#dae1e7]`, `flex-1 cursor-pointer`, large root gap such as `gap-20`, upstream gradient strings for primary/black cards, `rounded-t-[20px]`, fixed feature-list width such as `w-[230px]`, fixed table width such as `w-[1200px]`, flat row borders such as `h-11 border-b border-[#dae1e7]`
- negative: `rounded-[28px] border border-slate-200`, shadowed table wrappers, `bg-slate-50 text-slate-950`, or simplified grid-only card layout such as bare `lg:grid-cols-3`

Practical rule:
- if the upstream page is already a declarative JSX widget, do not treat successful route-local copy ownership as proof of visual parity
- for widget pages, the component/CSS contract is part of the source of truth; test it directly so the same miss does not recur

### L3. For integration-catalog pages, measure the wrapper elements that own the visual chrome
A practical finding from `/t/services/aip/integrations` parity work:
- browser snapshots can make the page look fully correct because all 45 card labels and filter labels are present
- but for pixel parity, you must measure the actual wrapper elements that own background, radius, padding, and grid sizing
- on the live page, the category pill anchors can report transparent backgrounds and zero padding because the pill chrome is applied on the wrapped list item
- if you compare only the anchor geometry/styles, you can falsely conclude the preview pills are wrong even when the wrapper is correct

Required measurement pattern for catalog/list pages:
1. inspect the pill list wrapper and measure the first few `<li>` items, not only the nested anchors
2. inspect the product grid `<ul>` and measure the first few card `<li>` items
3. for each wrapper, compare:
   - top/left
   - width/height
   - background color
   - border radius
   - padding
   - gap
4. then separately compare the nested image size and label text metrics inside each card

Also compare the live interaction/query contract, not only visible filter labels, but classify it by rollout scope:
- on `/t/platforms/aip/integrations`, live category links used numeric query values such as `category=0..9`, while the preview implementation used keyword slugs such as `category=workflow-automation`
- for a `/t/*` preview-tracking issue, do **not** automatically treat live numeric query compatibility as remaining preview work; the preview-local contract may intentionally use semantic keyword keys
- if public rollout is explicitly in scope and existing public URLs/bookmarks must be preserved, then treat the live query contract as a separate public URL-compatibility target
- if a PR adding numeric query compatibility was closed as wrong-scope, do not keep that compatibility as a parity requirement in the preview issue; record it as out of scope or future rollout-only
- when converting route-local category keys to live-compatible values, avoid broad global string replacement: it can corrupt unrelated strings such as asset filenames (`microsoft-365` becoming `4`)
- make the mapping deliberately and re-run the mirrored structure test plus a quick asset-path grep/diff review for every filename-bearing field

Also keep this page-family caveat in mind:
- the preview site's header/footer chrome may intentionally differ from the live `querypie.com/ja` chrome
- in that case, evaluate parity primarily on the migrated body area unless the user explicitly asks for full-page chrome matching
- for `/t/services/aip/integrations`, the meaningful parity target was the body composition: H1, description, category pills, 45-card grid, CTA section, and filter query behavior

## Verification checklist before finalizing

1. `npm run typecheck`
2. `npm run build`
3. restart preview if using `next start`
4. reopen preview URL
5. measure key elements again in browser console
6. confirm live vs preview deltas are materially reduced
7. push to the existing PR branch if this is a follow-up task

## Reporting format to the user

Summarize the parity work in this order:
1. which URLs were compared
2. whether local preview had to be restarted/rebuilt due to stale output
3. which measured live values were used as anchors
4. which body-area elements were changed
5. what remains as minor differences, if any

### When the task is an audit / issue rewrite instead of an implementation PR
Do not preserve every measured difference as an open issue.

A practical lesson from `/t/about-us` parity audit follow-up:
- once the user has supplied policy rules such as
  - default `1200px` width for independent text blocks,
  - shared CTA width is correct by policy,
  - uniform team-card widths are acceptable by policy,
- differences from live that conflict with those policy rules must be reclassified as **non-issues**, not left as lingering "decisions" or "follow-up questions"
- if latest `main` has already absorbed the valid fixes, rewrite the audit around:
  1. resolved items,
  2. non-issues by policy,
  3. any truly remaining narrow question

Practical rule for future parity audits and issue rewrites:
- do not keep stale bullets like "decide whether to match live CTA width" when the user already decided the shared primitive should stay
- do not keep stale bullets like "restore live varied card widths" when the user already decided uniform cards are acceptable
- explicitly separate:
  - actual remaining issues
  - items intentionally removed from concern

### When a repeated route-level width class is only expressing the shared default, move that responsibility into the primitive
Another practical lesson from the same `/t/about-us` follow-up:
- if a reusable wrapper like `AboutUsSectionIntro` is always supposed to use `max-w-[1200px]` for independent text blocks,
- do not keep repeating `className="max-w-[1200px]"` at every route callsite
- move the default width into the primitive itself, and reserve route-level `className` only for true exceptions

This keeps the route readable and makes the policy visible in one place.

## Pitfalls

When the user has already given a governing migration/parity rule, do not reopen it as a fresh design choice in the report.

Important practical lesson from `/t/about-us` audit follow-up:
- if the user already established a rule such as
  - wide standalone text blocks default to `1200px`
  - image+text split layouts are exceptions
  - shared CTA / shared site primitives should remain unless there is a concrete defect
- then the audit report must apply that rule directly
- do **not** rewrite the finding as an open question like:
  - "should we keep shared 1200px CTA or shrink to the live 841px block?"
  - "should we restore live varied-width team cards or keep the 320px grid?"
- if the user's rule already resolves the question, classify it as either:
  - valid defect
  - acceptable adaptation
  - live inconsistency / non-authoritative source behavior

Required classification pattern for this repo/page family:
1. first list the user's explicit policy constraints already given in the conversation
2. for each live-vs-preview difference, ask whether those constraints already decide the outcome
3. if yes, do **not** present it as an open design choice
4. instead classify it explicitly as one of:
   - `actual issue`
   - `acceptable local-site adaptation`
   - `live-side inconsistency / not a migration target`
5. only leave an item open when the user has not already given a rule that settles it

Practical `/t/about-us` examples:
- standalone section intro text at `760px` where no side-by-side media constrains width -> `actual issue` because the user's rule already says `1200px`
- CTA text block wider than the live page but still using the shared `1200px` CTA primitive -> `acceptable local-site adaptation`, not an open choice
- live team cards using mixed widths while stage uses uniform `320px` cards -> not automatically a defect; often `acceptable local-site adaptation` unless the user explicitly prioritizes live visual irregularity

## Pitfalls

- `difference from live, but not clearly a defect`
- `possible live-site implementation quirk / inconsistency`

Do not phrase every numeric delta as a preview defect. If a difference may come from shared preview design primitives, root-font policy, or an inconsistent live implementation, say so directly.

## Audit-only review mode

Use this mode when the user asks for a critical comparison/report first, not an implementation pass yet.

Typical triggers:
- "비교해서 검토해줘"
- "적절히 구현되었는지 보고해줘"
- "기존 UI와 콘텐츠를 그대로 옮겼는지 비판적으로 확인해줘"
- "PR의 Preview Deployment와 stage의 웹페이지 렌더링 결과를 실제 비교해줘"

In this mode:
1. re-state the exact two URLs being compared before drawing conclusions
2. inspect the exact requested stage/preview URL directly; do not substitute a different deployment or PR branch state
3. if the user names a PR rather than a preview URL, get the current Vercel preview URL from `gh pr view <number> --json comments,statusCheckRollup` before comparing
4. identify the routes actually affected by the PR diff and compare those routes, not only `/`
5. compare both content parity and UI/layout parity separately
6. report missing/changed content, structural layout differences, spacing/typography differences, and interaction differences as separate bullets
7. be explicit about severity:
   - blocker: not the same content/structure
   - major: clearly visible layout/asset mismatch
   - minor: small spacing or typography drift
8. end with an overall judgment such as:
   - faithful migration
   - mostly faithful with notable gaps
   - not yet faithful

Important pitfall learned from follow-up sessions:
- if the conversation contains prior implementation or PR-status discussion, do not drift into branch/commit reporting when the current task is an audit of live URLs
- anchor the response to the user's requested URLs and the rendered page comparison first
- for PR preview-vs-stage audits, it is acceptable to use a short Playwright script from the repo root to capture full-page screenshots and DOM geometry for multiple routes; save temporary artifacts under `/tmp/<task-name>` and remove any repo-local helper scripts before finishing
- if the script is stored under `/tmp`, Node may fail to resolve repo-local packages like `playwright`; either run the script from the repo, or use `createRequire('<repo>/package.json')` to resolve `playwright` and other dependencies from the repository installation
- identify affected routes from `gh pr view <number> --json files` before browsing; for shared primitive refactors, compare every changed callsite route, not only the most obvious page
- collect at least desktop and mobile viewport measurements when the PR changes shared page primitives or responsive containers
- useful measured anchors include body height, h1 rect/style, section top/height, section computed padding/background, first paragraphs, key images, form/card wrappers, and changed route-specific content blocks
- when screenshots look nearly identical, compute a pixel-diff summary from the saved screenshots (for example with repo-local `sharp` when Pillow/pixelmatch is unavailable) and report the diff bbox; this quickly distinguishes "body identical, footer shifted" from widespread layout drift
- for contact/form pages, explicitly compare whether the form and intro live in the same grid or whether the preview split them into separate intro + body rows; this can move the form down even when text content is unchanged
- for page-wrapper refactors, compare old wrapper computed padding/gutter against the new shared primitive; small numeric changes like `pb-20` -> `pb-[96px]`, `lg:pb-[128px]` -> `lg:pb-[120px]`, or `px-6` -> `px-[30px]` can cause visible footer shifts, card narrowing, and text rewrapping even when all content is present

### When turning a parity review into a GitHub issue, prefer code/DOM-backed examples over abstract prose
A practical correction from `/t/about-us` parity review work:
- a high-level issue body that only says things like "typography differs" or "layout rhythm is different" can be too abstract for the user to evaluate
- for this user, a useful audit issue should show the disagreement with concrete evidence from:
  - current repo source (`page.tsx` / section component code)
  - live/stage rendered DOM (`outerHTML`, heading tags, measured widths)
- when the issue argues that a difference is an intentional adaptation rather than a bug, show the exact code or DOM shape that creates that adaptation
- when the issue argues that something is a bug, show the exact local code that causes it and the live/stage measured result

### When the goal is UI commonization, do not over-treat stage deltas as parity bugs
A practical correction from PR 461 company-page commonization review:
- the user may ask to compare PR Preview against `stage.querypie.ai` not because stage pixel parity is the goal, but because stage is a useful baseline for detecting unintended visual breakage after commonizing UI primitives
- if the user clarifies that the goal is shared UI consistency, reclassify findings through this lens:
  1. `actual breakage`: overlap, missing content, broken assets/forms, unreadable/narrow content, excessive whitespace, or layout that feels clearly cramped/broken
  2. `commonization follow-up`: small stage deltas that expose a missing semantic spacing/gutter preset
  3. `non-issue`: exact pixel differences that are acceptable because the new shared primitive intentionally standardizes UI
- do not recommend restoring old page-specific wrappers merely to match stage; prefer semantic shared primitive variants only when there is a real remaining layout need
- for GitHub issues from this audit mode, frame the issue around consistent spacing/margin/padding and overly narrow/wide regions, not around making every page match stage exactly
- explicitly list non-issues so future readers do not reopen stable pages or accepted commonization differences
- before classifying a card/gallery page as cramped because its cards are narrower, identify the intended responsive model first:
  - if the design is an equal-grid model where cards divide available viewport width into 1/2/3 columns while maintaining fixed-height rhythm, narrower cards on narrower devices are normal responsive behavior, not automatically a defect
  - judge card/gallery quality by evidence such as unreadable text, broken logo sizing, collapsed vertical balance, awkward row/column rhythm, or clearly excessive inset — not by absolute card width alone
  - if a live-site gutter differs from the local shared primitive gutter across multiple company pages, classify it as a company-page gutter policy difference, not a one-page defect
  - only propose a page-specific gutter preset/wrapper when there is concrete visual breakage on that page; otherwise mark it as non-issue or future policy consideration
- concrete PR 461/issue 468 examples:
  - `/about-us`: no follow-up; stable after refactor
  - `/contact-us`: form/spacing follow-up was handled by PR 467, then removed from remaining work
  - `/certifications`: the initial mobile card/gutter concern was later reclassified as non-issue because the page uses the same broad responsive equal-card-grid model as the live page; the 30px vs ~24px gutter difference is a company-page policy delta, not a certifications-only defect
  - `/news`: desktop CTA offset was only a small list-page spacing-preset signal, not a broken content/layout issue

Recommended issue-writing pattern for parity audits:
- quote the exact local code snippet, for example:
  - `AboutUsSectionIntro className="max-w-[760px]"`
  - `AboutUsLeaderName` rendering `<h3>`
  - shared CTA callsites like `<AipFreeTrialCtaSection />`
- quote the exact live/stage DOM example when available, for example:
  - live `<h4>2017</h4>` vs stage `<h3>2017</h3>`
  - live CTA width `841.11` vs stage CTA width `1200`
- classify each difference as one of:
  1. clear bug / rule violation
  2. intentional adaptation candidate with pros/cons
  3. policy decision needed before implementation

### `/t/about-us` wide body-paragraph rule: treat unnecessary narrowing as an error, not as a styling preference
Another concrete lesson from the same review:
- for this page family, the user explicitly stated that wide explanatory/body paragraphs should default to the full `1200px` content width
- therefore, route-local intro wrappers like `AboutUsSectionIntro className="max-w-[760px]"` in wide body sections should be treated as implementation errors unless the user explicitly requests a narrower exception
- do not frame those narrowed blocks as a neutral "stage adaptation" by default

Practical application on `/t/about-us`:
- the investor intro and timeline intro blocks were both implemented with `max-w-[760px]`
- the team intro block already used `max-w-[1200px]`
- this kind of within-page inconsistency is a strong signal that the narrower blocks are bugs / leftover constraints rather than intentional design

Heuristic for future audits:
- if a broad section-level body paragraph on `/t/about-us` is narrower than the main `1200px` content width, first classify it as a likely error
- only keep it as an adaptation if there is explicit evidence in current code/design direction or the user says that narrower width is intentional

## Pitfalls

- trusting code structure instead of rendered geometry
- assuming `next start` reflects current code without rebuilding
- trusting delayed process watcher notifications as current state
- overfitting to screenshot vision summaries when DOM measurements disagree
- matching text but leaving major size/spacing differences in place
- adding extra card shadows, borders, or wrappers when the live page is flatter

## Done criteria

You are done when:
- the live and preview pages have the same section order
- key body elements have closely matching geometry or visual rhythm
- major images/logos/maps are measured to similar sizes/positions after lazy-loaded media has entered the viewport
- section background bands and vertical spacing materially resemble the live page
- preview has been rebuilt/restarted or deployed and verified in-browser after the final change
- for PR work, the exact Vercel preview deployment URL from the PR comment/check has been opened directly, not inferred from stage or localhost
