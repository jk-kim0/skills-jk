# Reference: corp-web-app Migration Audit Example

This is a concrete example of auditing a multi-phase migration plan (`docs/global-site-upgrade-content-unification-plan.md`) against actual repository state.

## Context

- **Repo**: `querypie/corp-web-app`
- **Plan doc**: `docs/global-site-upgrade-content-unification-plan.md`
- **Phases**: Phase 0 (guide import), Phase 1 (baseline), Phase 2 (repo-local loader), Phase 3 (MDX collection migration), Phase 4 (feature endpoint migration)
- **External source repos**: `corp-web-contents` (legacy Blob-backed content), `corp-web-japan` (pattern source)

## Key Commands Used

### 1. Verify current repository and branch state
```bash
pwd
git branch --show-current
git log origin/main --oneline -n 10
git fetch origin main
```

### 2. Read plan documents
```bash
cat docs/global-site-upgrade-content-unification-plan.md
cat docs/global-site-upgrade-phase-scope-exit-criteria.md
cat docs/global-site-upgrade-content-unification-decisions.md
```

### 3. Audit MDX collections
```bash
# Per-collection file and ID count
for c in blog whitepapers events "demo/use-cases" "demo/aip" "demo/acp" news; do
  echo "=== $c ==="
  find src/content/$c -name "*.mdx" 2>/dev/null | wc -l | tr -d ' ' | xargs echo "files:"
  ids=$(find src/content/$c -name "*.mdx" 2>/dev/null | sed 's|.*/\([^/]*\)-[^/]*\.[^.]*\.mdx$|\1|' | sort -u | wc -l | tr -d ' ')
  echo "unique IDs: $ids"
  find src/app -path "*/t/$c*" -name "page.tsx" 2>/dev/null | sort
  echo ""
done
```

### 4. Audit verification routes
```bash
find src/app -path "*/t/*" -name "page.tsx" | sort
```

### 5. Check for DynamicPage (Blob-backed) usage
```bash
find src/app -name "*.tsx" -o -name "*.ts" | xargs grep -l "DynamicPage" 2>/dev/null | sort
```

### 6. Check external source repo for unmigrated families
```bash
# corp-web-contents page-archives families
find ../corp-web-contents/page-archives -maxdepth 2 -type d | sed 's|../corp-web-contents/page-archives/||' | sort

# corp-web-contents features/demo families
find ../corp-web-contents/pages/features/demo -maxdepth 1 -type d | sed 's|../corp-web-contents/pages/features/demo/||' | sort
```

### 7. Check open PRs
```bash
gh api repos/querypie/corp-web-app/pulls?state=open --jq '.[] | "\(.number) | \(.title) | draft:\(.draft) | updated:\(.updated_at)"'
```

### 8. Check static page authoring status
```bash
# Route-local locale pages
find src/app -name "page.en.tsx" | sort

# Non-archived active pages still using dynamic routing
find src/app -name "page.tsx" | grep -v archived | grep -v internal | sort
```

## Key Findings from This Audit

1. **12 MDX collections fully migrated** to repo-local with `/<locale>/t/*` verification routes.
2. **Manuals existed on origin/main** but were not visible in the local checkout branch — cross-checking `git ls-tree origin/main` was necessary.
3. **8 open PRs** for route-local static page conversions + 7 Draft PRs for public release.
4. **20+ archived routes** still need route-local `page.{locale}.tsx` authoring.
5. **`src/app/[...slug]/page.tsx`** and **`src/app/page.tsx`** still use `DynamicPage` (Blob-backed).
6. **Whitepaper gated download flow** and **sitemap generation from repo-local content** are the two largest unimplemented Phase 4 features.

## Nuances

- **Distinguish `t/*` from public routes**: Many collections have verification routes but no canonical public routes. Report them separately.
- **Local branch vs origin/main**: The user was on `fix/archived-locale-assets`, not main. Always check `origin/main` for canonical state.
- **PR updated_at**: Some PRs appear "open" but haven't been updated recently — verify if they're stale.
- **External repo families not in plan**: Some `corp-web-contents` families (e.g. `company/bounty-program`) exist but are not mentioned in migration matrices — note them as potential gaps.
