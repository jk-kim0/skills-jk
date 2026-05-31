# Prisma 7 `migrate diff` schema-check compatibility

Use this when a GitHub Actions or local helper performs a read-only live DB vs Prisma schema drift check with `prisma migrate diff`, especially in Vercel/Prisma repositories.

## Symptom

A schema check workflow fails before detecting any real DB drift with an error like:

```text
--from-url was removed. Please use --[from/to]-config-datasource...
```

This is a Prisma CLI compatibility failure, not evidence that the live DB drifted.

## Prisma 7 replacement

Prisma 7 removed older direct URL/datamodel flags such as:

```bash
npx prisma migrate diff \
  --from-url "$DATABASE_URL" \
  --to-schema-datamodel prisma/schema.prisma \
  --script \
  --exit-code
```

Use the configured datasource plus schema file flags instead:

```bash
npx prisma migrate diff \
  --from-config-datasource \
  --to-schema prisma/schema.prisma \
  --script \
  --exit-code
```

`migrate diff` remains read-only. `--script` only prints SQL; it does not apply it.

## Wrapper-script env handling

If the helper script supports selecting a URL env var such as `--from-env DATABASE_URL` or `--from-env SOME_OTHER_URL`, ensure the Prisma child process sees the selected URL through the config datasource.

Safer pattern when `prisma.config.ts` chooses `DATABASE_DIRECT_URL ?? DATABASE_URL`:

```ts
const selectedDatabaseUrl = process.env[args.fromEnv];
const prismaEnv = {
  ...process.env,
  DATABASE_URL: selectedDatabaseUrl,
  DATABASE_DIRECT_URL: selectedDatabaseUrl,
};
```

Why set both?

- `--from-config-datasource` reads the datasource URL from `prisma.config.ts`, not from a `--from-url` CLI argument.
- If `prisma.config.ts` prioritizes `DATABASE_DIRECT_URL`, a pre-existing direct URL can override the selected `DATABASE_URL`.
- Setting only `DATABASE_DIRECT_URL: undefined` removes that variable from the spawned process, but if the Prisma config imports `dotenv/config`, local `.env` loading may reintroduce `DATABASE_DIRECT_URL`. Setting both env vars to the selected URL is more deterministic for local and CI runs.

## Tests and docs to update together

When making this compatibility fix, update all three layers when present:

1. Helper implementation: replace CLI args and inject env for `--from-config-datasource`.
2. Unit tests: assert the new args `--from-config-datasource` and `--to-schema`.
3. Workflow/design docs: state that the workflow is read-only and that failures from removed flags are CLI compatibility failures, not DB drift findings.

## Verification

Preferred lightweight verification:

```bash
npm exec prisma migrate diff -- --help
npm test -- tests/db-schema-diff.test.ts
git diff --check
```

If the repository requires a newer Node for Prisma 7, use the repo's declared Node version before installing/running Prisma commands. Do not encode one user's local nvm path in the repo or PR body; mention the project Node requirement instead.
