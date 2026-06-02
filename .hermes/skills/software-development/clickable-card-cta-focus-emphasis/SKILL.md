---
name: clickable-card-cta-focus-emphasis
description: Make an entire card clickable without nested links, while preserving a CTA-like visual affordance and adding strong focus-visible emphasis to the CTA when the parent link is focused.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ui, accessibility, nextjs, link-card, focus-visible, testing]
---

# Clickable card with CTA focus emphasis

Use this when:
- the user wants the whole card / hero block clickable
- the card currently has an inner CTA link/button
- nested interactive elements would be invalid or awkward
- keyboard focus should make the CTA area visibly stand out
- a placeholder / empty-slot / required-creation card needs one central CTA affordance, such as a plus-cross button

## Pattern

1. Make the outer card the only real link
- Wrap the full card in a single `Link`
- Do not keep an inner `Link` inside it

2. Keep the CTA as a visual affordance only
- Replace the inner CTA link/button with a non-interactive `span` or similar visual element
- Preserve its label and button-like styling

3. Use parent group focus state to emphasize the CTA
- Put `group` on the outer `Link`
- Add a strong `focus-visible` ring to the outer `Link`
- Use `group-focus-visible:*` classes on the CTA visual element so it becomes more obvious when the card link is keyboard-focused
- Good emphasis examples:
  - darker CTA background
  - ring on CTA
  - ring offset for contrast
  - slight image scale-up on focus as well as hover

## Recommended class pattern

Outer link:
- `group block ... focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-4 focus-visible:ring-offset-white`

CTA visual element:
- `group-hover:bg-slate-800 group-focus-visible:bg-slate-900 group-focus-visible:ring-2 group-focus-visible:ring-slate-900 group-focus-visible:ring-offset-2 ...`

Optional image polish:
- For a single outer-link card pattern: `group-hover:scale-[1.02] group-focus-visible:scale-[1.02]`
- For an absolute overlay-link / separated-CTA pattern, also include plain focus on the overlay trigger when needed:
  - `peer-hover:scale-[1.02] peer-focus:scale-[1.02] peer-focus-visible:scale-[1.02]`
- Practical lesson: with an overlay `Link`, relying only on `peer-focus-visible` can make the image scale feel missing in some focus flows; adding `peer-focus` restores the expected box-focus image emphasis.

## Variant: required-creation plus-cross button card

Use this variant when a card represents a required creation/addition slot and the user wants the center `+` mark itself to be the creation control.

Pattern:
1. Keep the card shell visually consistent with real entity cards
   - same radius and general card proportions
   - dashed border to signal an unfilled slot
   - preserve the card-type eyebrow, such as `Product` or `Contact List`
2. Make the center `+` cross the only visible creation affordance
   - do not add a separate lower primary button such as `Create`, `Add`, or `만들기`
   - title/description copy can explain what needs to be created, but should not introduce another button-shaped CTA
3. Style default vs hover/focus explicitly
   - default: low-contrast, pale `+` cross so it reads as an available empty slot
   - hover/focus: darken the `+` cross and add a focus-visible ring or equivalent clear focus affordance
   - keep layout and card size stable between default and focus states
4. Decide click target deliberately
   - the center `+` should be the semantic button/link
   - the surrounding card may be expanded as a larger hit target only if it does not add a second visible affordance

Pitfall:
- Do not treat a low-contrast `+` marker as merely decorative if the user asked for the plus itself to perform the create/add action. In that case, the plus is the button and the design should not also show a separate blue `Create` / `만들기` button.

See `references/required-creation-plus-button-card.md` for the Outbound Agent Entity Card Widget case that introduced this pattern.

## Alternate pattern: separate box-link focus from CTA focus

Use this variant when the user explicitly wants:
- the whole card area clickable
- a real CTA link/button that remains separately interactive
- box-level hover/focus and CTA-level hover/focus to behave differently
- box focus to NOT trigger CTA focus styling

Pattern:
1. Use an absolute overlay `Link` for the whole card
   - e.g. `absolute inset-0 z-0`
2. Put the visible card content in a higher layer
   - e.g. `relative z-10`
3. Set the content wrapper to `pointer-events-none`
4. Give only the CTA element `pointer-events-auto`
5. Keep the CTA as a real `Link`
6. Style box focus on the overlay link only
   - e.g. outer `focus-visible:ring-*`
7. Style CTA hover/focus on the CTA link only
   - do NOT use `group-focus-visible:*` from the box link when the user wants interaction separation

Recommended interaction split:
- box hover/focus may slightly scale the image or show a card outline
- CTA hover/focus may use its own stronger visual treatment such as blue background, blue glow shadow, and slight scale-up
- if the user asks to avoid box-focus affecting CTA, remove CTA ring/glow classes tied to the outer card focus state

Practical class ideas for separated CTA emphasis:
- stronger bright-blue example:
  - CTA hover: `hover:bg-blue-600 hover:shadow-[0_14px_28px_rgba(37,99,235,0.32)] hover:scale-[1.03]`
  - CTA focus: `focus-visible:bg-blue-600 focus-visible:shadow-[0_14px_28px_rgba(37,99,235,0.32)] focus-visible:scale-[1.03] focus-visible:outline-none`
- subtler dark-blue example when the bright glow feels too loud:
  - CTA hover: `hover:bg-blue-700 hover:shadow-[0_12px_24px_rgba(30,58,138,0.22)] hover:scale-[1.03]`
  - CTA focus: `focus-visible:bg-blue-700 focus-visible:shadow-[0_12px_24px_rgba(30,58,138,0.22)] focus-visible:scale-[1.03] focus-visible:outline-none`
- near-black navy example when the user wants the glow even less saturated / less bright:
  - CTA hover: `hover:bg-[#1e2f4d] hover:shadow-[0_10px_20px_rgba(30,58,138,0.16)] hover:scale-[1.03]`
  - CTA focus: `focus-visible:bg-[#1e2f4d] focus-visible:shadow-[0_10px_20px_rgba(30,58,138,0.16)] focus-visible:scale-[1.03] focus-visible:outline-none`
- specific dark-blue accent example when the user wants a clearer blue that still feels close to black:
  - CTA hover: `hover:bg-[#1E3A8A] hover:shadow-[0_10px_22px_rgba(30,58,138,0.20)] hover:scale-[1.03]`
  - CTA focus: `focus-visible:bg-[#1E3A8A] focus-visible:shadow-[0_10px_22px_rgba(30,58,138,0.20)] focus-visible:scale-[1.03] focus-visible:outline-none`
  - practical note: this keeps the blue visible without drifting into a bright/loud electric-blue CTA
- Box focus remains on the overlay link, not the CTA
- If the user explicitly asks to remove the CTA ring, remove ring-based CTA emphasis entirely and rely on background + shadow + slight scale only.

Important implementation detail for reliable image scale with an absolute overlay link:
- `peer-hover:*` / `peer-focus:*` directly on a nested `Image` can be unreliable or visually appear broken depending on the rendered wrapper structure
- a more robust pattern is to put the hover/focus selector on the visible content wrapper and target a named image class with an arbitrary selector
- example:
  - content wrapper: `peer-hover:[&_.featured-event-hero-image]:scale-[1.02] peer-focus:[&_.featured-event-hero-image]:scale-[1.02] peer-focus-visible:[&_.featured-event-hero-image]:scale-[1.02]`
  - image: `className="featured-event-hero-image ... transition-transform duration-500"`
- this is especially useful when the user reports that box-focus image scale 'seems missing' even though peer classes exist in the code

Copy/content guardrail:
- Do not rename user-facing eyebrow / CTA-adjacent copy just because the interaction model changed.
- If the user or current route already specifies a label like `Upcoming Event`, preserve that exact wording unless the user explicitly asks for a copy change.
- In review follow-up work, treat accidental copy rewrites inside interaction refactors as regressions to undo.

## Why

This avoids:
- invalid nested links
- inconsistent click targets
- weak keyboard focus discoverability
- unwanted coupling where box focus incorrectly makes the CTA look focused

And preserves:
- full-card clickability
- a clear CTA affordance
- accessible focus feedback
- the option to separate box interaction from CTA interaction when the user explicitly wants that behavior

## Testing checklist

Add/update source-structure tests to confirm:
- the component renders a single outer `Link` using `href`
- there is no nested `<Link ... <Link ...>` pattern
- the outer link has `focus-visible` ring classes
- the CTA visual element has `group-focus-visible` emphasis classes
- any expected hover/focus image scale classes are present

## Practical note

If the card is converted to a single link, treat the CTA as presentation, not as a second interactive control. The interaction model should be: one card, one link, stronger internal CTA emphasis on focus.
