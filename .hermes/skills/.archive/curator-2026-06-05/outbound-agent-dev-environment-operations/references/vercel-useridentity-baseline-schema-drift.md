# outbound-dev Vercel UserIdentity baseline schema drift

Use this reference when Vercel/outbound-dev is deployed successfully and `/login` returns 200, but DB migration/schema verification fails after a baseline-only schema change.

## Symptom

`Apply outbound-dev DB Migration` with `reset_database=false` can show:

- `prisma migrate deploy` succeeds.
- `No pending migrations to apply.`
- The subsequent schema check fails with drift.

Observed drift from an existing shared outbound-dev DB after the baseline migration had already been recorded:

- Missing enum `UserIdentityProviderType`.
- Missing table `UserIdentity`.
- `User.username` and `User.passwordHash` still `NOT NULL`.
- Missing `UserIdentity` indexes and FK.

This is not a Vercel deploy/alias problem when Vercel inspect is Ready, `/login` is 200, and recent Vercel error logs are empty. It is an existing shared dev DB diverging from the current single-baseline schema.

## Correct recovery path

1. Confirm the exact latest `origin/main` SHA and Vercel production deployment/alias.
2. Run `Apply outbound-dev DB Migration` first with `reset_database=false` unless the user explicitly requested reset.
3. If migration deploy succeeds but schema check reports baseline drift like the above, escalate to `reset_database=true` for outbound-dev.
4. Verify the reset workflow logs, not only the run conclusion:
   - `npm run db:reset`
   - `prisma migrate reset --force`
   - `Applying migration 20260530000100_baseline_main_schema`
   - `Database reset successful`
   - `npm run db:seed`
   - `prisma db seed`
   - `The seed command has been executed.`
   - `DB schema matches Prisma schema.`
5. Run `Check outbound-dev DB Schema` after reset. If duplicate schema-check runs are queued by accident, one successful run is enough; cancel or ignore redundant runs based on user impact.
6. Run `E2E - Runtime Smoke` with `base_url=https://outbound-dev.vercel.app`.
7. Re-check Vercel inspect, `/login`, and recent error logs before final reporting.

## Notes

- Reset is destructive to shared dev data; use it only when explicitly requested or when migration/schema evidence proves a baseline-only drift that cannot be repaired by normal `migrate deploy`.
- In active main-branch churn, re-fetch before final reporting and make sure all evidence is for the final latest SHA.
- If a runtime smoke for the same SHA and base URL is already in progress, do not dispatch a duplicate. If a duplicate was accidentally dispatched and the first run succeeds, cancel the redundant run.