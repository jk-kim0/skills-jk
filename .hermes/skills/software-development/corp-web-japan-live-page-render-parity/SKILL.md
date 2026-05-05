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

### C. Remove decorative wrappers if live is flatter
If the preview wraps a map or media asset in a padded rounded panel but the live page presents the asset flat/full-width, remove the wrapper rather than endlessly tweaking padding.

### D. Natural image sizes may matter more than neat symmetry
For people/team sections, live may intentionally use different portrait sizes per column. If the preview forces equal card widths/heights, parity can look wrong even though the grid is technically cleaner.

### E. Keep hero title structure separate from body columns when live does
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

### J. After parity is proven, clean up by moving layout responsibility into shared primitives instead of stacking more route-level wrappers
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
