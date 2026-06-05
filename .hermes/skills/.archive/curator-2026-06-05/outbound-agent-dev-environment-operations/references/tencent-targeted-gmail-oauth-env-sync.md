# Tencent targeted Gmail OAuth env sync

Use this reference when Gmail OAuth credentials need to be refreshed on one Tencent dev VM without letting the other VM block the operation.

## Problem pattern

The manual container-image deployment workflow can update VM-local Gmail OAuth settings from GitHub repository secrets and then restart/redeploy `outbound-front`. For urgent Gmail OAuth repairs, running both Tencent VMs in a fixed sequence is risky: an unrelated failure on the first VM can skip the intended VM.

## Desired workflow contract

The manual `Deploy Tencent container image` workflow should expose a `target` input:

- `all` — preserve the normal two-VM sequence.
- `dev-seoul` — apply only Seoul.
- `dev-tokyo` — apply only Tokyo.

For a Seoul-only Gmail OAuth repair, use inputs shaped like:

```text
target: dev-seoul
image: ireg.querypie.io/ci/outbound-front:<hash-id>
dry_run: false
confirm_apply: APPLY
update_gmail_oauth_config: true
```

Run a dry-run first when checking secret presence/syntax:

```text
target: dev-seoul
image: ireg.querypie.io/ci/outbound-front:<hash-id>
dry_run: true
update_gmail_oauth_config: true
```

Dry-run verifies required secrets and uploaded env file syntax; it does not mutate `/etc/outbound-agent/front.env`.

## Implementation shape

- Add `workflow_dispatch.inputs.target` as a choice input with default `all`.
- Validate target alongside image and confirmation in the validate job.
- Output the selected target from the validate job.
- Gate the Tokyo reusable workflow job with:
  - run when target is `all` or `dev-tokyo`.
- Gate the Seoul reusable workflow job with `always()` plus explicit conditions:
  - validate succeeded;
  - target is `all` or `dev-seoul`;
  - if target is `all`, Tokyo succeeded;
  - if target is `dev-seoul`, do not require Tokyo success.
- Keep default `all` behavior compatible with previous operator expectations.

## Verification

- `git diff --check`
- `actionlint .github/workflows/deploy-tencent-container-image.yml`
- YAML parse of the workflow file
- PR checks after push

## Operational follow-up

After an apply run, verify the intended VM specifically. For Seoul, run the Seoul Gmail OAuth diagnostic workflow or otherwise confirm:

- `outbound_front=active`
- `nginx=active`
- expected `current_image`
- Gmail env keys are present, redacted
- public `/login` returns HTTP 200

Do not infer Seoul was updated from a top-level workflow dispatch alone; verify the Seoul job actually ran and succeeded.