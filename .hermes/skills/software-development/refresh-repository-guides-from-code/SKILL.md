---
name: refresh-repository-guides-from-code
description: Update repository guidance documents by reconciling recent commits with the current codebase, workflows, routes, and tests.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [documentation, git, repository-maintenance, readme, workflow]
---

# Refresh repository guides from code

Use when the user asks to bring repository guidance up to date with the current implementation, or asks to audit/classify which repository docs, plans, READMEs, and guidance files are still valid before deciding what to rewrite.

## Goals

1. Review the recent change window first when an edit/refresh is requested; for a read-only validity audit, at least verify latest `origin/main` and recent last-touch commits for docs.
2. Identify the project-owned guidance files that actually exist.
3. Reconstruct the current contract from code, tests, and workflows.
4. Classify docs as valid, partially valid/stale, invalid/historical, or external-confirmation-needed.
5. Update the guidance docs so they match reality when the user requested edits; otherwise report a prioritized cleanup plan without changing files.

## Procedure

### 1. Start from the latest main-based branch

- Confirm the target repository and active branch/worktree.
- Fetch `origin --prune`.
- Create a fresh docs worktree/branch from `origin/main` unless the user explicitly wants a different base.
- Verify the merge-base matches `origin/main` before editing.

Example:
```bash
git fetch origin --prune
git worktree add .worktrees/docs-refresh-guides -b docs/refresh-guides origin/main
git -C .worktrees/docs-refresh-guides merge-base HEAD origin/main
git -C .worktrees/docs-refresh-guides rev-parse origin/main
```

### 2. Inspect recent commits before reading docs

Default to the last 7 days unless the user gives a different window.

Start with the commit summary view:
```bash
git log --since='7 days ago' --date=short --pretty=format:'%h %ad %an %s' --decorate --all
```

Then inspect the actual touched files, not just subjects. A docs refresh can be wrong if you rely only on commit titles.

Example:
```bash
for c in $(git log --since='7 days ago' --pretty=format:'%H' --reverse); do
  echo '---'
  git show --stat --format='%h %ad %an %s' --date=short --compact-summary --name-only --no-patch "$c"
  git diff-tree --no-commit-id --name-only -r "$c"
done
```

Look for themes such as:
- route additions/removals
- canonical URL changes
- content-source migrations
- workflow/CI/deploy changes
- testing-policy changes
- previous docs commits that may already be stale again

Important lesson:
- The changed-file list often reveals scope splits that commit titles hide, such as "detail route added" versus "list page still gated" or "detail page made local while list cards still link upstream".

### 3. Inventory only project-owned guidance files that really exist

Do not assume a `docs/` tree exists.
Do not treat worktree copies, vendored package docs, or generated markdown as repository guidance.

Common in-scope files:
- top-level project guide
- top-level agent/instructions guide
- a real `docs/` directory if present
- intentional markdown notes for retained assets or operations
- component-local READMEs under source directories when they describe reusable implementation contracts
- test-runner READMEs under a separate `tests/` package
- checked-in plan/proposal files when they are clearly part of the repo, not local Hermes session state

For read-only validity audits, build a compact inventory first:
```bash
git ls-files | perl -ne 'print if m{(^|/)(README|CHANGELOG|TODO|PLAN|ROADMAP|NOTES|AGENTS|CLAUDE|docs|plans|wiki|\.agents|\.hermes/plans)/|\.(md|mdx|txt)$}i' | sort
```
Then separately search for plan-like files and plan-like language:
```bash
git ls-files | grep -Ei '(^|/)(plan|plans|roadmap|todo|migration|proposal|design).*\.(md|mdx|txt)$|\.(plan|plans)\.' || true
```

Important lessons:
- When the request mentions a docs directory that is absent, narrow scope to the project-owned markdown files that actually exist and state that explicitly.
- Do not call local `.hermes/plans` absent/present from memory; inspect it. If it is absent and no tracked plan files exist, explicitly say there are no active local plan files before classifying ordinary docs.

### 4. Reconstruct the live contract from implementation

Check the files that define real behavior:
- `package.json`
- route/page files under the app tree
- redirect/API route files
- sitemap/robots/metadata files
- content loaders and source directories
- tests that encode current policy
- GitHub Actions workflow files

Use tests as evidence when they clearly assert intended behavior.

Questions to answer:
- Which public routes really exist now?
- Which paths are pages versus redirects?
- Which routes are launch-gated or intentionally excluded from the sitemap?
- Are detail pages canonicalized by `id`, slug, or both?
- Are list pages and detail pages following the same model, or is there a mixed contract (for example local detail rendering but upstream list-card hrefs)?
- Are any legacy compatibility routes intentionally retained for only one content family?
- What files are the actual content source of truth?
- Which commands in the docs are still valid?
- Do the docs mention files or setup paths that no longer exist?

### 5. Classify validity before editing when requested

When the user asks which docs/plans are valid, do not jump straight to rewriting. Produce an evidence-backed classification:

- **Valid**: core claims match current code/workflows/tests; only minor wording drift or external links remain.
- **Partially valid / needs refresh**: the high-level idea is still true, but route inventory, filenames, scripts, line numbers, runtime location, or implementation details have drifted.
- **Invalid / historical only**: the doc describes unimplemented plans, missing files/scripts, obsolete architecture, or a component structure that no longer exists. Prefer archive/delete/rewrite recommendations over treating it as active guidance.
- **External confirmation needed**: local code cannot prove a claim because it depends on Vercel settings, private dashboards, internal service URLs, credentials, or live operational state.

Useful cross-checks:
```bash
# root package commands and versions
node -e "const p=require('./package.json'); console.log(JSON.stringify({scripts:p.scripts, engines:p.engines, next:p.dependencies?.next, react:p.dependencies?.react}, null, 2))"

# separate test package scripts, if present
[ -f tests/package.json ] && node -e "const p=require('./tests/package.json'); console.log(JSON.stringify(p.scripts,null,2))"

# workflow reality
git ls-files '.github/workflows/*' | sort

# app-route reality
git ls-files 'src/app/**/page.tsx' 'src/app/**/route.ts' 'src/app/**/sitemap*.ts' | sort

# docs last-touch evidence
for f in README.md docs/*.md tests/README.md src/**/README.md; do [ -e "$f" ] && printf '%s\t' "$f" && git log -1 --format='%cs %h %s' -- "$f"; done
```

When docs mention file paths or npm scripts, verify them against both root `package.json` and nested packages such as `tests/package.json` before marking them stale. A script can be valid but scoped to a subpackage.

### 6. Fix the most common stale-doc patterns

#### Old setup/tooling references

Remove or rewrite references to:
- setup commands that no longer exist
- guides or companion files that are missing
- local config/skill paths that are not actually present in the repo

#### URI policy drift

Align docs with the real route model:
- canonical index paths
- detail routes
- redirect-only surfaces
- launch-gated pages
- sitemap expectations
- legacy compatibility routes that intentionally remain for only a subset of content
- mixed list/detail behavior where index cards still point upstream even though local detail routes now exist

#### Content-source drift

Document the actual source of truth:
- source directories
- frontmatter/data contracts
- gating markers or content split markers
- loader paths that matter to editors
- redirect allowlist behavior when unmatched-path handling is part of the user-visible contract

#### Verification drift

Do not leave generic "always run a dev server" guidance if the project really uses CI or preview deployments first.

### 6. Keep statements concrete

Prefer implementation-backed statements such as:
- a route is local and MDX-backed
- a path is redirect-only
- a page is intentionally excluded from sitemap coverage
- a query string is preserved across a redirect

Avoid vague prose that will drift quickly.

### 6.1 When docs cite repository file paths as reference examples, prefer commit-pinned GitHub links

If the user wants readers to open example files directly from the docs, do not leave those examples as plain code spans only.
Use GitHub links pinned to an immutable commit SHA so the reference keeps pointing at the exact reviewed snapshot even if later refactors move or rewrite the file.

Preferred rule:
- real file or directory examples -> link them
- generic placeholder patterns such as `src/app/<route>/page.tsx` or `src/content/<family>/<slug>.mdx` -> keep them as plain code patterns

Recommended source SHA for these links:
- use the latest reviewed repository snapshot that the doc is intentionally describing
- in a repo-doc refresh against current reality, this is often the current `origin/main` SHA
- in PR-specific developer guides, this can also be the exact base/main snapshot the examples were validated against

Link shapes:
- file -> `https://github.com/<owner>/<repo>/blob/<sha>/<path>`
- directory -> `https://github.com/<owner>/<repo>/tree/<sha>/<path>`

Practical steps:
1. decide which cited paths are real examples versus generic patterns
2. resolve the immutable commit SHA you want to freeze
3. convert real example paths to markdown links using `blob/<sha>` or `tree/<sha>`
4. keep placeholder conventions unlinked so the prose still reads as a reusable pattern rather than a claim about one exact file

Why this matters:
- later code movement does not silently repoint the docs at a different file
- reviewers can inspect the exact snapshot discussed in the document
- "example path" and "generic naming contract" stay clearly separated

### 6.2 When importing guidance from a sibling repository, adapt examples against current target repo reality

Use this when the user asks to move or i18n documentation from another repository, such as importing `corp-web-japan` guidance into `corp-web-app`.

Process:
1. Fetch/read the source documents and record the source repository commit SHA, not just `main` as a moving label.
2. Inspect the target repository for current equivalent examples before writing: route files, content roots, component paths, loaders, assets, README/docs indexes, and import manifests.
3. Replace source-repo examples only when a real target-repo equivalent exists.
4. If no appropriate target example exists, explicitly mark that section `TODO` and keep the source example/reference as conceptual context rather than inventing parity.
5. Update any import/manifest document so an item moved from `exclude` to `adapt` is not listed in both sections.
6. Update the repository README/docs index when adding new top-level guidance files or i18n companions.

Targeted verification for this class:
```bash
git diff --check
python3 - <<'PY'
import pathlib, re, urllib.parse, sys
root=pathlib.Path('.').resolve()
files=[pathlib.Path(p) for p in sys.argv[1:]]
issues=[]
for f in files:
    text=f.read_text()
    for i,line in enumerate(text.splitlines(),1):
        if re.match(r'^(<<<<<<<|=======|>>>>>>>)', line):
            issues.append((str(f), f'conflict marker line {i}'))
        if re.match(r'\s*\d+\|', line):
            issues.append((str(f), f'line prefix line {i}'))
    for m in re.finditer(r'\[[^\]]+\]\((\.\.?/[^)]+)\)', text):
        url=m.group(1).split('#',1)[0]
        target=(f.parent/urllib.parse.unquote(url)).resolve()
        if str(target).startswith(str(root)) and not target.exists():
            issues.append((str(f), f'missing link {url} -> {target.relative_to(root)}'))
if issues:
    print('\n'.join(map(str, issues)))
    sys.exit(1)
print('targeted markdown sanity OK')
PY README.md docs/<changed-doc>.md
```

Pitfalls:
- Do not cite a nonexistent i18n companion just because it would be symmetrical; first verify the file exists.
- Markdown links to Next.js route segment paths need percent-encoded brackets in URLs, for example `%5Blocale%5D`, `%5Bid%5D`, and `%5Bslug%5D`.
- Keep generic patterns as code spans; link only real examples.
- For docs-only PRs, still verify actual PR checks after creation; some repos attach docs-only workflow runs.
- Do not update only the visible path in a commit-pinned GitHub link after a route/file promotion. The old commit may contain `src/app/t/...` while the current commit contains `src/app/...`; changing the path while leaving the old SHA creates a broken historical link. If the doc is meant to show a historical before/after snapshot, preserve the historical path and SHA. If the doc is meant to show a current active reference, update both the path and the SHA to a commit where that path exists, then validate with `git cat-file -e <sha>:<path>`.

### 7. Verify the doc update itself

Before finishing:
- run `git diff --check`
- search for stale phrases you intended to remove
- confirm every referenced file, route, and command still exists
- confirm you did not document worktree-only or vendor-tree state as if it were repo state
- if the refreshed docs include static scan counts, re-run the scan script from the same baseline SHA and update all related rows together, not just the row that obviously changed
- if docs contain relative Markdown links or commit-pinned GitHub `blob/<sha>` / `tree/<sha>` links, validate that they resolve; use `scripts/validate-markdown-references.py` from this skill when available
- when docs reference GitHub issues, avoid adding auto-closing keywords such as `Closes #...` unless the user explicitly wants that issue closed on merge

Helpful commands:
```bash
git diff --check
git status --short
python3 <skill-dir>/scripts/validate-markdown-references.py docs
```

For broad docs refreshes, add targeted stale-pattern checks based on the drift you just fixed, for example:
```bash
python3 - <<'PY'
from pathlib import Path
patterns = [
    'Source baseline: this PR branch',
    'src/app/t/eula',
    'src/app/t/terms-of-service',
    'https://stage.querypie.ai/t/platforms',
    '`/t/plans`',
    'Closes #',
]
for p in sorted(Path('docs').rglob('*.md')):
    text = p.read_text(errors='replace')
    hits = [pat for pat in patterns if pat in text]
    if hits:
        print(p, hits)
PY
```

### 8. Commit and push

Use a focused docs commit.

Example:
```bash
git add <changed-doc-files>
git commit -m "docs: refresh repository guides for current implementation"
git push -u origin HEAD
```

### 9. Reporting checklist

Report:
- repository path, branch, and latest `origin/main` SHA used as the baseline
- whether active plan files exist, and where they were searched
- which guidance files were actually in scope
- a validity classification: valid, partially valid/stale, invalid/historical, external-confirmation-needed
- concrete evidence for stale/invalid verdicts: missing files, missing scripts, drifted route inventory, stale line-number diagrams, or generated/untracked artifact assumptions
- prioritized cleanup/update recommendations
- if edits were requested: recent change themes reviewed, contract changes reflected, verification performed, branch and commit pushed

## Practical lessons

- Verify whether a docs directory really exists before promising to update it.
- Guidance refreshes should be grounded in current code, tests, and workflows rather than prior prose.
- Route-policy docs often lag behind migration work; reconcile them against live routes and sitemap behavior.
- Verification instructions should match the repository’s real workflow instead of generic local-server advice.
- Ignore markdown under worktrees, dependency directories, and other generated/vendor trees when identifying the real project documentation set.
- For read-only documentation validity audits, it is acceptable to work on the current clean checkout without creating a docs branch, but still fetch/prune and verify `main` is aligned with `origin/main` before making current-state claims.
- When a doc calls something an API/test/script generally, check nested package boundaries before declaring it missing; for example a Playwright script may live under `tests/package.json` rather than the root package.
- Distinguish generated artifacts from missing source files. A path like `public/build-info.json` may be valid runtime output even when it is intentionally untracked.
- Treat component-local READMEs as suspect when they list files/classes that no longer exist; cross-check against the actual component directory before trusting architecture diagrams in prose.
