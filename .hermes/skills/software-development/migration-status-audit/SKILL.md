---
name: migration-status-audit
description: Audit a documented multi-phase migration or project plan against actual repository state to determine completed, in-progress, and remaining work.
trigger:
  - User asks to review a migration plan document and report current status
  - User asks "what's left", "progress check", "remaining work" for a phased project
  - User points to a docs/** plan document and asks for a comprehensive status report
  - Cross-checking a documented roadmap/plan against actual repo state
---

# Migration / Multi-Phase Project Status Audit

When a user asks to understand what remains in a documented migration or phased project plan, follow this systematic audit methodology. Do not rely on the plan document alone — always cross-reference with the actual repository state.

## Pre-flight

1. Confirm current repository (`pwd`, `git remote -v`).
2. Confirm current branch vs target baseline (`git branch --show-current`, `git log origin/main --oneline -n 5`).
3. Read the plan document(s) the user referenced.
4. Identify the plan's phases, collections, endpoints, or milestones.

## Phase 1: Document Extraction

Extract from the plan document:
- Phase definitions and scope boundaries
- Collection / endpoint / feature enumeration
- Completion criteria per phase
- Target architecture or directory conventions
- Dependencies between phases

## Phase 2: Repository State Cross-Check

For each phase, collection, or endpoint enumerated in the plan, verify actual state:

### For MDX / content collections
- `find src/content/<collection> -name "*.mdx" | wc -l` — file count
- `find src/content/<collection> -name "*.mdx" | sed ... | sort -u | wc -l` — unique IDs
- `find src/app -path "*/t/<collection>*" -name "page.tsx"` — verification routes
- Check locale coverage: count per `.{en,ko,ja}.mdx`

### For routes / endpoints
- `find src/app -name "page.tsx" | grep <pattern>` — route existence
- Check if route uses DynamicPage / Blob-backed rendering vs static / route-local
- Check for `page.{locale}.tsx` route-local authoring files

### For PRs / branches
- `gh pr list --state open --limit 50` or `gh api repos/<owner>/<repo>/pulls?state=open`
- Categorize by status: Draft vs Ready, updated time
- Map PRs to plan phases/collections

### For external source repos
- If migration sources content from another repo (e.g. corp-web-contents), check that repo for unmigrated families
- `find <external-repo>/<source-path> -type d | sort` — remaining source families

## Phase 3: Gap Analysis

Produce a structured comparison table with columns:
- Phase / Collection / Endpoint
- Plan Status (as documented)
- Actual Status (as verified)
- Gap (mismatch, incomplete, missing)
- Blocking PR or open branch

Special attention to:
- Collections documented as "migrated" but missing files on main
- Routes existing only as `/<locale>/t/*` verification but not public
- Draft PRs waiting for public release
- Source content in external repo that has no target in local repo
- Dynamic/Blob-backed routes still in use vs static replacements

## Phase 4: Synthesis & Reporting

Report in this order:
1. **Completed** — phases/collections that fully satisfy plan criteria
2. **In Progress** — open PRs, partial implementations, verification routes
3. **Remaining** — items with no implementation yet, identified by cross-checking plan with repo state
4. **Blockers** — unresolved dependencies, missing external content, policy decisions

Use concise tables for quantitative data (file counts, IDs, PR numbers). Use bullet lists for qualitative gaps.

## Pitfalls

- Do not trust the plan document's "Current main HEAD status" section at face value — always verify file and route existence independently.
- A collection having MDX files does not mean it has verification routes; check both.
- A PR being "open" does not mean it's the latest state; check `updated_at` and actual branch tip.
- External source repos may have content that appears in the plan as "already migrated" but was actually skipped.
- `src/app/[...slug]/page.tsx` with `DynamicPage` indicates Blob-backed content still in use — count these as NOT migrated.
- Distinguish clearly between `/<locale>/t/*` verification routes and canonical public routes when reporting status.

## Reference: Audit Command Cheat Sheet

```bash
# Collection inventory
for c in blog whitepapers events news; do
  echo "=== $c ==="
  find src/content/$c -name "*.mdx" 2>/dev/null | wc -l | xargs echo "files:"
  find src/content/$c -name "*.mdx" 2>/dev/null | sed 's|.*/\([^/]*\)-[^/]*\.[^.]*\.mdx$|\1|' | sort -u | wc -l | xargs echo "unique IDs:"
  find src/app -path "*/t/$c*" -name "page.tsx" 2>/dev/null | sort
  echo ""
done

# Route check (non-archived active pages)
find src/app -name "page.tsx" | grep -v archived | grep -v internal | sort

# PR status
gh api repos/<owner>/<repo>/pulls?state=open --jq '.[] | "\(.number) | \(.title) | draft:\(.draft) | updated:\(.updated_at)"'

# External source check  
find ../<external-repo>/<source-path> -maxdepth 2 -type d | sed 's|../<external-repo>/<source-path>/||' | sort
```