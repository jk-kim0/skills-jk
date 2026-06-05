# Tencent Seoul baseline schema drift reset

Use this reference when Dev Seoul has a current container image and healthy public `/login`, but authenticated/runtime routes or deployed runtime smoke fail because the VM-local PostgreSQL schema is older than the repo's current single-baseline Prisma schema.

## Symptom pattern

- VM deployment metadata matches the expected SHA/image:
  - `/opt/outbound-agent/deployments/current-revision`
  - `/opt/outbound-agent/repo/.deployed-revision`
  - `/opt/outbound-agent/deployments/current-image`
- `outbound-front`, `nginx`, and `outbound-agent-postgres` are active/healthy.
- Public `/login` returns HTTP 200.
- `docker logs outbound-front` shows Prisma runtime errors such as:
  - `P2021`
  - `The table public.UserIdentity does not exist in the current database`
  - `Invalid prisma.userIdentity.findFirst() invocation`
- `_prisma_migrations` contains the baseline migration name, but the current baseline SQL in the repo has since been regenerated with new tables. Prisma will not re-run the already-recorded baseline migration on an existing shared dev DB.

## Diagnosis sequence

1. Separate exact-version proof from DB/runtime health.
   - First verify VM `current_revision`, `.deployed-revision`, `current_image`, service state, and public `/login`.
   - Do not treat `/login` 200 as proof that authenticated routes are healthy.
2. Inspect recent `outbound-front` logs for Prisma `P2021` / missing-table errors.
3. Verify the missing table and migration history directly in VM-local PostgreSQL, for example checking `information_schema.tables` and recent `_prisma_migrations` rows.
4. Check whether the latest code changed the single baseline migration or schema model that the deployed runtime now uses.
5. Check whether `Apply tencent/outbound-seoul DB Migration` and `Check tencent/outbound-seoul DB Schema` have run for the latest main SHA.

## Repair sequence

For baseline drift on a shared dev DB, migrate-only may not repair the DB because the baseline migration is already marked applied. Use the explicit dev reset path after evidence:

1. Dispatch `Apply tencent/outbound-seoul DB Migration` on `main` with `reset_database=true`.
2. Verify the workflow log contains:
   - `prisma migrate reset --force`
   - `Applying migration 20260530000100_baseline_main_schema`
   - `Database reset successful`
   - `prisma db seed`
   - `The seed command has been executed`
3. Verify seed/schema directly in PostgreSQL. For the observed Google SSO/UserIdentity drift, confirm `UserIdentity` exists and has seeded rows.
4. Dispatch `Check tencent/outbound-seoul DB Schema` on `main` and require success.
5. Dispatch or wait for Dev Seoul runtime smoke on the deployed URL and require success.
6. If `origin/main` moves while repairing, follow the newest Tencent deploy after the reset and re-check VM metadata + post-deploy smoke against the newest SHA.

## Reporting shape

Report separately:

- DB repair evidence: migration/reset run ID, reset/seed log markers, schema check run ID.
- Exact deployed version evidence: current revision/image and latest `origin/main` SHA.
- Runtime evidence: public `/login`, recent log absence of the original missing-table error, and runtime smoke run/job result.

Do not describe a successful reset as enough by itself; pair it with schema check and runtime smoke.