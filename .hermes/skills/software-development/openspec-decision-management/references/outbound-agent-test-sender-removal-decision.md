# Outbound Agent test sender removal decision pattern

Use this reference when a Product Owner removes a previously planned local/fake provider, fixture sender, or demo-only identity from requirements/design/OpenSpec.

## Session pattern

The PO stated that the sender for Test email sends does not exist and must be removed/marked unused:

- display name: `Test email sender`
- email: `test-sender-kr@example.local`
- prior meaning: local test sender, active, ready for local test sends, no Gmail auth needed

The correct documentation response was not only to delete references. The durable contract needed to say explicitly:

- Test-send sender identity does not exist.
- The fake/local provider adapter and settings are no longer requirements.
- The named local sender row must not be seeded.
- Sender Settings must not show `Ready for local test sends` or `No Gmail auth needed` as an active requirement.
- Actual send still requires a connected/locked Gmail sender and must not fallback to a test sender.
- Remaining implementation/fixture references are legacy removal targets if code cleanup is out of the current PR scope.

## Files/layers to sweep

For OpenSpec-backed repos, update all applicable layers in one docs/spec PR:

1. Canonical decision log: `openspec/changes/<change-id>/design.md`
   - Rename the decision if necessary, for example from "test sender vs actual sender separation" to "test sender identity removal".
   - Add accepted decision, rationale, rejected alternatives, implementation impact, and follow-up cleanup.

2. Contract specs: `openspec/changes/<change-id>/specs/**/spec.md`
   - Add `SHALL NOT` negative requirements.
   - Add a scenario such as "test sender identity is not available".

3. User/feature docs: `docs/feature/**`
   - Mark the removed feature document as `Removed` or a legacy record.
   - Replace active design sections with removed-scope and current-principle sections.

4. Status docs: `docs/feature-status.md`, `docs/feature/status-*.md`
   - Downgrade active rows to `Mock`, `Removed`, or `legacy artifact` language.
   - Avoid leaving `Released`/`In-Progress` labels for a concept the PO says does not exist.

5. Model docs and setup docs
   - Remove wording that says the removed concept is still attached to core models.
   - If setup docs mention old fallback behavior, keep only the guard/negative statement.

## PR and verification shape

- Work in repo-local `.worktrees/` when required by the repo guide.
- Use latest `origin/main` as the base and rebase before push.
- Keep it docs/OpenSpec-only unless the user explicitly asks for implementation cleanup.
- PR body should say local build/test was not run when repository preference is commit/push first for docs-only work.
- `git diff --check` is the minimum local verification.
- CI scope detection plus skipped app CI is acceptable for docs/OpenSpec-only PRs when it passes.
