# Outbound Agent Entity Card: empty/status vs required creation

Use this reference when a Product Owner asks to reflect a UI design decision for Entity Card-style placeholders or empty slots.

## Decision pattern

A visually empty card slot can mean two different product states and should not be collapsed into one generic empty card:

1. State-only / no-action state
   - Labels such as `해당 항목 없음`, `비어 있음`.
   - Communicates that the current slot, lane, Drop Zone, or list has no item to show.
   - Does not imply the user must do anything.
   - Avoid plus markers, primary buttons, action verbs, drag handles, selection affordance, or detail actions.
   - Use muted border, neutral icon, low-emphasis status label, and optional reason text.

2. Required-creation state
   - Labels such as `추가해야 함`, `생성해야 함`.
   - Communicates that the setup flow cannot be completed until a new entity is added or created.
   - Should strongly express the missing required object and the next action.
   - Use plus icon or creation marker, dashed border, action-oriented title, primary button/link, and optionally make the card body the create action surface.
   - The card itself is not an Entity Card yet and should not expose selected/included/excluded/primary roles.
   - Replace it with the created Entity Card after creation succeeds.

## Documentation workflow

- Treat this as a Product Owner UI decision when the user states the intended distinction directly.
- If `docs/ui/entity-card-widget.md` or another UI doc is the canonical design surface, update that document directly rather than forcing a new OpenSpec change.
- Still use the same discipline as OpenSpec decisions: record `Status: Accepted`, rationale, accepted interactions, state model/API impact, and non-goals.
- For docs-only Outbound Agent work, use repo-local `.worktrees/`, start from latest `origin/main`, commit, push, and open a PR; `git diff --check` is sufficient lightweight verification unless the user asks for local build/test.

## Pitfalls

- Do not add CTA affordance to a state-only empty/no-item card.
- Do not make a required-creation placeholder selectable or draggable as if it were a real entity.
- Do not use the same label/copy for passive absence and required setup; the difference is the user's obligation to act.
