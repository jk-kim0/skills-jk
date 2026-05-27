---
name: corp-web-japan-jp-font-preload-runtime-verification
description: Verify and fix Japanese font preload behavior in corp-web-japan when source-level preload code does not appear in built or live HTML.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, fonts, preload, nextjs, react-dom, performance, verification]
    related_skills: [systematic-debugging, test-driven-development, corp-web-japan-origin-main-worktree-safety]
---

# corp-web-japan JP font preload runtime verification

Use this when:
- Japanese font optimization work was merged but live behavior does not match the intended preload design
- `src/app/head.tsx` or another source-level preload path appears correct in code review, but the preload is missing in build output or on stage
- you need to validate whether a font hint is really emitted into HTML and whether it changes browser timing

## Core lesson

In this repo on Next.js 16.2.4 / React 19, a source-level preload implementation can exist without appearing in built homepage HTML. Do not trust source inspection alone.

You must verify all three layers:
1. source code
2. built HTML output
3. live browser behavior

## Proven failure pattern

Observed in PR #125 follow-up work:
- `src/app/head.tsx` contained a preload link for `/fonts/PretendardJPSubset-600.woff2`
- the existing source-level regression test passed
- but `.next/server/app/index.html` did not contain that preload
- live `stage.querypie.ai` also did not show the subset preload in DOM/HTML
- result: the representative JP subset font loaded via CSS discovery, not early preload

## Root-cause checklist

### 1. Verify latest main and merged PR implementation
Always start from latest `origin/main` in a fresh worktree.

Read:
- `src/app/layout.tsx`
- `src/app/head.tsx` if present
- `src/app/globals.css`
- relevant tests under `tests/`

Check recent commits touching font loading.

### 2. Verify live browser behavior
On the exact requested environment/page:
- inspect `link[rel="preload"][as="font"]`
- inspect `document.fonts`
- inspect `@font-face` rules from loaded stylesheets
- inspect `performance.getEntriesByType('resource')`

For each relevant font, capture:
- URL
- `initiatorType`
- `duration`
- `startTime`
- `responseEnd`
- `transferSize`
- `encodedBodySize`

Important interpretations:
- `initiatorType: link` means actual preload behavior is visible
- `initiatorType: css` means the file is being discovered through CSS after the page is parsed

### 3. Verify build output, not just source
Run:
- `npm run build`

Then inspect built homepage HTML directly, usually:
- `.next/server/app/index.html`

Search for:
- target preload URL, e.g. `/fonts/PretendardJPSubset-600.woff2`
- `rel="preload"`

If the target preload does not exist in built HTML, the runtime will not behave as intended, regardless of what source files contain.

## Important behavioral finding about subset splitting
Weight-splitting a JP font does not guarantee only one JP file loads.

If the homepage visibly uses multiple weights, the browser will fetch multiple subset files through CSS matching.

### Proven homepage check
Measure actual weight usage in the live page by scanning rendered elements and reading `getComputedStyle(el).fontWeight`.

Check both:
- full page
- initial viewport only

In the proven case:
- the homepage used weights 400 / 500 / 600 in the first viewport
- and 700 elsewhere on the page
- therefore loading 400 / 500 / 600 / 700 subset files was expected behavior, not necessarily a bug

## Recommended implementation fix

### Replace `src/app/head.tsx` preload with `react-dom` `preload()` in `src/app/layout.tsx`

Proven working pattern:
- import `preload` from `react-dom`
- call it inside `RootLayout` before returning HTML

Example:

```tsx
import { preload } from "react-dom";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  preload("/fonts/PretendardJPSubset-600.woff2", {
    as: "font",
    type: "font/woff2",
    crossOrigin: "anonymous",
  });

  return (
    <html lang="ja" className={monaSansFont.variable}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
```

After this change, verify that built HTML actually contains the preload link.

### Why this fix matters
With the proven layout-level runtime preload:
- `/fonts/PretendardJPSubset-600.woff2` appears in built HTML
- live preview shows the preload link
- browser timing shows `initiatorType: link` for the JP 600 subset
- `startTime` and `responseEnd` for the representative JP weight improve substantially

## Testing strategy

### Existing test gap
A source-level test like "`src/app/head.tsx` contains preload markup" is insufficient.
It can pass while the built output is still wrong.

### Better regression test structure
At minimum, update source-level tests to require:
- `preload` imported from `react-dom` in `src/app/layout.tsx`
- layout contains the preload call
- `src/app/head.tsx` is absent if that path is no longer used

If practical, also add a build-output validation step that checks the generated homepage HTML for:
- Mona Sans preload
- JP 600 subset preload
- absence of old `PretendardJPVariable`

## Interpreting results after the fix

What this fix does solve:
- restores actual runtime preload emission for the representative JP subset weight
- makes the representative Japanese font start much earlier

What this fix does NOT automatically solve:
- if the homepage visibly uses several JP weights, the browser will still fetch additional subset files
- therefore total JP font transfer may still be high even after the preload path is fixed

## Recommended next optimization after preload is fixed
If further performance gains are needed:
1. reduce JP weight diversity in the initial viewport
2. move non-essential heavier-weight usage below the fold
3. re-measure the exact preview or stage environment after each change

## Proven validation template for preview/stage
Measure 3 times on the target URL and compare against pre-fix stage baseline.

Useful metrics:
- Mona Sans `startTime`, `duration`, `responseEnd`
- `PretendardJPSubset-600` `startTime`, `duration`, `responseEnd`
- `DOMContentLoaded`
- `load`
- preload links present in DOM
- whether `PretendardJPVariable` still appears

A successful runtime-preload fix should show:
- `/fonts/PretendardJPSubset-600.woff2` in preload links
- `initiatorType: link` for that font
- much earlier `startTime`
- much earlier `responseEnd`

## Done criteria

- latest-main implementation inspected in a fresh worktree
- build output inspected directly
- live browser behavior measured on the requested environment
- representative JP subset font verified as `initiatorType: link`
- source tests updated to reflect the actual chosen runtime mechanism
- PR verification includes explicit HTML-output proof, not just source proof
