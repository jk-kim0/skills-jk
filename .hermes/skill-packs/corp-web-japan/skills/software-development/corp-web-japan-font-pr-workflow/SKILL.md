---
name: corp-web-japan-font-pr-workflow
description: Create font-related PRs in corp-web-japan using an isolated worktree, open-PR precheck, self-hosted local fonts, and Draft PR + CI verification instead of local dev-server review.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Corp Web Japan Font PR Workflow

Use this when working on font changes in `corp-web-japan`, especially when the change should be isolated from unrelated UI/content work.

## When to use

- The task involves font loading, font fallback order, or typography policy in `corp-web-japan`
- The user asks to compare/align with `../corp-web-app`
- The user wants verification through Draft PR + CI instead of local dev-server preview

## Key repo- and user-specific rules

1. Before making changes, check open PR state first:
   - `gh pr list --state open --json number,title,headRefName,baseRefName,isDraft,updatedAt,url`
2. Use a separate worktree and branch for the font change.
3. Prefer Draft PR + CI verification; do not spend time on local `npm run dev` unless explicitly requested.
4. Do not assume any policy that the Japan site must default to `Pretendard JP`; follow the user's requested visual priority.

## Reference implementation

Use `../corp-web-app` as the structural reference only:
- `src/app/fonts.ts`
- `next/font/local`
- self-hosted font files under assets
- root-level application via layout
- `font-family: inherit` for controls/components that might otherwise fall back to UA defaults

Do NOT copy its font priority blindly. `corp-web-app` uses `Mona Sans -> Pretendard JP`; treat that as one possible policy, not a default requirement for `corp-web-japan`.

## Recommended implementation for a simple priority order

Use this when the user wants a straightforward fallback policy such as:
- `Mona Sans -> Pretendard JP -> system sans`
- or `Pretendard JP -> Mona Sans -> system sans`

### 1. Create isolated worktree

```bash
git fetch origin main
git worktree add -b feat/pretendard-jp-self-hosted ../corp-web-japan-font-pr origin/main
```

### 2. Copy font assets

Copy required font files from `../corp-web-app/src/assets/fonts/` into this repo, e.g.:

```bash
mkdir -p src/assets/fonts
cp ../corp-web-app/src/assets/fonts/PretendardJPVariable.woff2 src/assets/fonts/
cp ../corp-web-app/src/assets/fonts/Mona-Sans.woff2 src/assets/fonts/
```

### 3. Keep layout simple

For simple fallback ordering, you do not need `next/font/local` or per-font variables. Keep `src/app/layout.tsx` simple:

```tsx
<body className="font-sans antialiased">{children}</body>
```

### 4. Define a shared family in `src/app/globals.css`

- Remove external font imports (`Google Fonts`, jsDelivr Pretendard, etc.)
- Define both self-hosted files under one custom family name
- Put the font file you want first in the `@font-face` order
- Point `--font-app-sans` at that shared family

Example:

```css
@font-face {
  font-family: "QueryPie Sans";
  src: url("../assets/fonts/Mona-Sans.woff2") format("woff2-variations");
  font-display: swap;
  font-style: normal;
  font-weight: 100 900;
}

@font-face {
  font-family: "QueryPie Sans";
  src: url("../assets/fonts/PretendardJPVariable.woff2") format("woff2-variations");
  font-display: swap;
  font-style: normal;
  font-weight: 45 920;
}

:root {
  --font-app-sans:
    "QueryPie Sans",
    "Hiragino Sans",
    "Yu Gothic",
    "Meiryo",
    "Avenir Next",
    "Segoe UI",
    "Helvetica Neue",
    Arial,
    sans-serif;
}
```

### 5. Force controls to inherit

To avoid UA/default control fonts showing up differently from body copy:

```css
body,
button,
input,
select,
textarea {
  font-family: inherit;
}
```

## Important typography findings

### If you use `next/font/local` variables, scope them on `html`, not only on `body`

Experiential finding from the inline-link/font debugging work:
- If `globals.css` builds `--font-app-sans` from `var(--font-mona-sans), var(--font-pretendard-jp), ...`
- and the `next/font/local` variable classes are attached only on `body`
- then article/body text can collapse to a fallback serif such as `Times`, even when the page visually looks otherwise fine at first glance.

Safe pattern:

```tsx
<html lang="ja" className={`${monaSansFont.variable} ${pretendardJPFont.variable}`}>
  <body className="font-sans antialiased">{children}</body>
</html>
```

Avoid this pattern:

```tsx
<html lang="ja">
  <body className={`${monaSansFont.variable} ${pretendardJPFont.variable} font-sans antialiased`}>
    {children}
  </body>
</html>
```

Reason:
- the app sans token is resolved above normal body descendants
- keeping the font variables on `html` makes the Tailwind `font-sans` stack stable for body copy, headings, and inline links
- adding an inline `style={{ fontFamily: ... }}` on `html` is not a sufficient substitute if `body` still resolves `font-sans` through the broken variable chain

Verification tip:
- Check computed `font-family` in the browser on article body text and external inline links.
- If you see `Times`, the variable scope is still wrong.


### Prefer the simple fallback order unless the user explicitly wants script-based splitting

Experiential finding from this task:
- The user ultimately preferred a simpler outcome over a more technically precise script-splitting setup.
- For stakeholder-facing review, the visual result matters more than detailed font-configuration mechanics.
- If the user asks only for a priority order, use a plain fallback order first.

### Plain fallback order is usually the best default

If the order is:
- `Mona Sans -> Pretendard JP -> system sans`

then the implementation stays simple and predictable.
- Latin/alphanumeric content naturally tends toward Mona Sans.
- Japanese content falls back to Pretendard JP.
- No `unicode-range` setup is needed.

This is the preferred simple implementation when the user does not want extra complexity.

### When `Pretendard JP -> Mona Sans` is used

If the font order is:
- `Pretendard JP -> Mona Sans -> system sans`

then in practice most common text will still render in `Pretendard JP`, including:
- ASCII uppercase/lowercase
- digits
- common punctuation
- common arrows and symbols

Direct font-file comparison showed that `Mona Sans` adds almost nothing as a visible fallback for standard site copy when `Pretendard JP` comes first. The notable extra glyphs found in Mona Sans but not Pretendard JP were limited to characters like:
- `☺`
- `☹`
- `ﬂ`

So Mona Sans as a second fallback will almost never visibly appear for normal website copy.

### Only use `unicode-range` for explicit script-aware behavior

If the user explicitly wants:
- Pretendard JP for Japanese text
- Mona Sans for non-Japanese alphanumeric text

then a plain fallback order is not enough when `Pretendard JP` comes first.
In that case, use self-hosted `@font-face` rules with a shared family name plus `unicode-range`.

However, avoid this by default because it adds complexity and may not match the user's preference for a simpler, stakeholder-friendly solution.

### Mona Sans hosting

`Mona Sans` is not a browser/system default font. If used in this repo, it must be explicitly loaded. Preferred approach in this repo: self-host `Mona-Sans.woff2`.

## Verification workflow

Run CI-style checks locally, then open/update a Draft PR and rely on GitHub CI as the main verification path:

```bash
npm ci
npm run test:ci
npm run build
```

## PR workflow

1. Commit with an English message.

For exploratory work with multiple intermediate commits, squash before handing off:

```bash
git fetch origin main
BASE=$(git merge-base HEAD origin/main)
git reset --soft "$BASE"
git commit -m "feat: update Japanese site font priorities"
git push --force-with-lease origin <branch>
```

2. Push the branch if needed.

3. Open or update a Draft PR.

For stakeholder-facing font PRs, keep the PR title and description short and non-technical.

Good example title:

```text
Refine font priorities for Japanese pages
```

Good example description:

```text
## Summary
- updated the site font setup for Japanese pages
- keep Japanese text aligned with Pretendard JP
- let English letters and numbers feel closer to Mona Sans
- keep the change isolated in a separate PR for easier review

## Verification
- `npm run test:ci`
- `npm run build`
```

## Pitfalls

- Do not assume a merged PR shown as `closed` is unmerged; check `merged`/`mergedAt`
- Do not rely on local dev-server screenshots as the main approval path when the user asked for Draft PR + CI
- Do not expect Mona Sans fallback to affect normal English/digit rendering when Pretendard JP is first
- If you need Mona Sans to be visible, apply it intentionally to specific selectors instead of fallback order
