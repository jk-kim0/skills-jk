# Prisma DB Schema Drift Check for Vercel/Neon Next.js Apps

Use this reference when a Next.js app uses Prisma with a hosted PostgreSQL/Neon database and needs a read-only check that the live DB schema still matches `prisma/schema.prisma`.

## Durable pattern

- Do not run mutating Prisma commands in CI/workflows whose purpose is drift detection. Avoid `prisma db push`, `prisma migrate reset`, `prisma migrate deploy`, or any destructive/apply step unless the user explicitly asks for migration application.
- Prefer Prisma's read-only diff command. For Prisma 7+ projects with `prisma.config.ts`, inject the selected live URL into the datasource env vars the config reads, then run:

```sh
prisma migrate diff \
  --from-config-datasource \
  --to-schema prisma/schema.prisma \
  --script \
  --exit-code
```

Older Prisma projects may still use `--from-url "$DATABASE_URL" --to-schema-datamodel prisma/schema.prisma`; verify the installed CLI before copying examples.

- Interpret exit codes deliberately:
  - `0`: no schema drift detected.
  - `2`: drift/diff detected when `--exit-code` is used.
  - other non-zero: command/configuration failure.
- If `prisma/migrations/` exists, run `prisma migrate status --schema prisma/schema.prisma` first. If migration status fails, stop and report that the diff was not executed; do not conflate migration-history failure with schema diff output. If migration status succeeds but `migrate diff` exits `2`, look for schema changes that landed without a matching migration artifact.
- Never print the DB URL/connection string. Error messages should mention only the env var name, e.g. `DATABASE_URL is required to compare the live DB schema.`

## CLI shape that worked well

Expose an app-local script such as `scripts/db-schema-diff.ts` with package scripts:

```json
{
  "scripts": {
    "db:schema:diff": "tsx scripts/db-schema-diff.ts",
    "db:schema:check": "tsx scripts/db-schema-diff.ts --check"
  }
}
```

Useful CLI options:

- `--check`: return exit code `2` on drift so CI can fail.
- `--output <path>`: write diff SQL to a reviewable artifact.
- `--from-env <name>`: read a database URL from an alternate env var.
- `--schema <path>`: override datamodel path.
- `--help`: make the script self-documenting.

Unit-test the command runner rather than a real database connection:

1. Missing DB URL fails before invoking Prisma.
2. Drift path preserves `migrate diff` output and returns/checks exit code `2`.
3. Existing `prisma/migrations` runs `migrate status` first and stops on status failure.

## GitHub Actions / Vercel env pattern

For Vercel-hosted apps, avoid duplicating Neon connection strings into GitHub Secrets if Vercel already owns the env configuration. A manual workflow can pull Vercel env first, then run the local script:

```yaml
on:
  workflow_dispatch:
    inputs:
      vercel_environment:
        type: choice
        options: [preview, production]
        default: preview
      check_mode:
        type: boolean
        default: true

permissions:
  contents: read

steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-node@v4
    with:
      node-version: 24
      cache: npm
      cache-dependency-path: front/package-lock.json
  - run: npm ci
    working-directory: front
  - run: npx vercel pull --yes --environment="$VERCEL_ENVIRONMENT" --token="$VERCEL_TOKEN"
    working-directory: front
  - run: test -n "${DATABASE_URL:-}"
    working-directory: front
  - run: npm run db:schema:check -- --output schema-diff.sql
    working-directory: front
```

Always upload the diff/log artifact so reviewers can inspect drift details even when the job fails.

## Verification notes

- Use `actionlint` for workflow syntax.
- Verify CLI help and missing-env failure path locally.
- If the repo uses Prisma 7, ensure the verification Node version satisfies Prisma's engine requirement (for example Node 24.x). Treat a too-old local Node as setup state, not as a permanent skill constraint.
