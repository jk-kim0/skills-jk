# Prisma migration artifact allowlist CI repair pattern

Use this reference when a PR adds or removes Prisma schema/migration artifacts and GitHub Actions fails in a source-contract test rather than in application behavior.

## Symptom

- PR CI fails in unit tests after a new Prisma migration directory is added.
- Prisma validate/generate/typecheck may pass in CI, but a test that enumerates migration artifacts fails because its expected directory list is hard-coded.
- The failing assertion points at a repository contract test, for example `schema-migration-artifacts.test.ts`, not at the migration SQL itself.

## Triage sequence

1. Inspect PR checks first, then open the failing workflow/job log with `gh run view <run-id> --job <job-id> --log`.
2. Separate real migration/schema errors from repository artifact-contract failures:
   - schema/migration error: Prisma validate, migrate, or generated client errors;
   - artifact-contract error: a test compares actual migration directories/files against an expected allowlist.
3. If the new migration is intentional, update the contract test allowlist with exactly the new migration directory name.
4. Run the narrow failing test locally if possible.
5. Run a lightweight lint/diff check for the edited file.
6. Commit, rebase onto latest `origin/main`, push, then watch the new CI run to completion.

## Outbound Agent example

For querypie/outbound-agent PRs, `front/src/__tests__/schema-migration-artifacts.test.ts` can require an explicit expected migration directory update when `front/prisma/migrations/<timestamp_name>/` changes. A CI-only success path is acceptable when local Prisma generation is blocked by a developer-machine Node/Prisma compatibility issue, provided the failing narrow test and the edited-file lint/diff checks pass locally and CI proves Prisma generate/typecheck/unit/build on the PR branch.

## Reporting guidance

In the final PR status report, distinguish:

- root cause: migration artifact allowlist omitted an intentional new migration;
- fix: added the exact migration directory to the expected list;
- local verification: narrow test and edited-file checks;
- local limitation: if any, describe it as environment-specific and non-blocking only after CI passes;
- final CI state: list pass/skipped checks without implying skipped deploy jobs failed.
