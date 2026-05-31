# Vercel CLI local link and command safety

Use this reference when a repository checkout is not Vercel-linked, `vercel env pull` fails with `Your codebase isn’t linked to a project on Vercel`, or there is confusion about whether a Vercel CLI command deploys.

## Key behavior

- A bare `vercel` command is a deployment command.
- Vercel CLI help describes `deploy` as the default command, so `vercel` is equivalent to `vercel deploy` for the current directory/path.
- Do not run bare `vercel` when the intent is only inspection, env retrieval, linking, or logs.
- Use explicit subcommands for non-deploy operations:
  - `vercel link --yes --project <project> --scope <scope>`
  - `vercel env pull <file> --yes --environment=<env> --scope <scope>`
  - `vercel inspect <url-or-id> --scope <scope>`
  - `vercel ls <project> --scope <scope>`
  - `vercel logs <deployment-id> --scope <scope> --project <project> ...`

## Local link recovery pattern

When `vercel env pull` fails because the checkout is not linked:

```bash
vercel link --yes --project outbound-dev --scope querypie
```

Then verify without printing secrets:

```bash
rm -f .env.production.local.tmp
vercel env pull .env.production.local.tmp --yes --environment=production --scope querypie >/tmp/vercel-env-pull.log
node - <<'NODE'
const fs = require('fs');
const s = fs.readFileSync('.env.production.local.tmp', 'utf8');
console.log(JSON.stringify({
  hasDatabaseUrl: /^DATABASE_URL=/m.test(s),
  hasDirect: /^DATABASE_DIRECT_URL=/m.test(s),
  lineCount: s.split(/\n/).filter(Boolean).length,
}, null, 2));
NODE
rm -f .env.production.local.tmp
```

## Git hygiene

- `vercel link` may create `.vercel/project.json` and may also modify `.gitignore` or create a local `.gitignore`.
- In repos that intentionally keep `.gitignore` minimal, do not commit Vercel CLI's automatic ignore changes without explicit approval.
- Prefer reverting tracked `.gitignore` changes and adding local-only entries to `.git/info/exclude`, for example:

```bash
printf '%s\n' '/.vercel/' '/front/.vercel/' '/front/.env.production.local.tmp' >> .git/info/exclude
```

- Remove temporary env files after verification.
- Final verification should include clean `git status --short --branch` and a successful explicit `vercel env pull` command.

## Interpretation for outbound-agent

- The Vercel runtime env may contain `DATABASE_URL` but not `DATABASE_DIRECT_URL`.
- If `DATABASE_DIRECT_URL` is absent from Vercel env, do not treat that as a failed link; DB migration/reset workflows may correctly source the direct URL from GitHub Environment secrets instead.
