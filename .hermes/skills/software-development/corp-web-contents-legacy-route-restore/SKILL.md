---
name: corp-web-contents-legacy-route-restore
description: Restore deleted or deprecated corp-web-contents routes by using commit log evidence to distinguish true removals from route migrations, then prefer redirects to current equivalents instead of reviving stale duplicate content.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-contents, legacy-routes, redirects, git-history, route-migration, korean-content]
---

# corp-web-contents legacy route restoration

Use this when a user asks to find deleted/deprecated pages in `corp-web-contents` and restore them.

## Key rule: stay inside the named repo

If the user says `corp-web-contents`, do not widen scope to `corp-web-app`, `querypie-docs`, or external docs unless the user explicitly asks. The user may be asking about website content routes only, not product-manual repos or app-level redirect handlers.

## Preferred investigation method

The user may explicitly want commit-log evidence. In that case, start from `git log` and keep the analysis grounded in commit history.

Recommended commands:

```bash
git log --all --diff-filter=D --name-status --format='COMMIT %H %ad %s' --date=short -- pages layout public config

git log --all --oneline --decorate --date=short -- <specific deleted file paths>

git show <commit>^:<old/path/to/file>
```

## How to classify deletions

Do not assume every deleted Korean file should be recreated.

Classify each deletion as one of:

1. Route migration
   - Old path removed because content moved to a new path.
   - Example pattern: `resources/learn/documentation/...` moved under `features/documentation/...`.
   - Preferred restoration: add or fix redirects.

2. Category/list consolidation
   - Old list/index pages removed because a broader or new listing page replaced them.
   - Preferred restoration: redirect to the new list or category query.

3. Real content removal
   - Page intentionally removed with no replacement.
   - Only recreate content if the user explicitly wants the old content back.

4. Data/config cleanup
   - Example: legacy JSON/layout files removed as outdated.
   - Do not restore unless there is live route breakage or a user requirement.

## Route restoration strategy

Prefer restoring access, not reviving duplicate content.

### First choice: redirects to current canonical routes

If current content exists under a new pathname, restore the old route with `config/redirects.yaml`.

Patterns to look for:
- old documentation subtree -> new documentation subtree
- old blog subtree -> new blog subtree
- old webinar subtree -> new demo/webinar subtree
- old white-paper subtree -> new white-paper subtree

### Use recursive replace redirects for subtree migrations

If a whole subtree moved, use a recursive replace redirect instead of dozens of one-off rules.

Example pattern:

```yaml
- pathname: "/resources/learn/documentation"
  isRecursive: true
  isReplacePattern: true
  redirect:
    destination: "/features/documentation"
    permanent: true
```

This is better than adding many per-article redirects when the new tree preserves relative descendants.

### Add explicit exception redirects for renamed leaves

If a specific old leaf does not match the new subtree structure, add an explicit rule.

Examples from experience:
- `/resources/learn/documentation/product-introduction-download`
  -> `/features/documentation/acp-introduction-download`
- `/resources/learn/documentation/audit-points`
  -> `/features/documentation/github-contents`

## Verification workflow

1. Extract deleted Korean pathnames from commit log.
2. Normalize file paths to request pathnames.
   - Convert `pages/.../ko/content.mdx` to the actual route pathname without the trailing `/ko` directory marker.
3. Compare those old pathnames against `config/redirects.yaml`.
4. Patch missing rules.
5. Validate YAML parsing.
6. Recompute coverage to confirm no deleted Korean pathnames remain uncovered.

Useful script idea:
- derive deleted `ko` routes from `git log --diff-filter=D`
- strip `pages/` prefix and `/content.mdx` suffix
- if the route ends with `/ko`, remove that suffix to get the actual pathname
- check whether each pathname is covered by an exact rule or a recursive parent rule

## Important interpretation lesson

If commit history shows:
- a Korean documentation index deleted in one commit, and
- nearby commits moving blog/white-paper/tutorial/documentation paths to a new subtree,
then the likely bug is missing legacy redirects, not missing current content.

In that case, restoring redirects is the correct fix.

## Git workflow

After patching redirects:

```bash
git checkout -b fix/restore-legacy-routes
# edit config/redirects.yaml
python3 - <<'PY'
from pathlib import Path
import yaml
yaml.safe_load(Path('config/redirects.yaml').read_text())
print('YAML OK')
PY
git add config/redirects.yaml
git commit -m "fix: restore legacy korean documentation routes"
git push -u origin <branch>
gh pr create ...
```

## PR summary guidance

Explain clearly:
- which commit logs showed the deletion/migration
- that the issue was route restoration, not content recreation
- which old Korean routes were uncovered
- which recursive and explicit redirects were added
- how YAML and coverage were verified

## Pitfalls

- Do not wander into other repos when the user names one repo explicitly.
- Do not recreate stale MDX files when the content already exists at a canonical new path.
- Do not rely only on current file structure; use commit log to distinguish migration from removal.
- Do not add many one-off redirects when one recursive replace rule correctly models the migration.
