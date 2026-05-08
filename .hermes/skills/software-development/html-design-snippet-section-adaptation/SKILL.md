---
name: html-design-snippet-section-adaptation
description: Adapt a user-provided standalone HTML/Tailwind design snippet into an existing React/Next.js section component without importing page-level CDN dependencies.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [html, tailwind, nextjs, react, design-adaptation, section-component]
---

# Adapt a standalone HTML/Tailwind snippet into a repo section component

Use this when the user pastes a full HTML mockup or landing-page snippet but only wants one section or component updated inside an existing repo page.

## When to use
- The user pastes `<!DOCTYPE html> ...` markup as a visual reference
- The repo already has an existing route/page/component structure
- The requested scope is only one section, card, hero, empty-state, CTA, etc.
- The pasted snippet includes CDN scripts, Google Fonts, or icon-font dependencies that should not be copied directly into the repo

## Core rules
1. Extract only the requested section, not the whole pasted page shell.
2. Do not import `cdn.tailwindcss.com`, Google Fonts, or other page-level external dependencies into repo code.
3. Replace external icon-font usage (for example Material Symbols) with inline SVG or existing repo-native icons/components.
4. Keep the current route/page ownership model intact.
   - If the repo wants `page.tsx` thin, update the existing section component instead of rebuilding the whole page from the pasted HTML.
5. Preserve the repo's existing typography/color/token conventions where practical, while matching the requested visual hierarchy.

## Recommended workflow
1. Confirm actual scope from the user request.
   - Whole page?
   - One section only?
   - A hero/empty-state/card only?
2. Inspect the existing component that owns that UI region.
3. Identify snippet parts that are only scaffolding and should be ignored:
   - full `<html>`, `<head>`, nav, footer
   - Tailwind CDN config
   - Google Fonts links
   - duplicate global styles
4. Translate only the relevant section markup into the existing `.tsx` component.
5. Replace icon-font spans like `material-symbols-outlined` with inline SVG if no repo icon primitive already exists.
6. Update structure/source tests so they assert the important copy and visual-structure markers from the new section.
7. Run narrow targeted tests.

## Practical heuristics
- If the pasted code shows a whole page but the user asks for an empty-state box, only migrate the empty-state section.
- If the design relies on a webfont that the repo already controls globally, do not add another font import just to mimic the snippet.
- If the snippet uses very custom theme colors, first map them to the repo's nearest existing slate/neutral tokens unless the user explicitly asks for exact token import.
- If the snippet's icon source is not already in the repo, inline SVG is usually the safest minimal implementation.

## Good output shape
- Existing section component updated
- No new global dependency added
- No copied `<script>` or `<link>` tags
- Tests updated to verify key copy and structural markers

## Example lesson
For a corp-web-japan internal events demo follow-up, the user provided a full HTML page for a "No Upcoming Event" state, but the correct implementation was:
- update only `InternalEventsDemoEmptyState`
- keep the rest of the route unchanged
- replace Material Symbols dependency with inline SVG
- update the narrow component test to match the new copy and structure
