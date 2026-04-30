---
name: nextjs-rsc-client-boundary-debugging
description: Debug Next.js App Router CI/build failures caused by React Server Component and Client Component boundary mistakes after component extraction or refactoring.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, react, rsc, client-components, app-router, ci, build, debugging]
---

# Next.js RSC / Client Boundary Debugging

Use this when a Next.js App Router refactor passes casual inspection or even lint/typecheck, but CI or `next build` fails after extracting components.

Typical triggers:
- extracting page-local JSX into a new component file
- moving context-based UI into shared or section components
- passing icons/components/functions as props from `page.tsx`
- introducing `createContext`, `useContext`, hooks, or state into extracted UI

## Core lessons

1. `createContext`, `useContext`, hooks, and state require a Client Component.
- If a file uses them, add `"use client"` at the top.
- Lint/typecheck may not catch this, but `next build` will.

2. Server Components cannot pass function values directly to Client Components.
- This includes component constructors like Lucide icons (`Users`, `Blocks`) passed as props.
- Build errors often say something like:
  - `Functions cannot be passed directly to Client Components`
  - or complain that a module depending on `createContext` is imported into a Server Component tree incorrectly.

3. For this class of issue, `npm run test:ci` alone may be insufficient.
- Always run both:
  - `npm run test:ci`
  - `npm run build`
- The full build is what reliably exposes RSC/client-boundary serialization problems.

## Debug workflow

### 1. Reproduce locally first
Run the same steps CI runs.

```bash
npm run test:ci
npm run build
```

If CI failed on Vercel too, inspect both GitHub Actions and Vercel logs.

```bash
gh pr checks <PR_NUMBER> || true
gh run list --branch <branch> --limit 5
gh run view <RUN_ID> --log-failed
npx vercel inspect <deployment_id> --logs
```

### 2. Classify the failure

#### Case A: missing Client Component directive
Symptoms:
- error mentions `createContext`, `useContext`, hooks, or state in a non-client file
- import trace points to an extracted component file

Fix:
- add `"use client"` to that component file

#### Case B: server → client function prop serialization
Symptoms:
- `Functions cannot be passed directly to Client Components`
- often caused by passing icon components, render functions, callbacks, or component constructors from `page.tsx` into a client component

Fix options, in order of preference:
1. replace function props with serializable values (`tone`, `variant`, `iconName`)
2. move selection logic inside the client component
3. only if truly necessary, convert the parent subtree to client — but avoid widening client scope without a strong reason

Example:
- Bad:
  - server `page.tsx` passes `icon={Users}` into a client component
- Better:
  - pass `tone="crew"`
  - client component chooses `Users` internally based on `tone`

### 3. Re-run both checks locally
After each fix:

```bash
npm run test:ci
npm run build
```

Do not stop after lint/test if the original failure was in build/deploy.

### 4. Push and confirm CI reruns

```bash
git add <files>
git commit -m "fix: <describe boundary fix>"
git push origin HEAD:<branch>

gh pr checks <PR_NUMBER> || true
gh run list --branch <branch> --limit 5
```

## Practical heuristics

- If an extracted component uses context internally, assume it probably needs `"use client"`.
- If a server page passes anything richer than strings, numbers, booleans, arrays, plain objects, or JSX children into a client component, inspect it for serialization risk.
- Lucide icon constructors are functions. Treat them as non-serializable across the server/client boundary.
- A refactor that improves readability can still break build semantics. Readability extraction and RSC boundary safety are separate concerns.

## Good refactor pattern for page-specific UI

When you want better page readability but the extracted UI is not broadly reusable:
- keep `page.tsx` server-side if possible
- extract page-specific UI into a dedicated component file
- if that component needs context/hooks, mark it client
- pass serializable props only
- keep component-internal visual branching inside the client file

## Commit patterns that matched this workflow
- `fix: restore top page imports after hero extraction`
- `fix: mark solution choice card as client component`
- `fix: avoid server-to-client icon props`

## When this skill is especially relevant
- stacked PR follow-up refactors on Next.js App Router repos
- page-local component extraction requested for readability
- CI failures that appear only after otherwise harmless JSX refactors
