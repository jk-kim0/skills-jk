---
name: corp-web-app-mdx-collection-migration
description: Migrate corp-web-contents MDX/publication collections into corp-web-app repo-local content, preserving corpus parity, locale coverage, route-aligned assets, docs inventory/matrix alignment, and existing PR workflow.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, mdx, migration, corp-web-contents, publication, content-parity]
---

# corp-web-app MDX collection migration

Use this when migrating or reviewing a corp-web-app repo-local MDX/publication collection sourced from `../corp-web-contents`, especially Phase-style collection migrations with `/t/<locale>/...` verification routes.

## Core workflow

0. Classify the requested migration review before editing.
   - If the user asks whether a migrated page is visually/functionally equivalent to a reference page, do not stop at checking MDX files and `/t/*` route existence.
   - Treat it as a publication-list render-parity audit: compare the actual browser output, inspect the list route source, inspect loader/card fields, and separate corpus/locale gaps from visual shell gaps.
   - A raw verification route that renders a developer sentence plus a text-only `<ul>` proves content ingestion only; it does not mean the feature/page migration is complete.
   - See `references/publication-list-render-parity-audit.md` for the session-derived checklist and corpus-count snippet.

1. Work on the relevant PR branch in a fresh or freshly-reset worktree.
   - For an existing open PR, update the same branch/PR unless the user asks for a new PR.
   - If the branch is already attached to an old worktree, verify it is clean, remove/recreate or hard-reset it from the remote branch before editing.
2. Identify the canonical source root from the current migration docs and real `corp-web-contents` tree.
   - Do not trust collection names alone; verify actual source counts with `git ls-files`.
   - Compare against corp-web-japan when it is the proven migration pattern, but treat `corp-web-contents` as the copy/content source unless the user says otherwise.
   - If the user explicitly chooses a corp-web-japan stage page as the parity source of truth, close the source decision in docs and migrate the supplemental corpus from corp-web-japan rather than leaving it as an open question. Preserve source semantics such as hidden redirect records instead of resurfacing them in list pages.
3. Generate or copy MDX records into the route-aligned repo-local target root.
   - Current corp-web-app collection-flat convention: `src/content/<collection-path>/<id>-<slug>.<locale>.mdx`.
   - Simple families use a one-segment collection path, e.g. `src/content/blog/<id>-<slug>.<locale>.mdx`.
   - Nested route families must keep the route-aligned nested collection path, e.g. demo use cases use `src/content/demo/use-cases/<id>-<slug>.<locale>.mdx`, not `src/content/use-cases/**`.
4. Relocate source `ogImage`/thumbnail assets under a route-aligned `public/<collection-path>/<id>/...` path.
5. Update source-based regression tests.
   - Assert all expected IDs, not just total file count.
   - Assert locale coverage exactly as the source corpus provides it.
   - Assert route-aligned assets exist.
6. Update docs in the same PR when the migration exposes stale planning/inventory assumptions.
   - Check `docs/global-site-upgrade-content-unification-plan.md` and related decisions/phase-scope docs.
   - Check `docs/inventories/mdx-collection-migration-matrix.md`.
   - Check `docs/inventories/content-collection-inventory.md`.
   - Check `docs/inventories/global-route-endpoint-inventory.md` when `/t/*` routes have landed.
   - Search docs for stale source roots, old target names, old baseline SHAs, and wrong collection paths.
   - If the PR changes a planned target collection (for example from `manuals` to `tutorials`), update both the plan document and the migration status/inventory documents in the same PR; do not leave the docs implying the old target or that the work is still only future work.
   - Distinguish current `origin/main` state from current PR state: mark newly migrated collections as "in PR" until merged, while keeping "implemented on main" limited to already-merged families.
   - After rebasing onto a newer `origin/main`, re-check any baseline commit SHA written into docs and amend it if `origin/main` moved during the task.
7. Rebase onto latest `origin/main`, commit/amend, force-push with lease, update PR body, and report CI status without long passive waiting unless asked.

## Proven source mappings

### Tutorials

Canonical source root:

```text
../corp-web-contents/page-archives/learn/tutorials/<category>/<id>/<slug>/<locale>/content.mdx
```

Target root:

```text
src/content/tutorials/<category>/<id>-<slug>.<locale>.mdx
public/tutorials/<category>/<id>/...
```

Routes:

```text
/t/<locale>/tutorials
/t/<locale>/tutorials/:category/:id/:slug
/<locale>/tutorials
/<locale>/tutorials/:category/:id/:slug
```

Important source coverage:
- 23 detail records when legacy category plus numeric ID are considered together.
- Preserve category as a collection subdirectory and route path segment (`dac`, `general`, `kac`, `sac`).
- Preserve numeric IDs inside each category; do not synthesize frontmatter IDs such as `dac-1`.
- EN: 23 records.
- JA: 23 records.
- KO: 23 records.
- Total detail MDX records: 69.
- The list-root `page-archives/learn/tutorials/<locale>/content.mdx` files are separate list/page content and should not be counted as detail records.

Critical pitfall:
- Do not migrate this source into `manuals`. Tutorials and manuals are distinct content types/formats for corp-web-app migration, even if earlier planning docs or corp-web-japan-derived naming suggested mapping `learn/tutorials` to `manuals`.
- Do not delete or repurpose `.agents/skills/manuals-posting/SKILL.md` when adding tutorials. `manuals` remains a separate future collection and its repo-local skill should remain byte-for-byte unchanged unless the task explicitly edits manuals.
- Do not replace manuals import/guidance manifest rows with tutorials rows. For example, `docs/imports/corp-web-japan-guidance-manifest.md` should keep the `.agents/skills/manuals-posting/SKILL.md` entry and add `.agents/skills/tutorials-posting/SKILL.md` as a separate adjacent entry.
- Do not use flat synthesized filenames such as `src/content/tutorials/dac-1-register-databases.en.mdx`, and do not synthesize frontmatter IDs such as `id: "dac-1"`. The expected shape is `src/content/tutorials/dac/1-register-databases.en.mdx` with frontmatter `id: "1"`.
- For tutorials `relatedIds`, use collection-qualified references like `tutorials/sac/4`, not category-only references like `sac/4`. Category-only values may be technically stored by the generic loader, but they are ambiguous outside a tutorials-local resolver and do not match the category subcollection identity (`tutorials/{dac,general,kac,sac}`).
- When changing tutorials related ID shape, update all 69 MDX files consistently, then add/keep a migration test that verifies every related ID matches `^tutorials/(dac|general|kac|sac)/\d+$` and resolves to an existing same-locale tutorial record.
- Do not modify the shared `src/lib/repo-content/publication-repository.ts` for tutorials category routing. Avoid adding generic `routeSegments`, recursive discovery, or `getRouteSegments`; instead treat each category path as an existing flat collection identifier (`tutorials/dac`, `tutorials/general`, etc.) and compose those category repositories in `src/lib/repo-content/tutorials.ts`.
- When fixing or reviewing an existing PR that used `manuals`, flat synthesized tutorial IDs, or category-only related IDs, rename/update only the tutorials-related code, route, content root, asset root, tests, repo-local tutorials skill, and planning docs together so there are no leftover `/manuals` asset refs, `manualsPublicationRepository` imports, stale flat path strings, or `relatedIds: sac/4`-style values.
- In docs, verify the exact tutorials target path string wherever it appears, especially `docs/inventories/content-collection-inventory.md`: it must be `src/content/tutorials/<category>/<id>-<slug>.{locale}.mdx`, not `src/content/tutorials/<category>-<id>-<slug>.{locale}.mdx`.\n- Audit frontmatter relationship fields such as `relatedIds`, not only route/content/asset parity. For tutorials, numeric-only IDs are ambiguous across categories; `category/id` (e.g. `sac/4`) is only tutorials-local, while a shared cross-collection contract should prefer collection-qualified IDs such as `tutorials/sac/4`. Check whether the loader actually resolves the field or only stores string metadata, then recommend docs/tests accordingly.\n\nUseful checks:

```bash
git -C ../corp-web-contents ls-files 'page-archives/learn/tutorials/*/*/*/content.mdx'

python3 - <<'PY'
import subprocess, collections
repo='../corp-web-contents'
files=subprocess.check_output(['git','-C',repo,'ls-files','page-archives/learn/tutorials/*/*/*/content.mdx'], text=True).splitlines()
print(len(files), collections.Counter(p.split('/')[-2] for p in files))
print(len({p.split('/')[3]+'-'+p.split('/')[4] for p in files}))
PY
```

Verification after migration:

```bash
python3 - <<'PY'
from pathlib import Path
from collections import Counter, defaultdict
import re
wt=Path('.')
root=wt/'src/content/tutorials'
mdxs=list(root.glob('*/*.mdx'))
root_mdx=list(root.glob('*.mdx'))
ids_by_cat=defaultdict(set)
locales=Counter()
missing=[]; bad_ids=[]; synthetic=[]; manual_refs=[]
for p in mdxs:
    cat=p.parent.name
    num=p.name.split('-', 1)[0]
    loc=p.name.rsplit('.', 2)[1]
    ids_by_cat[cat].add(num)
    locales[loc]+=1
    text=p.read_text(encoding='utf-8')
    if '/manuals/' in text:
        manual_refs.append(str(p))
    m=re.search(r'^id:\s*"?([^"\n]+)"?', text, re.M)
    if not m or m.group(1) != num:
        bad_ids.append((str(p), m.group(1) if m else None, num))
    if re.search(r'^id:\s*"?(dac|general|kac|sac)-\d', text, re.M):
        synthetic.append(str(p))
    h=re.search(r'^heroImageSrc:\s*"?([^"\n]+)"?', text, re.M)
    if h and not (wt/'public'/h.group(1).lstrip('/')).exists():
        missing.append((str(p), h.group(1)))
print('files', len(mdxs), 'root_files', len(root_mdx))
print('categories', {k: len(v) for k,v in sorted(ids_by_cat.items())})
print('locales', dict(locales))
print('bad_ids', len(bad_ids), 'synthetic_id_frontmatter', len(synthetic))
print('manual_refs', len(manual_refs), 'missing_assets', len(missing))
PY
```

Expected tutorials shape: 69 files under category subdirectories only (`dac` 10, `general` 2, `kac` 3, `sac` 8; EN/KO/JA 23 each), no root-level `src/content/tutorials/*.mdx`, numeric frontmatter IDs only, and no missing assets.

### Demo use cases

Canonical source root:

```text
../corp-web-contents/pages/features/demo/use-cases/<id>/<slug>/<locale>/content.mdx
```

Customer-success duplication pitfall:
- The first five demo use-case records also appear in `../corp-web-contents/page-archives/customers/customer-success-cases/<id>/<slug>/<locale>/content.mdx`.
- corp-web-japan migrated those records into `src/content/use-cases/*.mdx`, not a separate `customer-success-cases` collection.
- In corp-web-app, if `src/content/demo/use-cases/1-5-*` already exists, a PR adding `src/content/customer-success-cases/1-5-*` is likely duplicate data migration unless an explicit product requirement calls for a separate customer-success collection/route family.
- See `references/customer-success-cases-use-cases-duplication.md` for the slug list and verification commands.

Target root:

```text
src/content/demo/use-cases/<id>-<slug>.<locale>.mdx
public/demo/use-cases/<id>/...
```

Routes:

```text
/t/<locale>/demo/use-cases
/t/<locale>/demo/use-cases/:id/:slug
/<locale>/demo/use-cases
/<locale>/demo/use-cases/:id/:slug
```

Important source coverage:
- 29 IDs total.
- EN: 29 records.
- JA: 29 records.
- KO: 6 records, IDs 1-6 only.
- Total MDX records: 64.

Critical pitfall:
- `../corp-web-contents/page-archives/customers/customer-success-cases` is only the customer-success subset for IDs 1-5.
- It overlaps the first five demo use cases but is not the complete use-case corpus.
- If a PR claims corp-web-japan use-case parity, using that archive root will silently omit IDs 6-29.
- Tests must therefore assert IDs 1-29 and locale counts EN=29, JA=29, KO=6.

See `references/demo-use-cases-source-parity.md` for the session-derived verification details and commands.

See `references/tutorials-category-subcollection-pr-followup.md` for the corrected tutorials category subcollection shape, manuals-skill preservation pitfall, and rebase conflict note.

See `references/tutorials-related-id-qualification.md` for why tutorials `relatedIds` should use collection-qualified values such as `tutorials/sac/4`, plus a verification script.

See `references/mdx-plan-inventory-refresh.md` for doc/inventory refresh checks, stale-path grep patterns, and the baseline-SHA rebase pitfall.\n\nSee `references/related-ids-collection-identifiers.md` for relatedIds/frontmatter relationship-field review steps, tutorials category identifier pitfalls, and a verification script for category-local vs collection-qualified references.\n\n## Useful checks

List source coverage:

```bash
git -C ../corp-web-contents ls-files 'pages/features/demo/use-cases/*/*/*/content.mdx'
```

Count by locale:

```bash
python3 - <<'PY'
import subprocess, collections
repo='../corp-web-contents'
files=subprocess.check_output(['git','-C',repo,'ls-files','pages/features/demo/use-cases/*/*/*/content.mdx'], text=True).splitlines()
print(len(files), collections.Counter(p.split('/')[6] for p in files))
print(sorted({p.split('/')[4] for p in files}, key=int))
PY
```

Verify generated local parity after migration:

```bash
python3 - <<'PY'
import re
from pathlib import Path
src=Path('../corp-web-contents/pages/features/demo/use-cases')
wt=Path('.')
def split(s):
    m=re.match(r'^---\n([\s\S]*?)\n---\n?', s)
    return ('',s) if not m else (m.group(1), s[m.end():])
def norm(s): return re.sub(r'\s+',' ',s.replace('\r\n','\n').strip())
missing=[]; diffs=[]; assets=[]
for content in src.glob('*/*/*/content.mdx'):
    id_,slug,loc=content.parts[-4],content.parts[-3],content.parts[-2]
    target=wt/f'src/content/demo/use-cases/{id_}-{slug}.{loc}.mdx'
    if not target.exists(): missing.append(str(target)); continue
    _,sb=split(content.read_text(encoding='utf-8'))
    _,tb=split(target.read_text(encoding='utf-8'))
    if norm(sb)!=norm(tb): diffs.append(f'{id_}-{slug}.{loc}')
for mdx in (wt/'src/content/demo/use-cases').glob('*.mdx'):
    text=mdx.read_text(encoding='utf-8')
    m=re.search(r'^heroImageSrc: "?([^"\n]+)"?$', text, re.M)
    if m and not (wt/'public'/m.group(1).lstrip('/')).exists(): assets.append((mdx.name,m.group(1)))
print(f'missing={len(missing)} body_diffs={len(diffs)} missing_assets={len(assets)}')
PY
```

## Done criteria

- Source root and locale coverage are verified from `corp-web-contents`, not inferred from PR body.
- Local MDX and assets cover the full source corpus for the migration family.
- Tests assert ID and locale coverage.
   - If the task is render parity, the production/list UX is verified separately from content ingestion: localized hero, category/sidebar or drawer, card grid/list, thumbnail/date/badge rendering, progressive controls, responsive behavior, and absence of developer-only verification copy.
   - For resource-list sidebar/category parity, do not leave the category set as an open decision once the user confirms matching GNB/menu links exist. Adopt the reference resource category set for page-body navigation, while exposing only routes that exist or are intentionally part of the verification surface.
- Docs inventory/matrix no longer contradict the implemented migration.
- PR branch is pushed and PR body reflects the final scope.
