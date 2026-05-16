# Tutorials category subcollection PR follow-up

Session learning from correcting a corp-web-app tutorials migration PR.

## Required tutorials shape

Tutorials are not manuals. `page-archives/learn/tutorials/**` must migrate to a separate `tutorials` collection, and legacy tutorial categories must remain visible in both content paths and routes.

Use:

```text
src/content/tutorials/<category>/<id>-<slug>.<locale>.mdx
public/tutorials/<category>/<id>/...
/t/<locale>/tutorials/:category/:id/:slug
```

Implementation note: keep `src/lib/repo-content/publication-repository.ts` unchanged. Treat each category path as its own existing flat collection identifier, for example `family: "tutorials/dac"`, `contentRoot: "src/content/tutorials/dac"`, and `publicBasePath: "/tutorials/dac"`; then compose those category repositories in `src/lib/repo-content/tutorials.ts`.

Categories observed:

```text
dac      10 IDs
general   2 IDs
kac       3 IDs
sac       8 IDs
```

Frontmatter `id` must be the numeric ID inside the category (`"1"`, `"2"`, ...), not a synthesized ID like `"dac-1"`.

## Common mistakes to avoid

- Do not flatten tutorials to `src/content/tutorials/<category>-<id>-<slug>.<locale>.mdx`; use `src/content/tutorials/<category>/<id>-<slug>.<locale>.mdx`.
- Do not route tutorials as `/tutorials/:id/:slug` when category is needed to disambiguate legacy numeric IDs.
- Do not delete or modify `.agents/skills/manuals-posting/SKILL.md`; manuals is a separate collection.
- When replacing a mistaken manuals migration, touch only tutorials-related code/docs/skills. Leave manuals artifacts intact unless explicitly asked.
- In status/planning docs, check the literal path string in `docs/inventories/content-collection-inventory.md` and `docs/inventories/mdx-collection-migration-matrix.md`; both should show the nested category path, not the flat synthesized path.

## Publication repository boundary

Do not change `src/lib/repo-content/publication-repository.ts` just to support tutorials categories. Avoid adding shared concepts such as `routeSegments`, recursive MDX discovery, `getRouteSegments`, or `category` to the generic repository API for this migration.

Preferred pattern:

```ts
const repositoriesByCategory = Object.fromEntries(
  tutorialCategories.map(category => [
    category,
    createPublicationRepository({
      contentRoot: path.join(process.cwd(), 'src/content/tutorials', category),
      family: `tutorials/${category}`,
      publicBasePath: `/tutorials/${category}`,
    }),
  ]),
);
```

Then expose a tutorials wrapper that:

- concatenates `records` from all category repositories,
- concatenates/sorts `list({ locale })` results,
- routes `getDetail({ category, id, slug, ... })` to the matching category repository,
- returns `not-found` for an unknown category.

This keeps category handling in `src/lib/repo-content/tutorials.ts` and preserves the generic repository's existing flat collection contract.

## Rebase conflict note

If a rebase shows changes in `publication-repository.ts`, first check whether they came only from the previous incorrect route-segments approach. The final tutorials migration should leave this shared file byte-for-byte aligned with `origin/main` unless another explicitly scoped change requires it.

## Quick verification

```bash
python3 - <<'PY'
from pathlib import Path
from collections import Counter, defaultdict
import re
root=Path('src/content/tutorials')
files=list(root.glob('*/*.mdx'))
root_files=list(root.glob('*.mdx'))
ids_by_cat=defaultdict(set); locales=Counter(); bad=[]; synthetic=[]; missing=[]
for p in files:
    cat=p.parent.name
    num=p.name.split('-',1)[0]
    loc=p.name.rsplit('.',2)[1]
    ids_by_cat[cat].add(num); locales[loc]+=1
    text=p.read_text()
    m=re.search(r'^id:\s*"?([^"\n]+)"?', text, re.M)
    if not m or m.group(1)!=num: bad.append(str(p))
    if re.search(r'^id:\s*"?(dac|general|kac|sac)-\d', text, re.M): synthetic.append(str(p))
    h=re.search(r'^heroImageSrc:\s*"?([^"\n]+)"?', text, re.M)
    if h and not Path('public', h.group(1).lstrip('/')).exists(): missing.append(str(p))
print('files', len(files), 'root_files', len(root_files))
print('categories', {k: len(v) for k,v in sorted(ids_by_cat.items())})
print('locales', dict(locales))
print('bad_ids', len(bad), 'synthetic_id_frontmatter', len(synthetic), 'missing_assets', len(missing))
PY
```

Expected: `files 69`, `root_files 0`, categories `{'dac': 10, 'general': 2, 'kac': 3, 'sac': 8}`, locales EN/KO/JA 23 each, zero bad/synthetic IDs and missing assets.
