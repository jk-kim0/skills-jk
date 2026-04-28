---
name: react-hook-lint-false-positive-in-test-mocks
description: Diagnose and fix React Hook ESLint false positives caused by test mock names like `useSomethingMock` inside Vitest/Jest mock factories.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [react, vitest, jest, eslint, hooks, testing, ci]
---

# React Hook lint false positives in test mocks

Use this when CI or local lint/build fails with `react-hooks/rules-of-hooks` in a test file even though no real Hook misuse was intended.

Typical error:

```text
React Hook "useSomethingMock" is called in function "default" that is neither a React function component nor a custom React Hook function.
```

## Root cause pattern

In test files, a mock variable is often named like:

```ts
const usePathnameExceptLocaleMock = vi.fn();
```

and then referenced inside a mock factory:

```ts
vi.mock('src/utils/client/use-pathname-except-locale.hook', () => ({
  default: () => usePathnameExceptLocaleMock(),
}));
```

ESLint's React Hooks rule can interpret that `use...` identifier as a Hook call, even though it is just a mock function. This commonly breaks both:
- `next lint`
- `next build` (when lint/type checks run during build)

It can also cause downstream Preview/Deploy failures because lint/build failed earlier.

## Fast diagnosis flow

1. Read the CI log first.
2. If the failing line is inside a test file and mentions `react-hooks/rules-of-hooks`, inspect nearby mock variable names.
3. Look for any mocked helper/spy variables starting with `use`:
   - `useRouterMock`
   - `usePathnameMock`
   - `useWhateverMock`
4. Confirm whether that identifier is being invoked inside a `vi.mock()` or `jest.mock()` factory.

## Fix

Rename the mock variable so it no longer starts with `use`.

Example:

```ts
const pathnameExceptLocaleMock = vi.fn();

vi.mock('src/utils/client/use-pathname-except-locale.hook', () => ({
  default: () => pathnameExceptLocaleMock(),
}));
```

Also update all references in the test:

```ts
pathnameExceptLocaleMock.mockReturnValue('/features/demo');
```

## Preferred fix vs alternatives

Prefer:
- Renaming the mock variable

Avoid unless absolutely necessary:
- disabling `react-hooks/rules-of-hooks`
- adding lint ignores to the test file
- rewriting working code just to dodge the rule

The rename is the smallest, cleanest fix.

## Verification

Run the narrowest checks first:

```bash
npm run lint -- --file path/to/test-file.tsx
npm run test:run -- path/to/test-file.tsx
```

Then re-check PR CI:

```bash
gh pr checks <pr-number>
```

## Notes

- This is a lint-rule false positive caused by naming, not a real Hook usage bug.
- If `next build` and `next lint` fail with the same file/line, fix the lint error first before chasing deploy symptoms.
