# corp-web-app UI implementation OpenSpec follow-up

Use this when a `corp-web-app` UI implementation PR already exists and the user asks to record the UI behavior in OpenSpec (for example, “OpenSpec 명세에 명시해줘”).

## Pattern

1. Stay on the existing PR branch/worktree unless the user asks for a separate docs PR.
2. Identify whether an existing OpenSpec spec already owns the behavior:
   - `platform-*` for reviewer/debugging/app foundation behavior.
   - `contract-*` for data, loaders, metadata, routing, validation, or state transitions.
   - `uc-*` for user-facing website UI/capability behavior.
3. If no existing spec fits, create a class-level spec rather than mixing unrelated UI requirements into a nearby content/data spec.
   - Example: public publication/news list card behavior belongs in a `uc-publication-list-ui` style spec, not in a content-authoring spec about MDX fields/assets.
4. Express the behavior as durable Requirements plus GIVEN/WHEN/THEN scenarios.
   - For responsive UI, state the compact/mobile contract and separately allow wider-viewport behavior when appropriate.
   - Include explicit negative requirements when the bug was caused by a reversed visual order or similar implementation affordance.
5. Update OpenSpec discovery surfaces in the same commit:
   - `openspec/specs/README.md` inventory row.
   - `openspec/project.md` implementation baseline bullet when the behavior is broad enough for future agents to notice.
6. Keep repository-internal OpenSpec text in English, even when the PR title/body is Korean for the user's repo-work convention.
7. Run lightweight verification: `git diff --check` plus the same focused source/route test that backs the UI implementation when available.
8. Update the PR body to mention the new OpenSpec path and the implementation verification.

## Example requirement wording

For a mobile news list ordering bug:

- Compact/mobile news cards SHALL render date when present, title, and description before thumbnail.
- Thumbnail SHALL NOT visually precede the text block on compact/mobile viewports.
- Wider viewports MAY remain side-by-side if they do not change the compact/mobile reading order contract.

## Pitfalls

- Do not append UI rendering contracts to `content-authoring` simply because the page is backed by MDX/publication data; separate authoring/data contracts from user-facing UI contracts.
- Do not create a one-off spec named after the PR, bug, or route only; use a reusable class-level spec id such as `uc-publication-list-ui`.
- Do not forget `openspec/specs/README.md`; otherwise future agents may not discover the new spec.
