# Contact-list CSV fixture sanitization example

Session pattern captured from an outbound-agent contact-list fixture update.

## Situation

A local CSV export was converted into a committed contact-list fixture. The user first asked to keep rows where the `requested_by` email belonged to `chequer.io` or `querypie.com`. A first pass correctly filtered the 4th column, but a follow-up scan found an external email-like value in non-primary columns:

- `name`: `seongil.park@tossbank.com`
- `certificate_organization`: `seongil.park@tossbank.com`

The row's `requested_by` value was internal, so a primary-column-only filter was insufficient for sanitization.

## Durable lesson

For real-export-derived fixtures, use a two-stage rule:

1. Use the user's named/ordinal primary column for row eligibility.
2. Then scan every cell for email-like strings and remove/redact remaining values outside the allowed domains.

This prevents internal-service columns or valid primary-contact columns from masking sensitive values in names, organizations, notes, or raw metadata fields.

## Verification shape

Report evidence like:

```text
primary column: requested_by (4th column)
remaining data rows: 32
residual non-allowed email-like values: 0
line endings preserved: true
git diff --check: pass
```

If a PR branch is updated, also report the PR number, branch, head SHA, and current CI state without waiting unless the user asked to watch CI to completion.
