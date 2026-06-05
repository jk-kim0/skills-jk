# outbound-dev baseline drift reset+seed recovery

Use this reference when Vercel/outbound-dev is deployed and `/login` is healthy, but DB migration or schema check fails after `prisma migrate deploy` reports no pending migrations.

## Symptom pattern

- `Deploy outbound-dev Production` is successful for the latest `origin/main` SHA.
- `vercel inspect https://outbound-dev.vercel.app --scope querypie` shows `Ready` and the alias is attached to the latest deployment.
- `https://outbound-dev.vercel.app/login` returns HTTP 200 and recent Vercel error logs are empty.
- `Apply outbound-dev DB Migration` with `reset_database=false` runs `prisma migrate deploy` successfully and logs `No pending migrations to apply.`
- The following schema check step fails with `DB schema drift detected.`

This usually means the shared dev database has already recorded the single baseline migration, but the baseline migration/schema has changed on `main`. Because the project uses a baseline-only policy, `migrate deploy` will not replay the revised baseline against that existing DB.

## Examples of drift seen

- `UserIdentityProviderType` enum and `UserIdentity` table missing, plus `User.username` / `User.passwordHash` still `NOT NULL`.
- `DryRunOutcome` enum missing.
- `EmailProviderType` missing the `dry_run` enum value.
- `DryRunSenderSettings` table, unique index, and FK missing.

## Recovery sequence

1. Re-fetch and record latest `origin/main`.
2. Verify Vercel deployment separately from DB state:
   - `Deploy outbound-dev Production` run for the latest SHA is `success`.
   - `vercel inspect https://outbound-dev.vercel.app --scope querypie --no-color` shows `Ready`, the expected alias, and production target.
   - `/login` returns HTTP 200.
   - Recent Vercel error logs are empty or unrelated.
3. Run `Apply outbound-dev DB Migration` with `reset_database=false` first.
4. If it fails only at schema check after `No pending migrations to apply`, classify it as baseline drift rather than a Vercel deploy/runtime problem.
5. Run `Apply outbound-dev DB Migration` again with `reset_database=true`.
6. Verify the reset run logs actually include:
   - `npm run db:reset`
   - `prisma migrate reset --force`
   - `Applying migration 20260530000100_baseline_main_schema`
   - `Database reset successful`
   - `npm run db:seed`
   - `prisma db seed`
   - `The seed command has been executed.`
   - `DB schema matches Prisma schema.`
7. Run `Check outbound-dev DB Schema` with `vercel_environment=production` and `check_mode=true`.
8. Run `E2E - Runtime Smoke` with `base_url=https://outbound-dev.vercel.app`.
9. Finish with final `vercel inspect`, `/login` HTTP check, and recent error-log check.

## Operational notes

- If `origin/main` advances while diagnosing, restart the verification sequence from the new latest SHA. Do not report the earlier reset as current if a newer deployment/schema has landed.
- Do not jump directly to reset unless schema drift evidence is present or the user explicitly requests reset+seed.
- Avoid duplicate runtime-smoke dispatches. If a matching outbound-dev smoke for the same SHA is already in progress, wait for it instead of dispatching another; cancel accidental duplicate runs once a successful smoke exists.
- Public `/login` 200 proves the app is reachable, not that the DB schema matches the latest baseline.
