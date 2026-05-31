# Outbound Agent recipient range decision cleanup example

Use this as a compact example when a Product Owner decision removes a previously planned product restriction.

## Trigger

The Product Owner decided that, for the MVP Release Ready bar, recipient email address range should not be restricted by the product:

- Actual Gmail sends should not use an internal/domain allowlist.
- Approved SendRuns should allow the Contact List's eligible recipients.
- Test recipient range should be managed by the tester when constructing Contact Lists or entering test recipients, not by product logic.
- Product safety should focus on general rate limits and user-mistake guards.

## Correct follow-through pattern

1. Update the canonical decision record in `openspec/changes/<change-id>/design.md`:
   - `Status: Accepted`
   - one direct accepted decision paragraph
   - alternatives marked `Accepted` / `Rejected`
   - Release Ready implementation impact

2. Update contract and use-case specs:
   - add `SHALL NOT` requirements for internal/domain/test-recipient allowlist gating
   - add scenarios proving external eligible recipients are not blocked solely by domain
   - add scenarios for rate limit/cooldown guards instead

3. Sweep stale implementation surfaces if the user asked for Release Ready implementation:
   - remove provider-call allowlist guard helpers and blocked reasons
   - remove stale schema fields/enums and seed values
   - remove UI rows or warning copy that still expose the old allowlist concept
   - update regression tests so they assert the rejected guard is absent

4. Sweep stale docs and plans:
   - feature docs
   - implementation plans
   - UI docs
   - task checklists
   - Open Questions that mention the old allowlist policy

5. Verify with lightweight checks and PR metadata:
   - `git diff --check`
   - targeted tests when dependencies are available
   - if local dependencies are unavailable and repo preference is to avoid local installs, report the blocked local test and rely on CI

## Pitfall

Do not reinterpret “testers can configure recipients themselves” as “keep a test-send allowlist.”
If the PO says the product should not consider test recipient range, remove the product-level allowlist concept rather than relocating it to test send only.
