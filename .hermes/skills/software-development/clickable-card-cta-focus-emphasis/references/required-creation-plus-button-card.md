# Required-creation plus-button card pattern

Session source: Outbound Agent PR #266, Entity Card Widget visual design.

## Problem

A required-creation card initially used a dashed card with an eyebrow, a pale center `+` marker, explanatory copy, and a separate blue lower `Create` / `만들기` style button.
The user corrected this as the wrong interaction model: the central `+` mark itself should be the add/create button.

## Correct design

- Card keeps the entity/card-type eyebrow at the top, e.g. `Product`.
- Card uses dashed border to communicate an empty slot that must be filled.
- Center `+` cross is the semantic creation button.
- Default state: `+` cross is pale / low contrast.
- Pointer hover or keyboard focus: `+` cross becomes darker and receives clear focus affordance, such as a focus ring.
- No separate lower blue `Create`, `Add`, or `만들기` button.
- Title and description may explain the need, e.g. `Product를 생성해야 함`, but they are not additional button affordances.
- Card-size and layout must not shift between default and hover/focus states.

## Implementation guidance

Preferred semantic shape:

```tsx
<div className="rounded-card border border-dashed ...">
  <div className="eyebrow">Product</div>
  <button
    type="button"
    aria-label="Product 생성"
    className="plus-cross-button text-blue-600/20 hover:text-blue-700 focus-visible:text-blue-700 focus-visible:ring-2 ..."
  >
    <PlusIcon aria-hidden="true" />
  </button>
  <h3>Product를 생성해야 함</h3>
  <p>Campaign을 만들려면 Product가 필요합니다.</p>
</div>
```

If the product wants the whole card to be clickable, the card can enlarge the hit target, but it should not introduce another visible CTA. Preserve the single visible affordance: the center plus-cross button.

## Review checklist

- [ ] No lower `Create` / `Add` / `만들기` button remains.
- [ ] Center `+` is treated as the button/link, not decoration.
- [ ] Default and hover/focus states are both shown or specified.
- [ ] Hover/focus darkens the `+` and provides keyboard-visible focus.
- [ ] Eyebrow still identifies the card/entity type.
- [ ] Dashed border remains stable; card size/layout do not change on focus.
