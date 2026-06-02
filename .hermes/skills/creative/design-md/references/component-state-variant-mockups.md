# Component state-variant mock-up lessons

Use this reference when a user asks for visual-design mock-ups for component variants in a repo PR.

## Checklist

- Represent every requested variant in the mock-up, not only the visually active/actionable one.
- Put variants side by side with the existing/base component so reviewers can compare continuity and deltas.
- Preserve the base component shell first: footprint, radius, padding, typography, shadow, eyebrow position, preview-slot position, and grid alignment.
- For state-only/empty variants, show status only:
  - no CTA
  - no plus marker
  - no pointer cursor
  - no focus ring that implies action
  - no button-like wrapper around neutral status icons unless the user explicitly asks for it
- For required-creation variants, show a single clear creation affordance and remove any alternate CTA the user rejects.
- If the center plus is the button, do not also add a bottom Create/Make button.

## Icon rendering pitfalls

- A plus/cross built from overlapping horizontal and vertical rectangles makes the intersection visually darker.
- When the user wants a uniform plus/cross color, render it as a single glyph or single vector path/shape.
- On hover/focus, darken the whole plus/cross uniformly.
- Do not add a circular background behind the plus/cross unless requested.
- For a neutral empty/no-item icon, a large muted circle with a single minus mark is often enough; avoid wrapping the minus in a rounded rectangle when the user asks for a simpler mark.

## Markdown design-doc pattern

- Keep the PNG asset repo-tracked and colocated with related design images.
- Add or update a small visual-design Markdown file that records the interaction rules, not just the image.
- Link that file from the parent component design doc and the local UI docs index when one exists.
