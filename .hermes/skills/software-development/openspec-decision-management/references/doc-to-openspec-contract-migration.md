# Doc-to-OpenSpec Contract Migration Pattern

Use this reference when a repository has a long-lived design document that is acting as a canonical implementation contract, but the repo now uses OpenSpec as the durable spec source.

## Trigger

- A `docs/**` design file contains normative implementation rules: adapter boundaries, service ownership, validation, DTO/error shape, state transitions, provider/async exclusions, endpoint naming, or similar `SHALL`-style constraints.
- The same rules are already partly represented in `openspec/specs/**/spec.md` or should be enforced through scenarios.
- The design doc is becoming stale because implementation has moved beyond the original sprint/phase.

## Recommended migration shape

1. Create a class-level contract spec under `openspec/specs/contract-<topic>/spec.md` when the rules are cross-cutting.
   - Example: `openspec/specs/contract-front-api-boundary/spec.md` for Front App API / service boundary rules.
2. Move normative content into OpenSpec Requirements and Scenarios.
   - Use `SHALL`, `SHALL NOT`, `MAY`, `MUST`.
   - Convert prose rules into verifiable `GIVEN` / `WHEN` / `THEN` scenarios.
   - Keep endpoint inventories out of long-lived specs unless they are core naming contracts; code route trees should remain the detailed source of truth.
3. Convert the original `docs/**` file into a short bridge document instead of deleting it abruptly.
   - Mark status as `Superseded by OpenSpec`.
   - Link to the new canonical spec and adjacent specs.
   - Preserve only short historical/background context.
   - Explicitly say new rules belong in OpenSpec, not in the bridge doc.
4. Update active references that described the old docs file as canonical.
   - Planning/done/archive docs may either link to the new OpenSpec or keep historical context, but avoid saying the bridge doc is the implementation contract.
5. Update OpenSpec inventory/readme files so agents can discover the new spec.
6. Verify with lightweight docs checks.
   - `git diff --check`
   - Resolve relative Markdown links in changed files.
   - For docs-only PRs, app CI may be skipped if scope detection supports it.

## Pitfalls

- Do not leave two canonical sources: a bridge doc must not keep new normative content.
- Do not treat an old sprint endpoint list as the current endpoint inventory if the app has evolved; migrate durable naming/operation principles, not stale full route lists.
- Do not bury cross-cutting implementation contracts inside a feature-specific change spec if future features also need them.
- Do not add code changes when the task is only to migrate documentation/spec authority.

## Example outcome

- New canonical spec: `openspec/specs/contract-front-api-boundary/spec.md`
- Bridge doc: `docs/api-implementation-design.md`
- Updated references: technology stack, schema contract docs, feature plans, and OpenSpec inventory files point to the new spec.
