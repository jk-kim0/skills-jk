# Header JSON-to-TSX authoring follow-up (PR #658)

Session pattern:
- PR #658 originally converted header data from remote layout JSON to checked-in JSON.
- Latest `origin/main` already contained the same baseline change via #660, so #658 was `DIRTY` and not valid as-is.
- The useful follow-up was to keep PR #658 open but rewrite its branch from latest `origin/main` into a narrower route-local-style layout authoring refactor.

Commands/verification used:

```bash
git fetch origin --prune
gh pr view 658 --repo querypie/corp-web-app --json headRefName,headRefOid,baseRefName,mergeStateStatus,files,commits,statusCheckRollup
git merge-base origin/refactor/local-header-data origin/main
git merge-tree <merge-base> origin/main origin/refactor/local-header-data
```

Rewrite pattern:

```bash
# In the existing PR branch worktree
git reset --hard origin/main
# implement follow-up delta only
git rev-list --oneline origin/main..HEAD
git push --force-with-lease origin HEAD:refs/heads/refactor/local-header-data
```

Implementation shape:
- Removed:
  - `src/components/layout/header/data/en.json`
  - `src/components/layout/header/data/ja.json`
  - `src/components/layout/header/data/ko.json`
- Added:
  - `src/components/layout/header/header-data.en.tsx`
  - `src/components/layout/header/header-data.ja.tsx`
  - `src/components/layout/header/header-data.ko.tsx`
- Updated `src/components/layout/header/header-data.ts` to import locale TSX modules and keep `getHeaderData(locale)` unchanged.
- Each locale module exports a `satisfies HeaderType` object.

Regression test addition:
- In `src/components/layout/header/__tests__/header-data.test.ts`, assert locale TSX modules exist and old JSON files do not.

Targeted verification:

```bash
npm run test:run -- src/components/layout/header/__tests__/header-data.test.ts
npx prettier --write \
  src/components/layout/header/header-data.ts \
  src/components/layout/header/__tests__/header-data.test.ts \
  src/components/layout/header/header-data.en.tsx \
  src/components/layout/header/header-data.ja.tsx \
  src/components/layout/header/header-data.ko.tsx
```

PR body language:
- State clearly that the original PR became invalid because #660 landed the baseline work.
- Describe the new PR as a follow-up authoring-surface refactor, not as the original remote-to-local migration.
