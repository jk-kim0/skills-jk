# Shared DB Neon direct URL and migration artifact recovery

Use this when a GitHub Actions Prisma migration/backfill workflow for a shared Vercel Neon DB fails because the direct DB URL is missing, or when schema drift remains after applying existing migrations.

## Failure signature

In the failed Actions log, the validation step shows the migration env as empty and stops before migrate/backfill work begins:

```text
DATABASE_DIRECT_URL:
DATABASE_DIRECT_URL secret is required for migration/backfill.
```

This means the workflow did not receive a GitHub Actions secret for the Neon direct/non-pooling connection string. It is not a Prisma migration failure yet.

## Correct secret source

- Vercel runtime should keep using the pooled URL as `DATABASE_URL`.
- Prisma Migrate/backfill workflows should use the Neon direct/non-pooling URL as GitHub Actions secret `DATABASE_DIRECT_URL`.
- Prefer the Vercel Neon Storage resource direct/non-pooling secret, commonly named `POSTGRES_URL_NON_POOLING` or `DATABASE_URL_UNPOOLED`, when available.
- Do not sync `DATABASE_DIRECT_URL` into the Vercel Project runtime env unless the app actually needs it at runtime.
- Do not print the DB URL in logs, PR bodies, artifacts, or summaries.

## Safe recovery sequence

1. Inspect the failed job log first; confirm whether the workflow failed before migration execution because `DATABASE_DIRECT_URL` was empty.
2. Check repository secret names with `gh secret list` and Vercel project/runtime env names without printing values.
3. Obtain the Neon direct/non-pooling URL from the Vercel Neon Storage integration or other approved secret source.
4. Validate connectivity without echoing the URL, for example by writing it to a mode-600 temp file and running a minimal `psql "$(cat /tmp/secret)" -c 'select current_database();'` check.
5. Set the GitHub secret: `gh secret set DATABASE_DIRECT_URL --repo <owner>/<repo> --body-file /tmp/secret`.
6. Delete the temp secret file immediately.
7. Re-run the migration workflow with only the necessary one-time steps enabled. Do not repeat a baseline resolve if it already succeeded.
8. Run the read-only schema drift workflow after migration/backfill.
9. If drift remains, inspect whether `schema.prisma` is ahead of committed migration artifacts. Do not treat every drift as a live DB problem.
10. If a migration artifact is missing but the live shared DB was manually corrected, create a PR that adds the missing `front/prisma/migrations/<timestamp>_<name>/migration.sql` artifact and document that the current shared DB should use `prisma migrate resolve --applied <migration>` rather than re-running the SQL.
11. Deploy or redeploy the affected Vercel environment and smoke the exact production alias, confirming the alias points to the expected deployment id/commit and pages do not contain Prisma error markers such as `P2021` or `P2022`.
12. Once the one-time recovery/adoption path has succeeded, open a follow-up workflow cleanup PR that removes recovery-only dispatch inputs and steps (for example baseline resolve toggles, migration-name inputs, backfill file selectors, or arbitrary branch refs). Leave the ongoing migration workflow as `main` + direct DB secret + `prisma migrate deploy` + schema drift check.

## Pitfalls

- A green Vercel deployment only proves the build deployed; it does not prove the shared DB schema matches runtime code.
- If `schema.prisma` changed without a migration artifact, manually fixing the shared DB resolves the immediate runtime problem but leaves future environments and migration history broken.
- Avoid using pooled runtime `DATABASE_URL` for Prisma Migrate; use direct/non-pooling Neon connection strings for migration/backfill.
- Keep one-time baseline resolve separate from ordinary `prisma migrate deploy` runs. Repeating baseline resolve can obscure migration history rather than fixing schema drift.
- Do not preserve recovery-only workflow options after they are no longer needed. A manual DB migration workflow that still exposes completed one-time toggles/backfill file inputs is itself a future operational hazard; simplify it promptly so future migrations require correctly committed Prisma migration artifacts rather than operator memory.
