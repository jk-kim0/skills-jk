# Shared Vercel DB migration from Neon to Supabase Marketplace

Use this reference when a Vercel-hosted development app moves from a Vercel Neon Marketplace resource to Supabase Marketplace, especially when Production and Preview share one development PostgreSQL DB and migrations run through a protected manual GitHub Actions environment.

## Durable pattern

1. Create the Supabase Marketplace resource with an explicit region and connect it to the Vercel project.

```bash
vercel integration add supabase \
  --name <resource-name> \
  --plan free \
  --metadata region=icn1 \
  --metadata publicEnvVarPrefix=NEXT_PUBLIC_ \
  --format=json \
  --scope <team>
```

If the resource is created but not connected to the project, connect it through the storage connection API. The body shape that worked:

```json
{
  "envVarEnvironments": ["production", "preview"],
  "projectId": "<vercel-project-id>",
  "type": "integration"
}
```

Invoke with the Vercel CLI API helper using `--input` rather than shell redirection so content-type is set correctly:

```bash
vercel api /v1/storage/stores/<store-id>/connections \
  --method POST \
  --input /tmp/supabase-connect.json \
  --scope <team>
```

2. Promote Supabase pooled URL to the app's `DATABASE_URL`.

The Supabase integration syncs `POSTGRES_PRISMA_URL` and `POSTGRES_URL_NON_POOLING`. Use:

- Runtime `DATABASE_URL` = Supabase `POSTGRES_PRISMA_URL` / pooled URL
- Migration secret `DATABASE_DIRECT_URL` = Supabase `POSTGRES_URL_NON_POOLING` / direct non-pooling URL

For Vercel env creation/upsert via API, use `type: "encrypted"` for `DATABASE_URL` if later `vercel env pull` validation should show the value. `type: "sensitive"` may make pull output unsuitable for host verification.

Example env upsert body:

```json
{
  "type": "encrypted",
  "key": "DATABASE_URL",
  "value": "<supabase-pooled-url>",
  "target": ["production", "preview"]
}
```

```bash
vercel api '/v10/projects/<project-id>/env?upsert=true' \
  --method POST \
  --input /tmp/vercel-database-url-body.json \
  --scope <team>
```

3. Set the GitHub environment secret from stdin when the installed `gh` lacks `--body-file`.

```bash
env -u GITHUB_TOKEN gh secret set DATABASE_DIRECT_URL \
  --env <github-environment-name> \
  < /tmp/supabase-direct-url.txt
```

4. Apply migrations with the direct URL, not the pooled runtime URL.

```bash
cd front
export DATABASE_DIRECT_URL='<supabase-direct-non-pooling-url>'
export DATABASE_URL="$DATABASE_DIRECT_URL"
npm run prisma:generate
npm run prisma:migrate:deploy
```

If a fresh Supabase DB fails on a migration because an earlier baseline already created a column/table that a later migration tries to add, inspect the live schema first. Only then mark the specific migration applied:

```bash
npx prisma migrate resolve --applied <migration-name>
npm run prisma:migrate:deploy
```

Do not leave `migrate resolve --applied` in recurring workflows; it is a one-time recovery/adoption step.

5. Seed only through an explicit setup step and make seed safety match the new provider host.

For a `dev-vercel`-style shared development DB, seed should require an explicit app/setup environment value and verify that the DB host is a Supabase host after the provider switch. Do not keep a Neon-only seed safety allowlist after switching runtime DBs.

6. Verify without printing secrets.

Useful checks:

- `vercel env pull` for Production and Preview, then parse only host suffixes and provider domains.
- `vercel api /v10/projects/<project-id>/env` to verify `DATABASE_URL` targets and update timestamps.
- `npm run db:schema:check -- --from-env DATABASE_DIRECT_URL --output <tmp-file>`.
- A minimal Prisma/adapter query for seed row counts.
- `vercel integration list --all --scope <team>` to confirm the old Neon resource no longer appears for the project.

7. Remove the old Neon Marketplace resource after Supabase runtime, migration secret, migrations, schema drift, and seed checks pass.

```bash
vercel integration-resource remove <old-resource-name> \
  --disconnect-all \
  --yes \
  --format=json \
  --scope <team>
```

Then verify deletion by querying the old store ID and expecting `Store not found (404)`.

## PR/workflow hygiene

- Rebase the PR branch onto latest `origin/main` before force-pushing the env/workflow docs update.
- Preserve newly landed backfill steps from `main` when resolving workflow conflicts; remove only one-time baseline/provider-specific recovery steps.
- Update the PR title/body after provider migration. Stale PR bodies that still describe Neon limitations are misleading once Supabase is the source of truth.
- After force-push, verify PR `headRefOid`, remote branch SHA, and fresh checks/runs attach to the new SHA.
