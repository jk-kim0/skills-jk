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

### 4.1 For exact cross-URL browser comparisons, normalize viewport with emulation, not only window resize
A useful practical lesson from preview-vs-stage parity verification:
- page window resize alone may still leave slightly different `innerWidth` values across tabs/pages
- those small viewport mismatches can create false left-offset differences in otherwise identical layouts
- before trusting geometry deltas, explicitly verify `window.innerWidth`, `window.innerHeight`, and `devicePixelRatio` on both pages

Preferred method in DevTools-based verification:
- apply the same emulated viewport to both pages (for example `1440x2200x2`)
- then confirm with browser evaluation that both pages report the same `innerWidth`, `innerHeight`, and DPR
- only after that should you compare `getBoundingClientRect()` numbers or full-page screenshots

Practical rule:
- prefer viewport emulation over plain window resizing when the task is "are these two rendered pages identical?"
- if a first pass shows small but systematic horizontal offsets, re-run after emulation before concluding there is a real layout mismatch

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

### C1. Before changing image corner radius, verify whether the asset file already contains baked-in rounded transparency
A practical `/t/about-us` finding:
- the hero image looked more rounded in preview than on the live page
- the initial assumption was that the wrapper radius needed tuning
- but the actual cause was that the PNG asset itself already had subtle rounded transparent corners
- adding an extra wrapper radius (`rounded-*` + `overflow-hidden`) made the corners look doubly rounded and visually too soft

Practical rule:
- when matching image corner radius, do not inspect only the wrapper's computed `border-radius`
- also verify whether the image file already encodes corner transparency or anti-aliased rounded edges
- if the asset already contains the intended subtle rounding, prefer removing the extra wrapper radius and background chrome rather than stacking another rounded mask on top

Useful verification methods:
1. inspect the DOM ancestor chain around the image and compare live vs preview wrapper radius/overflow
2. inspect the image asset itself for alpha in the corners
3. if needed, decode the PNG and sample corner alpha values to confirm whether transparency is baked in

Practical heuristic:
- if the PNG corners are transparent at the outermost pixels and become fully opaque only a few pixels inward, the visible rounding may be coming from the asset, not the wrapper
- in that case, wrapper `rounded-*` usually exaggerates the curve and should be removed for parity

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

### E1. For corp-web-japan preview routes, body parity can matter more than shared local header/footer parity
A practical lesson from `/t/about-us` follow-up work:
- the local preview route may intentionally keep the repo's shared `SiteHeader` and `SiteFooter`
- the upstream live page may use a different cross-site header/footer implementation
- if the user's complaint is specifically that the page implementation "looks too different" from the source page, the fastest and usually correct target is the page body area, not a full chrome rewrite

Practical rule:
- first classify whether the mismatch is in global chrome or in the page body
- if the request is about the page implementation and not the site shell, prioritize matching:
  - hero typography and hero media geometry
  - section heading typography
  - body paragraph line-height and weight
  - section spacing rhythm
  - card/grid treatment inside the page body
- only widen scope into shared header/footer replacement if the user explicitly asks for full-page chrome parity

### E2. When the live page uses a strong repo-local house pattern for the first visible section, measure that internal reference page and reuse its spacing rhythm
A useful `/t/about-us` lesson:
- the upstream page alone may not be the best source for the exact top-of-page spacing once the preview route lives inside the local corp-web-japan shell
- for the first visible section after the local header, an existing local route such as `/news` can provide the correct house-style spacing anchor

Practical rule:
- if the mismatch is specifically the gap from the local site header to the page title or the title block rhythm inside the first section, measure an already-approved local route with the same shell
- copy the local section/container rhythm first, then continue matching the rest of the body to the upstream page

Typical values to compare:
- first section top padding
- first section bottom padding
- title font size / line height / weight
- inner container max width

Why:
- this avoids overfitting the top spacing to an upstream shell that the preview route is not actually using
- it produces better visual parity inside the local site chrome while preserving upstream body intent

### E3. For partner/investor logo rows, prefer natural-width flex spacing measured from the live page instead of equal-width grid distribution
A recurring mismatch on marketing/company pages:
- the preview can look too loose or too synthetic when logos are distributed through equal-width grid columns
- the live page may instead use natural logo widths with a specific measured horizontal gap

Practical rule learned from `/t/about-us`:
- measure the actual live horizontal gaps between named logos
- if the preview gaps are materially wider, switch the row to `flex` with natural image widths and an explicit `gap-x` close to the live measurement
- keep `justify-center` and allow wrapping only as needed

Why:
- equal-width grid tracks often exaggerate whitespace around narrow logos
- natural-width flex spacing usually matches the visual density of the live page much more closely

### E4. For timeline/history sections, do not assume generic card separators; verify whether the live page uses a left vertical rule with content offset
A practical `/t/about-us` finding:
- the preview timeline initially used row separators/dividers
- the live page visually communicated the sequence with a left vertical rule and content indented to the right

Practical rule:
- inspect the live section structure and not just the text order
- if the visual cue is a single left rule, rebuild the timeline around that cue rather than stacking horizontal separators between items
- measure indentation and vertical spacing after the structural switch

Why:
- timeline parity is often dominated by the organizing line rather than by typography alone
- getting the structural cue wrong makes the whole section feel like a different design even when the copy matches

### E5. For leadership/profile card parity, measure content usage across the full column width before assuming the problem is only image sizing
A key late-stage `/t/about-us` lesson:
- leadership cards can look visibly narrower than the live page even when the outer grid column width is technically correct
- the real cause may be inner `max-w-*` wrappers on the image or text block that prevent the card from using the full available column width

Practical rule:
- measure all of these separately on both live and preview:
  - outer card width
  - image wrapper width
  - image rendered width/height
  - text block width
  - social-link wrapper width and alignment
  - social icon width/height
- if the preview card reads too narrow, remove unnecessary inner `max-w-*` constraints before changing the grid itself
- make the image wrapper and text block `w-full` when the live card uses the full column more evenly

For social/profile links like LinkedIn:
- do not assume a tiny inline icon at the left edge is correct
- measure whether the live page places the social icon/link at the right edge of the info block
- if so, use a full-width link wrapper with end alignment (for example `flex w-full justify-end`) and match the icon size more closely to the live page

Why:
- many apparent grid-width problems are actually inner-content-width problems
- fixing the icon anchor position and removing narrow inner wrappers can materially improve perceived parity without redesigning the card grid

### E6. If a parity page later needs to align with site-wide design-system defaults, prefer the repository's shared text-color convention over route-local custom hex values
A practical `/t/about-us` follow-up lesson:
- parity work against the upstream page can temporarily introduce route-local custom text colors such as `#24292F` and `#57606A`
- later, the user may explicitly decide that whole-site consistency matters more than preserving that route as a one-off visual exception
- in this repository, the stable shared convention is:
  - route-level `main`: `text-slate-950`
  - ordinary descriptive/body/secondary copy: `text-slate-600`

Practical rule:
- when the user asks to stop treating a parity page as an exception, remove route-local custom hex text colors from that route
- normalize primary headings / names / labels back to `text-slate-950`
- normalize descriptive and secondary copy back to `text-slate-600`
- if the route currently repeats those values many times, consolidate them into local semantic class constants first, then switch the constants to the shared site defaults

Why:
- it keeps one preview/static page from drifting away from the site's overall visual system
- it makes later maintenance easier because the page follows the same color hierarchy as `/news`, `/whitepapers`, the top page, and solution pages
- it documents that parity work can be intentionally superseded by an explicit user request for design-system consistency

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
- also distinguish carefully between author/token values shown in CSS rules and the final computed value the browser actually renders

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

### K. For follow-up parity requests, prefer existing shared CTA primitives over route-local one-off CTA markup
A recurring follow-up pattern on preview/static marketing pages:
- the initial parity fix may handcraft a route-local CTA section because it is faster for first-pass visual alignment
- later the user may ask to reuse an existing CTA section/button already used elsewhere in the repo

Practical rule learned from `/t/about-us` follow-up work:
- before keeping a custom CTA block, inspect whether the repo already has a visually compatible shared CTA composition
- for corp-web-japan, check `/internal/mdx-list-demo` and `src/components/sections/resource-list-section.tsx`
- if the desired treatment matches that internal demo, prefer reusing:
  - `ResourceListCtaSection`
  - `ResourceListCtaContent`
  - `ResourceListCtaCopy`
  - `ResourceListCtaTitle`
  - `ResourceListCtaDescription`
  - `ResourceListCtaActions`
  - `BrandGradientCtaButton`
- keep the page-specific CTA copy in the route, but swap the surrounding CTA shell/button to those shared primitives

Why:
- this preserves visual consistency with the repo's established CTA treatment
- it reduces route-local duplicated gradient-button/spacing markup
- it aligns with the user's preference for reusing existing components when a matching one already exists

### K1. If those CTA primitives are promoted out of a resource-list-specific module, prefer a narrowly generic "simple CTA" naming scheme
A practical abstraction/naming lesson from the `/internal/mdx-list-demo` CTA refactor follow-up:
- the old names like `ResourceListCtaSection` were too resource-list-specific for a plain marketing CTA block
- a fully broad wrapper name like `CtaSection` can also feel too generic if the repo may later accumulate several CTA families

Preferred naming pattern in this repo for this specific primitive family:
- file path: `src/components/sections/simple-cta-section.tsx`
- wrapper section primitive: `SimpleCtaSection`
- keep the inner child primitives short and generic:
  - `CtaContent`
  - `CtaCopy`
  - `CtaBox`
  - `CtaTitle`
  - `CtaDescription`
  - `CtaActions`
  - `CtaButton`

Practical rule:
- if you extract a simple marketing CTA shell out of a more specific module, prefer `SimpleCtaSection` as the exported section wrapper name rather than `CtaSection`
- keep the child building-block names unchanged unless there is a concrete collision
- when renaming the file, update structure tests so they assert imports from `@/components/sections/simple-cta-section`

Why:
- this keeps the CTA family reusable without pretending it is the only CTA abstraction the repo will ever need
- it matches the user's preference for a more concrete, moderately scoped component name
- it avoids over-coupling a generic CTA shell to a resource-list domain name

### L. If the target visual icon is not available as a standalone asset, search sibling repos for the icon component source and extract it into a route-aligned local asset
A practical parity/migration issue on static preview pages:
- a page may need a tiny brand/social icon that is currently inlined in JSX or only exists in another repo as a React icon component
- searching only for `*.svg` can fail even though the real SVG path data exists in source form elsewhere

Practical rule learned from `/t/about-us` LinkedIn follow-up work:
- after failing to find a standalone SVG file, search sibling repos such as `../corp-web-app` and `../corp-web-contents` for icon component names like `linkedin.icon.tsx`
- if the icon exists only as a React component, extract its SVG path into a local static file under the route-aligned asset root, for example `public/about-us/linkedin.svg`
- then update the route to use the local static asset instead of keeping an ad hoc inline SVG implementation

Why:
- it keeps preview-page assets self-contained under the route-aligned public path
- it preserves parity with existing upstream icon artwork instead of redrawing or approximating the icon
- it reduces duplicated inline SVG code in the route file

### M. When users ask to normalize executive/team portrait cards, use a uniform image frame rather than preserving each source image's natural rendered size
A common late-stage parity follow-up:
- the first parity pass may intentionally preserve natural portrait dimensions because the live page uses mixed widths/heights
- the user may then explicitly prefer consistency over that mixed natural sizing

Practical rule learned from `/t/about-us` follow-up work:
- if the user asks for all leadership/profile images to be the same size, switch to a shared card frame such as:
  - fixed max width
  - `aspect-square`
  - `overflow-hidden`
  - rounded corners
  - `object-cover object-top`
- keep the profile text block width aligned with that image frame so each card reads as a consistent unit

Why:
- this resolves the user's visual concern directly instead of preserving upstream asymmetry
- it is a reusable pattern for leadership/team sections on static marketing pages where card consistency matters more than exact source-image geometry

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
