# New Vercel monorepo front-app project setup

Use this reference when creating a new Vercel project for a repository where only a subdirectory app should deploy, such as `front/` in a planning/monorepo repository.

## Preflight

1. Verify repository state before changing anything:
   - current cwd and git branch/status
   - whether the deployable app exists on `main` or only on a feature branch/worktree
   - whether an open PR already exists for the deployable app branch
2. Inspect the app subdirectory for:
   - `package.json` scripts
   - lockfile and package manager
   - `next.config.*` / framework config
   - `.env.example`
   - runtime DB/client requirements such as Prisma `DATABASE_URL`
3. Verify Vercel access without printing secrets:
   - check `VERCEL_TOKEN` / `VERCEL_TEAM_ID` presence as booleans only
   - if Hermes terminal does not see shell-exported Vercel env, use `zsh -ic` for read-only probes on this user's macOS setup
4. Check whether the target project name already exists before creating it.
5. Resolve whether the production branch should be `main` or the feature branch that currently contains the app. If `main` does not contain the app yet, setting production branch to `main` will not deploy the intended app.

## Recommended settings for a subdirectory Next.js app

- Project name: user-requested name, e.g. `outbound-dev`
- Git repository: exact GitHub repo, e.g. `querypie/outbound-agent`
- Framework: `nextjs`
- Root Directory: app subdirectory, e.g. `front`
- Install Command: package-manager default or explicit `npm install` when lockfile is `package-lock.json`
- Build Command: `npm run build`
- Output Directory: leave as Next.js default unless the app is static-exported
- Production Branch: the branch that currently contains the deployable app, if the user wants an immediate demo before merge

## Environment questions to ask before first deploy

For Prisma/PostgreSQL-backed demos, Vercel project creation alone is not enough. Ask for or create a dev database before promising a working demo.

Minimum env keys commonly needed:

- `DATABASE_URL`: required for `prisma generate`, app runtime DB access, and seed/schema operations
- `APP_ENV`: only add if the app actually reads it. For seed safety, use an app-recognized deployed-dev value such as `dev-vercel` rather than weakening guards globally.
- `NEXT_PUBLIC_APP_NAME`: only add if the app actually reads it; do not create decorative/public env keys just because they seem plausible.

Ask explicitly:

1. Should the dev demo use an existing DB URL or should a new dev DB be provisioned?
2. Which Vercel environments should receive the DB URL: Production, Preview, Development, or all?
3. May the agent run schema and seed commands against the remote DB?
   - `DATABASE_URL=... npm run prisma:push`
   - `DATABASE_URL=... APP_ENV=dev-vercel npm run db:seed`
4. Is the default `*.vercel.app` domain sufficient, or is a custom domain required?

## Neon/Vercel Marketplace DB setup notes

If the user asks the agent to provision a new dev DB, Vercel Marketplace Neon is a good default for a Vercel-hosted Next.js/Prisma demo when available.

Practical rules:

- Create/link the Neon resource to the intended Vercel project and record resource IDs, region, plan, and whether Neon Auth is enabled.
- Marketplace integrations may inject many env vars (`POSTGRES_*`, `PG*`, `DATABASE_URL_UNPOOLED`, `NEON_PROJECT_ID`, etc.). Keep only the env keys the app actually uses. For a simple Prisma app, that is often just `DATABASE_URL` in Production and Preview.
- Do not keep unused generated env vars merely because the integration created them; they confuse future audits and can mask which connection string the app really uses.
- Run schema setup and seed with the exact deployed DB URL and an app-supported deployed-dev environment marker; if a seed guard rejects non-local hosts, prefer a narrow guard for the chosen dev host/env combination over a broad bypass.
- Verify seeded table counts or a small read-only runtime/API path after seeding, without printing the database URL.

## Deployment and verification

For a working demo, verify both platform configuration and application behavior:

1. Confirm the Vercel project settings after creation/update: team/project ID, linked Git repo, root directory, framework, install/build commands, production branch, and Node.js version.
2. If the repository has multiple apps or the Vercel CLI is run from a subdirectory/worktree, watch for accidental project creation with the wrong name/root (for example a project named after `front`). If it happens, delete the accidental project promptly and report it.
3. Deploy the intended branch/environment, then verify at least:
   - `/login` (or equivalent unauthenticated UI route) returns 200
   - `/` redirects as expected
   - a protected API route returns an expected unauthenticated response rather than a missing-env/build error
4. If adding GitHub Actions for deploys, use clear verb-first workflow/job names that identify the target project and environment, e.g. `Deploy Preview to outbound-dev`.

## Safe reporting

Report project/team/repo/root-directory/branch/build settings, env key names, resource IDs, seed counts, deploy URLs, and HTTP status checks. Never echo raw tokens or database URLs. If a deploy cannot be working yet because DB/env is missing, say so plainly and ask for the blocking value rather than creating a misleading empty deployment.