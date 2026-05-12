---
name: nextjs-typescript-config-contracts
description: Keep routine TypeScript checks stable when Next.js generates or rewrites tsconfig include patterns and typed-route artifacts.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, typescript, tsconfig, typed-routes, build, debugging]
    related_skills: [systematic-debugging]
---

# Next.js TypeScript Config Contracts

Use this when a Next.js repo shows any of these symptoms:
- `next build` rewrites tracked `tsconfig.json`
- build succeeds, but a later plain `tsc --noEmit` or repo `typecheck` fails
- `.next/types/**` or `.next/dev/types/**` generated validators reference deleted or moved routes
- a contract test asserts one tsconfig include shape, but the installed Next version wants another

## Core idea

Separate two contracts instead of forcing one file to satisfy both:
1. the repo's routine TypeScript contract (`tsc --noEmit`, CI, editor expectations)
2. Next's build/dev/typegen contract (whatever the installed Next version currently expects)

When Next mutates `tsconfig.json`, treat that as a framework-managed contract issue first, not as an ordinary local type failure.

## Investigation workflow

1. Reproduce the exact sequence
   - Start clean: remove `.next` and restore tracked tsconfig files.
   - Run the repo's normal routine check first.
   - Run `next build`.
   - Diff tracked tsconfig files.
   - Run the routine typecheck again.

   Typical sequence:
   ```bash
   rm -rf .next
   git checkout -- tsconfig.json
   npm run typecheck
   npm run build
   git diff -- tsconfig.json
   npm run typecheck
   ```

2. Inspect the generated artifacts, not just the error message
   - Check whether `.next/types/validator.ts` and `.next/dev/types/validator.ts` exist.
   - Search them for deleted routes or handlers.
   - Confirm whether the problem is stale generated files, tracked config churn, or both.

3. Check the installed Next implementation directly
   - Search `node_modules/next/dist/**` for the exact include pattern or message.
   - High-value strings:
     - `.next/dev/types`
     - `reconfigured your tsconfig.json`
     - `tsconfigPath`
   - Read the current implementation before inventing a workaround. Next behavior can change across versions.

4. Check whether the installed Next version supports a dedicated build tsconfig
   - Current Next releases expose `typescript.tsconfigPath` in `next.config.ts`.
   - If supported, prefer config separation over post-build file restoration hacks.

## Recommended fix pattern

When routine `tsc` should stay on a stable tracked config, but Next wants broader includes during build:

1. Keep `tsconfig.json` as the routine contract.
   - Include only the generated paths that routine `tsc` should read.
   - Example: keep `.next/types/**/*.ts` but omit `.next/dev/types/**/*.ts` if that is the stable CI/editor contract.

2. Add a dedicated Next-owned config, e.g. `tsconfig.next.json`:
   ```json
   {
     "extends": "./tsconfig.json",
     "include": [
       "next-env.d.ts",
       "src/**/*.ts",
       "src/**/*.tsx",
       "src/**/*.mts",
       "tests/**/*.ts",
       "tests/**/*.tsx",
       "tests/**/*.mts",
       ".next/types/**/*.ts",
       ".next/dev/types/**/*.ts"
     ]
   }
   ```

3. Point Next at that file in `next.config.ts`:
   ```ts
   import type { NextConfig } from "next";

   const nextConfig: NextConfig = {
     typescript: {
       tsconfigPath: "tsconfig.next.json",
     },
   };

   export default nextConfig;
   ```

4. Keep routine scripts unchanged unless the repo explicitly wants otherwise.
   - `npm run typecheck` can keep using plain `tsc --noEmit` against `tsconfig.json`.
   - `next build` will use the dedicated Next config.

## Verification

Verify all of these, in order:

1. contract test for tracked config shape
2. routine typecheck before build
3. clean `next build`
4. `git diff -- tsconfig.json` after build
5. routine typecheck after build
6. if the repo has a combined CI script, run that both before and after a clean build

Example:
```bash
node --test tests/typecheck-tsconfig-contract.test.mjs
npm run typecheck
rm -rf .next
npm run build
git diff -- tsconfig.json
npm run typecheck
npm run test:ci
```

## Good regression-test shape

Prefer a contract test that asserts both sides explicitly:
- tracked `tsconfig.json` keeps the stable routine include set
- dedicated Next config includes the extra generated paths Next expects
- `next.config.ts` actually points to the dedicated config

This catches both regressions:
- Next mutating tracked config again
- someone deleting the dedicated config wiring later

## Pitfalls

- Do not assume a stale validator file is the root cause before checking the installed Next source. Newer Next versions may already filter some generated paths during build.
- Do not “fix” this only by excluding `.next/dev` everywhere if the installed Next build actually expects that include in its own config contract.
- Do not stop after proving `next build` passes. The real bug class is often “build passes but leaves the repo in a broken post-build state.”
- Do not rely on memory of old Next behavior. Search the installed `node_modules/next` version and docs every time this class of issue appears.

## When this pattern is the right answer

Use config separation when all of these are true:
- Next wants to manage tsconfig include patterns
- the repo wants a stable tracked `tsconfig.json`
- routine `tsc` or CI should remain insulated from transient build/dev generated artifacts
- post-build cleanliness matters as much as build success
