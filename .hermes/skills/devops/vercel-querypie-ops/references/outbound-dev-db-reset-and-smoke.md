# outbound-agent outbound-dev DB reset and smoke recovery

Use this reference when redeploying or validating the `querypie/outbound-agent` dev environments, especially after an incompatible schema change.

## Dev endpoints

- Vercel: `https://outbound-dev.vercel.app`
- Tencent Tokyo: `https://outbound-tokyo.dev.querypie.io`
- Tencent Seoul: `https://outbound-seoul.dev.querypie.io`

## Deployment / verification flow

1. Start from latest `origin/main`; record the exact main SHA.
2. Confirm the main branch CI and Vercel Production deploy workflow are successful for that SHA.
3. Confirm the main container deploy workflow has published the image and deployed both Tencent targets for that SHA.
4. Run/reset the outbound-dev DB only through the repository workflow when possible, with `reset_database=true` for incompatible schema changes.
5. Inspect the Vercel production alias with `vercel inspect https://outbound-dev.vercel.app --scope querypie` and confirm `/login` returns HTTP 200 and serves the expected deployment id.
6. Dispatch `e2e-runtime-smoke.yml` separately for all three endpoint URLs above and wait for all runs to complete against the same latest main SHA.

## Seed-specific pitfall

For Prisma 7, do not assume `prisma migrate reset --force` will populate reviewer/demo fixture data just because the workflow summary says “reset + seed”. Verify that the workflow contains an explicit `npm run db:seed` step after reset, or verify the DB row counts afterward.

A Vercel smoke failure where login stays on `/login` instead of navigating to `/sales-demo/home` can indicate an empty seed state rather than a runtime 5xx. Check seed counts for at least `User`, `Team`, `TeamMembership`, and `Campaign` before debugging application auth.

Expected reviewer seed baseline after reset:

- `User`: 3
- `Team`: 3
- `TeamMembership`: 3
- `Campaign`: 1

## Safe manual seed recovery pattern

Use only when the workflow reset succeeded but seed data is absent.

- Use Node 24 for Prisma 7 commands.
- Run `npm run prisma:generate` before manual seed if the generated Prisma Client may be stale after UUID/default changes.
- Pull Vercel env values to a temporary file, but never print secrets.
- Do not `source` a temp env file containing PostgreSQL URLs; query strings containing `&` can be mangled by the shell.
- Parse the temp env file with Node or another parser, choose `POSTGRES_PRISMA_URL` / `POSTGRES_URL_NON_POOLING` / `POSTGRES_URL`, and pass the URL via `env DATABASE_URL="$DB_URL" APP_ENV=dev-vercel npm run db:seed`.
- For local `pg` probes against Supabase pooler URLs, changing the temporary local probe URL to `sslmode=no-verify` can avoid local CA-chain failures without changing Vercel/runtime configuration.
- Remove all temporary env files after the recovery.

## Reset/schema drift pitfalls

- After a reset, schema drift can still remain if the baseline migration SQL itself diverges from `schema.prisma`. One observed case was `Team.country` / `Team.language` defaults present in `migration.sql` but absent from Prisma schema; the operational repair is `ALTER TABLE "Team" ALTER COLUMN "country" DROP DEFAULT, ALTER COLUMN "language" DROP DEFAULT;`, and the durable repo fix is to update both the baseline migration and shared repair SQL.
- The Tencent migration workflows accept a `branch` input, so a small repair branch can be used to run VM-local reset/schema-check safely before the fix is merged to `main`. The Vercel migration workflow currently checks out `main`, so Vercel-only SQL repair may need to be applied manually or through a merged workflow/repair change.

## Tencent deploy recovery pitfalls

- If the main Tencent container-image workflow fails while resolving `node:*-bookworm-slim` from Docker Hub with `429 Too Many Requests`, treat it as a transient registry/rate-limit blocker, not an application build failure. Rerun once, but if the same Docker Hub 429 repeats, use the source/archive deploy workflows (`deploy-tencent-outbound-tokyo.yml`, `deploy-tencent-outbound-seoul.yml`) with `branch=main` to put the latest source revision on the VMs while the image path is blocked.
- For Tencent source/archive deploy workflows, inspect the log for `revision=<sha>` and service state. A workflow can fail on its immediate public HTTPS smoke with a temporary `502 Bad Gateway` even after the repo was swapped and `outbound-front` started. Re-check `/login` directly and run the runtime smoke workflow before deciding that DB reset or rollback is needed.
- When the user asks for “latest version deployed” across all three dev servers, do not rely only on GitHub run conclusions. Record evidence from Vercel `vercel inspect`, Tencent deploy log `revision=<sha>`, direct `/login` HTTP 200 checks, DB schema-check runs, and final `e2e-runtime-smoke.yml` runs.

## PR follow-up if a workflow gap is found

If the reset workflow did not explicitly seed after reset, create a normal PR rather than leaving the fix as an operational note. The workflow contract test should assert the presence of the `npm run db:seed` step so future reset-mode changes keep demo login smokeable.