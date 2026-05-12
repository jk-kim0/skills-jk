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

### L. After parity is proven, clean up by moving layout responsibility into shared primitives instead of stacking more route-level wrappers
A recurrent trap in parity follow-up work:
- first you achieve the right pixels by adding route-local wrappers, duplicated utility classes, or inline styles
- then the rendered result looks correct, but the implementation becomes structurally messy and hard to maintain
- if you keep stacking overrides on top of shared primitives, later cleanup can accidentally re-break computed styles

Important real finding from the internal MDX list CTA cleanup:
- route-level `className` overrides on top of a shared CTA/button primitive produced duplicated utility classes in the final DOM
- even when computed styles happened to match, the markup/layout quality was still not acceptable
- the clean fix was to move the true default responsibility into the shared primitive and expose narrow hooks for the variant-specific geometry

Preferred cleanup pattern after a parity fix stabilizes:
1. identify which values are truly route-specific and which are actually the primitive's responsibility
2. move stable section-level responsibility into the shared primitive itself
   - example: CTA section background, padding, text alignment
3. move stable layout shells into shared helper primitives
   - example: dedicated `ResourceListCtaContent` and `ResourceListCtaCopy`
4. expose narrowly scoped override props on reusable controls instead of appending conflicting utility classes
   - example: `geometryClassName`, `labelClassName`, `iconWrapClassName`, `iconClassName` on a CTA button primitive
5. simplify the route so it authors copy and composition only

Practical heuristic:
- use inline style as a fast parity-debugging tool
- but if the user explicitly asks for markup/layout quality cleanup, do not stop at the working visual result
- refactor the primitive defaults so the final route no longer needs nested anonymous wrappers or duplicated utility stacks just to hold the same geometry

## Good implementation pattern for `/t/*` company-info parity pages

For static company-info preview pages such as `/t/about-us`:
- keep copy in `page.tsx`
- use local route-aligned assets under `public/<slug>/...` if that is the repo convention requested by the user
- match the live page's visual structure using browser-measured geometry
- keep the public non-preview redirect route untouched unless explicitly requested

### L2. For integration-catalog pages, measure the wrapper elements that own the visual chrome
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

Also keep this page-family caveat in mind:
- the preview site's header/footer chrome may intentionally differ from the live `querypie.com/ja` chrome
- in that case, evaluate parity primarily on the migrated body area unless the user explicitly asks for full-page chrome matching
- for `/t/services/aip/integrations`, the meaningful parity target was the body composition: H1, description, category pills, 45-card grid, and CTA section

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

## Decision discipline for corp-web-japan parity audits

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

In this mode:
1. re-state the exact two URLs being compared before drawing conclusions
2. inspect the exact requested stage/preview URL directly; do not substitute a different deployment or PR branch state
3. compare both content parity and UI/layout parity separately
4. report missing/changed content, structural layout differences, spacing/typography differences, and interaction differences as separate bullets
5. be explicit about severity:
   - blocker: not the same content/structure
   - major: clearly visible layout/asset mismatch
   - minor: small spacing or typography drift
6. end with an overall judgment such as:
   - faithful migration
   - mostly faithful with notable gaps
   - not yet faithful

Important pitfall learned from follow-up sessions:
- if the conversation contains prior implementation or PR-status discussion, do not drift into branch/commit reporting when the current task is an audit of live URLs
- anchor the response to the user's requested URLs and the rendered page comparison first

### When turning a parity review into a GitHub issue, prefer code/DOM-backed examples over abstract prose
A practical correction from `/t/about-us` parity review work:
- a high-level issue body that only says things like "typography differs" or "layout rhythm is different" can be too abstract for the user to evaluate
- for this user, a useful audit issue should show the disagreement with concrete evidence from:
  - current repo source (`page.tsx` / section component code)
  - live/stage rendered DOM (`outerHTML`, heading tags, measured widths)
- when the issue argues that a difference is an intentional adaptation rather than a bug, show the exact code or DOM shape that creates that adaptation
- when the issue argues that something is a bug, show the exact local code that causes it and the live/stage measured result

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
- major images/logos/maps are measured to similar sizes/positions
- section background bands and vertical spacing materially resemble the live page
- preview has been rebuilt/restarted and verified in-browser after the final change
