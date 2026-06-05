---
name: multi-environment-dev-deployment-ops
description: Verify, migrate, schema-check, deploy, and smoke-test multiple development environments against the latest main branch, with reset/redeploy escalation only after evidence of drift or runtime failure.
version: 1.0.0
metadata:
  hermes:
    tags: [deployment, db-migration, schema-check, smoke-test, multi-environment]
---

# Multi-Environment Dev Deployment Operations

Use this skill when a user asks to confirm that multiple development servers/environments are on the latest version, run database migrations, run schema checks, smoke-test runtime behavior, and reset/redeploy only if something is broken.

This is a class-level workflow. Apply environment-specific details from repository docs, existing workflows, and support references.

## Core principles

1. Establish the authoritative target revision first.
   - Fetch the remote default branch.
   - Record the full target SHA.
   - If the branch is actively moving, wait for the same SHA to remain stable for about one minute before calling it “latest”.
   - If the branch moves during the task, restart the verification sequence for the new final SHA.

2. Prefer migrate-only before reset unless reset is the user's explicit requested operation.
   - Run migrations without reset first by default.
   - Run schema drift checks after migrations.
   - Only use database reset by default when migration, schema check, or runtime smoke proves the environment is incompatible or broken.
   - If the user explicitly asks to reset dev/test databases, treat reset as authorized scope and run the reset workflow directly; still run schema checks and runtime smoke afterward.
   - Do not reset merely because reset is available.

3. Verify exact deployment separately from public HTTP health.
   - Public `/login` or `/health` returning 200 proves runtime availability, not exact revision.
   - Use authoritative deployment metadata per platform:
     - VM/container: revision files, image tags, service status.
     - Vercel: deployment workflow logs plus `vercel inspect`, deployment ID, alias, target, and region.
     - Other platforms: deployment ID, image digest/tag, commit SHA, or release metadata.

4. Verify database-backed runtime behavior, not only static page availability.
   - After `/login` or public smoke, hit an authenticated or DB-backed route when safe credentials/fixtures exist.
   - For seeded dev apps, prefer a fixture user/session and a lightweight page that exercises database reads.
   - Keep secrets out of logs and responses.

5. Verify runtime secret injection from the deployment workflow, not from secret existence alone.
   - Treat `gh secret list` as presence-only evidence: it proves names exist, not that the app runtime receives them.
   - Inspect the exact deploy workflow inputs, reusable workflow calls, default values, and skipped/successful steps to confirm whether secrets are written to Vercel env, VM env files, container env files, or runtime config.
   - When a workflow has an opt-in secret-sync flag, run the safest available dry-run with that flag enabled before claiming the injection path works.
   - Distinguish “code/image deploy succeeds with existing runtime env” from “this deploy also updates runtime secrets.” Report them separately.

6. Escalate in order.
   - migration failure -> inspect logs -> reset only if data/schema state is the cause.
   - schema drift -> inspect diff/artifact -> reset only if intentional destructive dev reset is appropriate.
   - deployment revision mismatch -> trigger the canonical deploy workflow before touching DB reset.
   - runtime failure after correct revision + clean schema -> inspect service logs; redeploy/reset only when evidence points there.

## Recommended sequence

1. Fetch and stabilize latest default-branch SHA.
2. Inspect recent CI/deploy/migration runs for that SHA.
3. Dispatch migrations for all target environments with reset disabled.
4. Poll until migrations are complete.
5. Dispatch schema drift checks for all target environments.
6. Poll until schema checks are complete.
7. Confirm deployment workflows for the stabilized SHA.
8. Read authoritative per-environment deployment metadata.
9. Run public runtime smoke for every environment.
10. Run provider/configuration parity smoke where the task involves external providers (for example, compare OAuth start redirect `client_id` fingerprints and per-environment callback `redirect_uri` values for Gmail).
11. Run DB-backed/authenticated smoke where possible.
12. If anything fails, investigate the failing environment before resetting.
13. Re-fetch the default branch once more before final reporting.

## GitHub Actions patterns

For repos using GitHub Actions:

- Use `gh workflow run` for manual migration/schema workflows.
- Use `gh run list --branch <branch> --json ...` to confirm `headSha`, status, and conclusion.
- If a top-level run appears stuck while public runtime is healthy, inspect job-level state with `gh run view <run-id> --json jobs` before declaring failure.
- A top-level run can lag job completion briefly; job-level evidence and VM/runtime evidence help avoid false failure reports.

## Pitfalls

- Do not trust arbitrary hashes scraped from rendered HTML as deployment revision unless the app explicitly embeds a known build/version field.
- Do not confuse a successful Vercel deployment URL with alias promotion; inspect aliases too.
- Do not report “latest” during active merge/push churn unless you re-fetch and verify the final SHA remained stable.
- Do not leave reset/redeploy implied. Explicitly state whether reset was required and whether it was performed.
- Do not treat clean deployment + DB migration as proof that provider runtime env values are current; external-provider smoke may need separate env-parity checks.
- If a skill or workflow reference is missing because of local setup state, continue with repository workflow files and verified platform state; do not encode the missing local setup as a durable limitation.

## Support references

- `references/outbound-agent-three-dev-env-ops.md` — concrete workflow and verification signals from Outbound Agent’s Vercel/Incheon and Tencent Seoul/Tokyo dev environments.
