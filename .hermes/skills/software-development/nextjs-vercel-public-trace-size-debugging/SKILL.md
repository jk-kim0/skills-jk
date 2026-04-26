---
name: nextjs-vercel-public-trace-size-debugging
description: Diagnose and fix Vercel Preview/Deploy failures caused by Next.js output file tracing pulling oversized public assets into API/server function bundles.
---

# When to use

Use this when a Next.js app deploys locally but Vercel Preview/Deploy fails with function size / bundle size / traced files issues after adding or moving large files under `public/`.

Typical signs:
- GitHub Actions Preview deploy fails while local `npm run build` passes.
- Vercel logs mention function size limits or oversized serverless bundles.
- A recent change added many files under `public/` (images, docs, generated assets, route-aligned asset trees, etc.).
- API routes or server code read files from `process.cwd()/public` or similar generic public-root paths.

# Core idea

In Next.js on Vercel, server/API output tracing can conservatively include files reachable from filesystem access patterns. If a route touches `process.cwd()/public` generically, Vercel may bundle large unrelated assets from `public/`, causing function size failures.

The fix is usually **not** to remove the assets. Instead:
1. identify which function is oversized,
2. find generic `public` filesystem access in that function,
3. narrow it to explicit allowed subdirectories,
4. rebuild and re-run CI.

# Procedure

1. Confirm the failing check.
   - Check PR CI first:
     - `gh pr checks <PR_NUMBER>`
     - `gh pr view <PR_NUMBER> --json statusCheckRollup`
   - If only Preview/Deploy fails while test/typecheck/build pass locally, suspect Vercel-specific tracing.

2. Inspect Vercel deploy logs.
   - Use the deployment ID from the failed job.
   - Command:
     - `npx vercel inspect <DEPLOYMENT_ID> --logs`
   - Look for messages about oversized functions or files traced into routes.

3. Find routes that access `public` too broadly.
   - Search for patterns like:
     - `process.cwd()`
     - `path.join(..., "public")`
     - generic `publicDir`
   - Example search:
     - `search_files(pattern='publicDir|process\\.cwd\\(|/public|join\\([^\\n]*public|path\\.join\\([^\\n]*public', target='content', path='src', file_glob='*.{ts,tsx}')`

4. Narrow filesystem access to explicit roots.
   - Bad pattern:
     - `const publicDir = path.join(process.cwd(), "public")`
     - `path.join(publicDir, relativeSrc)`
   - Better pattern:
     - define explicit allowed roots only, e.g.
       - `path.join(process.cwd(), "public", "documentation")`
       - `path.join(process.cwd(), "public", "demo")`
     - or use a typed map such as:
       - `const ALLOWED_ROOTS = { documentation: ..., demo: ... } as const`
   - Avoid generic fallback to all of `public/`.

5. For upload/delete routes, use an explicit directory map.
   - Example shape:
     - `const UPLOAD_DIR_PATHS = { uploads: ..., news: ..., documentation: ..., demo: ... } as const`
     - `type UploadDirName = keyof typeof UPLOAD_DIR_PATHS`
   - Return a typed key from any resolver like `resolveUploadDirName(...)`.
   - Use `UPLOAD_DIR_PATHS[dirName]` instead of recomputing `path.join(process.cwd(), "public", dirName)`.

6. Add or update tests.
   - For download routes, test:
     - allowed prefixes resolve,
     - disallowed prefixes are rejected,
     - traversal attempts are rejected.
   - This prevents future regressions back to generic public-root handling.

7. Re-run local verification.
   - `npm run test:run ...`
   - `npm run typecheck`
   - `npm run build`

8. Inspect local trace artifacts after build.
   - Check `.next/server/app/**/route.js.nft.json` for the affected routes.
   - Verify the trace no longer obviously includes the large asset subtree you added.
   - This is a strong local signal, though Vercel is the final authority.

9. Commit, push, and re-check CI.
   - After push:
     - `gh pr checks <PR_NUMBER>`
     - wait and re-check until Preview/Deploy completes.

# Practical lessons from corp-web-v2

- Adding a large route-aligned asset tree under `public/path/solutions/**` can break Vercel Preview deploys even when local build passes.
- The breakage came from API routes using generic `process.cwd()/public` access, not from the assets themselves.
- Narrowing these routes to explicit subdirectories fixed the deploy without undoing the asset reorganization.
- In this repo, both of these routes were relevant examples:
  - `src/app/api/downloads/file/route.ts`
  - `src/app/api/admin/uploads/route.ts`

# Pitfalls

- Local `next build` may pass while Vercel Preview still fails; do not assume local build is sufficient.
- `vercel build` may be unavailable in a worktree if project settings are not pulled locally; in that case rely on CI + `vercel inspect`.
- When switching from string keys to a typed directory map, update helper function return types too, or TypeScript may reject indexed access.
- Do not “fix” this by deleting or flattening assets first unless the assets themselves are actually wrong. Often the true issue is trace scope, not asset existence.
- If the user wants the tracing fix separated into its own PR, do not assume changing the feature PR's base branch to the fix branch will make Vercel Preview pass. In practice, Preview deploys are evaluated from the PR head branch commit, so the feature PR can still fail until the tracing-fix branch is actually merged or the feature branch is rebased/cherry-picked to include that fix.

# When separating the tracing fix into its own PR

Use this when the user wants deployment/infra scope isolated from content or feature work.

Recommended sequence:
1. Create a dedicated branch from `origin/main` for the tracing fix only.
2. Cherry-pick or reimplement only the API/server trace-scope commits there.
3. Verify that standalone PR with test/typecheck/build plus GitHub/Vercel CI.
4. Remove those commits from the feature/content PR so review scope stays clean.
5. Leave a PR comment linking the prerequisite PR.
6. Expect the feature PR's Preview deploy to remain red until the standalone tracing-fix PR is merged, or until the feature branch explicitly includes the same fix commits again.

This prevents reviewer confusion and matches the user's expectation that CMS/API infrastructure changes be reviewed independently from public-content migration work.

# Verification checklist

- Vercel log no longer reports function size / oversized bundle failure.
- Local `typecheck` passes.
- Local `build` passes.
- Relevant route tests pass.
- PR checks show Preview/Deploy pass, not just test/typecheck/build.
