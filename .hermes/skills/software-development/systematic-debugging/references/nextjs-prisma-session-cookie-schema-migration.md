# Next.js + Prisma session cookie schema migration 500s

Use when a deployed Next.js App Router app suddenly returns 500 for authenticated or previously authenticated users after a user-id schema migration.

## Symptom signature

- Public login page renders normally.
- Root or protected routes return 500 only for some browsers/users.
- Vercel Runtime Logs show Prisma errors like:
  - `PrismaClientKnownRequestError`
  - `Invalid prisma.user.findUnique() invocation`
  - `P2007`
  - `invalid input syntax for type uuid: "<legacy-id>"`
- The failing request has an old session cookie, for example a CUID value, while the current database column is PostgreSQL UUID.

## Root cause pattern

A stale browser cookie can survive a schema/id-format migration.

If auth code blindly does:

```ts
const userId = cookieStore.get(sessionCookieName)?.value;
await prisma.user.findUnique({ where: { id: userId } });
```

then PostgreSQL UUID columns can reject legacy non-UUID cookie values before Prisma can simply return `null`.

The bug is not that the user is unauthenticated; it is that stale unauthenticatable state reaches the database adapter as an invalid typed value.

## Investigation recipe

1. Reproduce with curl using the exact stale cookie value from logs or the affected browser:

```bash
curl -sS -D /tmp/headers -o /tmp/body \
  -H 'Cookie: outbound_session=<legacy-id>' \
  https://example.com/
```

2. Query Vercel Runtime Logs around the reproduction and confirm the deployment id, path, status, and Prisma error.
3. Inspect the current Prisma schema for the id column type.
4. Trace the auth helper that reads the cookie and calls Prisma.
5. Add a regression test proving invalid session-cookie ids are rejected before `prisma.user.findUnique` is called.

## Fix pattern

Validate the session id format before issuing the typed database query.

Example for UUID-backed `User.id`:

```ts
const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function isValidSessionUserId(userId: string) {
  return uuidPattern.test(userId);
}

export async function getCurrentUser() {
  const cookieStore = await cookies();
  const userId = cookieStore.get(sessionCookieName)?.value;
  if (!userId || !isValidSessionUserId(userId)) {
    return null;
  }

  return prisma.user.findUnique({ where: { id: userId } });
}
```

Treat invalid session ids as unauthenticated state and let the normal login redirect flow handle them.

## Verification checklist

- Targeted auth test passes and asserts invalid ids do not call Prisma.
- Typecheck/build runs under the same Node major as the Vercel project when Prisma/Next versions are sensitive to runtime version.
- Deployed URL with the stale cookie returns the expected unauthenticated redirect/login response, not 500.
- Fresh Vercel logs for the new deployment show 307/200 or the expected response, while old 500 rows remain attributable to the previous deployment id.

## Pitfalls

- Do not only clear your local/browser cookie and call the issue fixed; future users may still have stale cookies.
- Do not rely on Prisma returning `null` for every malformed id. Typed database adapters can fail before a normal not-found result.
- Distinguish redirect-shell HTML from a real 500: a bare 307 response body may include a Next redirect/error shell, but `curl -L` should reach the final login page with 200.
