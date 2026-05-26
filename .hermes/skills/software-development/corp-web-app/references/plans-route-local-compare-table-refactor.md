# Plans Route-Local CompareTable Refactor Notes

Use these notes when refactoring `corp-web-app` plans/pricing pages toward route-local authoring without changing visible content.

## Trigger

- The task touches `src/app/**/plans/**/page.{en,ko,ja}.tsx`.
- The current implementation uses `CompareTable rows={...} columns={...}` or other large page-local data props that hide the authored table semantics.
- The user asks for route-local authoring refactoring only, especially after a content-update PR has already merged.

## Preferred approach

1. Check the referenced PR state first.
   - If the PR is open follow the existing PR branch workflow.
   - If it is merged, create a fresh branch/worktree from latest `origin/main`; do not revive the merged PR branch.
2. Scope the change to the files changed by the referenced PR unless the user broadens the scope.
3. Preserve public behavior and content:
   - no route, canonical, sitemap, middleware, redirect, or navigation changes
   - no visible text changes
   - no metadata value changes
4. Convert data-prop table authoring into JSX composition using the existing CompareTable primitives:
   - `CompareTableHeader`
   - `CompareTableColumnHeader`
   - `CompareTableBody`
   - `CompareTableSection`
   - `CompareTableRow`
   - `CompareTableCell`
   - `CompareTableCellText`
5. Keep the same row labels, column labels, cell values, booleans, and inline React nodes when moving from arrays to JSX.
6. Run Prettier on touched files after the transform.
7. If the route-local authoring pattern is meant to persist, update the repo-local guidance in the same PR, not as a later cleanup:
   - `docs/static-page-route-local-authoring.md`
   - `docs/code-location-conventions.md`
   - `.agents/skills/static-page-route-local-authoring/SKILL.md`
8. In those guidance updates, name the actual CompareTable primitives used by the repo (`CompareTableHeader`, `CompareTableColumnHeader`, `CompareTableBody`, `CompareTableSection`, `CompareTableRow`, `CompareTableCell`, `CompareTableCellText`) so examples do not drift into non-existent component names.
9. Explicitly forbid reintroducing route-level `rows` / `columns` data props or a central plans content object for authored comparison-table content.

## Useful verification

- Confirm no legacy table authoring remains in the touched page files:

```bash
python3 - <<'PY'
from pathlib import Path
files = [
  'src/app/(legacy)/[locale]/plans/acp/page.en.tsx',
  'src/app/(legacy)/[locale]/plans/acp/page.ja.tsx',
  'src/app/(legacy)/[locale]/plans/acp/page.ko.tsx',
  'src/app/(legacy)/[locale]/plans/aip/page.en.tsx',
  'src/app/(legacy)/[locale]/plans/aip/page.ja.tsx',
  'src/app/(legacy)/[locale]/plans/aip/page.ko.tsx',
  'src/app/(legacy)/[locale]/plans/page.en.tsx',
  'src/app/(legacy)/[locale]/plans/page.ja.tsx',
  'src/app/(legacy)/[locale]/plans/page.ko.tsx',
]
for f in files:
    p = Path(f)
    if not p.exists():
        continue
    s = p.read_text()
    print(f, 'rows={', s.count('rows={'), 'columns={', s.count('columns={'), 'CompareTableSection', s.count('<CompareTableSection'))
PY
```

- Run targeted lint on the changed files rather than a broad build unless requested.
- `git diff --check` is a good quick whitespace/syntax-adjacent guard.
- Check the repo-local docs/skill guardrails were actually added when the user asks to preserve the pattern:

```bash
grep -R "rows.*columns\|CompareTableHeader\|Plans/pricing pages\|Plans and pricing table" -n \
  docs/static-page-route-local-authoring.md \
  docs/code-location-conventions.md \
  .agents/skills/static-page-route-local-authoring/SKILL.md
```

## Pitfalls

- Do not move plans pages out of the current route group unless the user explicitly asks for route relocation or Tailwind route migration.
- Do not refactor `CompareTable` itself unless the route-local page refactor requires it.
- Do not leave repo guidance behind when the goal is to keep a route-local authoring pattern durable; update the repo-local docs and checked-in skill in the same PR so future agents and reviewers see the intended contract.
- During a rebase, if `git rebase --continue` opens Vim/noninteractive editor and hangs, rerun with `GIT_EDITOR=true git rebase --continue` after confirming the index is ready.
- If the remote PR branch changes unexpectedly after a force push or CI interaction, fetch the PR branch, compare `HEAD...origin/<branch>`, then reset the local worktree to the verified remote PR head before final reporting.
- If a broad `tsc --noEmit` fails due unrelated existing test/type setup issues, report that separately and rely on targeted checks for the touched files.
- Treat generated `tsconfig.tsbuildinfo` and similar outputs in a broken/incomplete worktree directory as residue; remove the broken directory, run `git worktree prune`, recreate the worktree from the intended base, and reapply the source changes in the verified worktree.
