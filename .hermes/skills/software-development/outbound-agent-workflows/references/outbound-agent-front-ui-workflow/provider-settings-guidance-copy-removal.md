# Provider-backed settings guidance-copy removal pattern

Use this reference when a provider-backed settings page or entity registry already has Entity Card affordances and the user asks to remove broad helper/guidance copy.

## Durable lesson

For settings pages such as Email Senders, a top-level guidance block can become redundant once provider-specific Optional Create cards communicate the available action. If the user asks to remove the helper, treat it as a UI contract change, not just visual cleanup.

## Apply this sequence

1. Remove the rendered guidance component/block and delete the unused component/function instead of hiding it behind CSS or leaving dead JSX.
2. Remove redundant section headings if the card list and page header already establish the context.
3. Update source-level tests to assert absence of the removed copy/headings, not only presence of the remaining cards.
4. Update the route-specific UI design doc so future contributors do not reintroduce a top guidance block.
5. Update the relevant OpenSpec design/scenarios when the page contract includes SHOULD/SHALL guidance around setup cards or helper text.
6. Update the PR body `UI 변경` section so screenshot reviewers understand the intended visual delta.
7. Run focused tests/lint for the changed page/widget and report in-progress CI checks briefly instead of waiting silently for long preview jobs.

## Review checklist additions

- Confirm the remaining Optional Create card still has an explicit CTA affordance and provider-specific state copy.
- Confirm removed copy is not still present in locale strings, tests, design docs, OpenSpec, or PR body.
- Confirm the absence assertion is narrow enough that future copy can be added deliberately without matching stale removed guidance.
