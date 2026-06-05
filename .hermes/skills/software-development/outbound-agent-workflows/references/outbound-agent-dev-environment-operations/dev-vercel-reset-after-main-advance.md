# dev-vercel reset after main advances

Use this reference when the user asks to reset only dev-vercel / outbound-dev and redeploy, especially after a multi-environment operation where `origin/main` may have advanced during the session.

## Correct completion criteria

Do not declare dev-vercel reset complete from the workflow conclusion alone. Confirm all of these from the `Apply outbound-dev DB Migration` run logs:

- `RESET_DATABASE: true`
- `npm run db:reset`
- `prisma migrate reset --force`
- `Database reset successful`
- `npm run db:seed`
- `prisma db seed`
- `Running seed command \`tsx prisma/seed.ts\` ...`
- `🌱  The seed command has been executed.`
- shared schema repair SQL files, if present, were executed
- final schema check says `Database schema is up to date!` and `DB schema matches Prisma schema.`

Then deploy outbound-dev Production after the reset, even if a Production deploy for the same SHA succeeded earlier. This preserves the user-requested order: reset/seed first, then fresh deploy.

## Recommended commands

```sh
git fetch origin main --prune
TARGET=$(git rev-parse origin/main)
echo "target=$TARGET"

gh workflow run "Apply outbound-dev DB Migration" -f reset_database=true
# identify the new run, then inspect status and logs

gh run view <reset-run-id> --log \
  | grep -E "reset|seed|Database reset successful|The seed command has been executed|migrate reset|db:seed|schema"

gh workflow run "Deploy outbound-dev Production" -f BRANCH=main
# identify the deploy run and wait/check until success

curl -fsSIL --max-time 30 https://outbound-dev.vercel.app/login
curl -fsSIL --max-time 30 https://outbound-dev.vercel.app/sales-demo/home
```

Expected public smoke signals:

- `/login` returns 200
- an authenticated route such as `/sales-demo/home` returns a login redirect, commonly 307, when no session is present

## Reporting wording

Say explicitly:

- the latest `origin/main` SHA used
- reset run URL and success
- which destructive reset/seed log lines were observed
- deploy run URL and success
- public smoke result

If main advanced during the session, state the newer SHA and redo/reconfirm the steps against it before finalizing.
