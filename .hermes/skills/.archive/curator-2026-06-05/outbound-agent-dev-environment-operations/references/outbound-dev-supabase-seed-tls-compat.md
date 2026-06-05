# outbound-dev Supabase seed TLS compatibility

Use this reference when `Apply outbound-dev DB Migration` is run with `reset_database=true` and the Supabase reset applies migrations successfully, but the seed step fails immediately with Prisma `P1011` / `TlsConnectionError` / `self-signed certificate in certificate chain`.

## Symptom

The reset step can succeed via Prisma migrate, then `npm run db:seed` fails in `front/prisma/seed.ts` on the first Prisma transaction, often at `prisma.activity.deleteMany()`.

The relevant warning before failure is that pg treats SSL modes `prefer`, `require`, and `verify-ca` as aliases for `verify-full` unless libpq-compatible behavior is requested.

## Durable cause

Supabase pooler URLs commonly use `sslmode=require`.
With `@prisma/adapter-pg` / `pg`, that can be interpreted as stricter certificate verification than libpq-style `require`, causing self-signed-chain rejection during seed even though migrate/reset can complete.

## Fix pattern

Mirror the repo's `front/scripts/run-sql-file.ts` URL normalization in any seed/database script that constructs a `PrismaPg` adapter directly:

```ts
const libpqCompatSslModes = new Set(["prefer", "require", "verify-ca"]);

function buildSeedDatabaseUrl(rawDatabaseUrl: string) {
  try {
    const url = new URL(rawDatabaseUrl);
    const sslMode = url.searchParams.get("sslmode")?.toLowerCase();

    if (sslMode && libpqCompatSslModes.has(sslMode) && !url.searchParams.has("uselibpqcompat")) {
      url.searchParams.set("uselibpqcompat", "true");
      return url.toString();
    }
  } catch {
    return rawDatabaseUrl;
  }

  return rawDatabaseUrl;
}
```

Then pass `connectionString: buildSeedDatabaseUrl(databaseUrl)` to `new PrismaPg(...)`.

## Operational workaround before merge

If this fix is on a PR/ops branch and needs to be used to recover outbound-dev immediately:

1. Ensure `.github/workflows/apply-outbound-dev-db-migration.yml` checks out the workflow ref/branch, not hardcoded `main`:
   - `ref: ${{ github.ref_name }}`
2. Push the branch.
3. Dispatch:
   - `env -u GITHUB_TOKEN gh workflow run 'Apply outbound-dev DB Migration' --ref <branch> -f reset_database=true`
4. Confirm the run succeeded.
5. Rerun the normal main-branch schema checks for all three environments.
6. Smoke `/login` and a DB-backed authenticated route on all three dev URLs.

Do not describe this as a permanent environment limitation; it is a Prisma/pg URL compatibility issue and should be fixed in code.