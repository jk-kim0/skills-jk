# Related IDs and collection identifiers in corp-web-app MDX migrations

Session-derived review notes from PR 639 / tutorials migration.

## What to inspect

When reviewing migrated MDX frontmatter, do not stop at counts, routes, and assets. Also trace relationship fields and identifier contracts:

1. Locate frontmatter fields (`relatedIds`, legacy `relatedPosts`, `relatedItems`, etc.).
2. Find the loader type/schema and parser behavior.
3. Find all consumers/resolvers. Distinguish stored-only metadata from rendered/validated relationships.
4. Compare source legacy relationship format to migrated format.
5. Check whether IDs are globally unique, collection-local, or category-local.
6. Add or request tests that validate both identifier grammar and reference existence.

## Current corp-web-app publication loader behavior

`src/lib/repo-content/publication-repository.ts` currently treats `relatedIds` as stored metadata only:

- `PublicationRecord.relatedIds: string[]`
- non-array frontmatter becomes `[]`
- array items are stringified with `String(item)`
- no grammar validation
- no built-in resolver in `createPublicationRepository`

Therefore many shapes are technically accepted, but not necessarily semantically correct.

## Tutorials-specific finding

PR 639 migrated source `relatedPosts` values like:

```yaml
relatedPosts:
  - /resources/learn/tutorials/sac/4/use-web-terminal
```

into repo-local `relatedIds` values like:

```yaml
relatedIds:
  - sac/4
```

That shape is internally resolvable only if interpreted as a tutorials-local `category/id` key. It is not a global collection-qualified identifier.

Tutorials repository setup uses category subrepositories:

```ts
createPublicationRepository({
  contentRoot: path.join(process.cwd(), 'src/content/tutorials', category),
  family: `tutorials/${category}`,
  publicBasePath: `/tutorials/${category}`,
})
```

So, for a global relationship contract, the safer identifier is:

```yaml
relatedIds:
  - tutorials/sac/4
```

## Recommendation

If `relatedIds` is intended to be a shared cross-collection field, prefer collection-qualified IDs:

- flat collection: `blog/9`, `events/17`, `whitepapers/24`
- nested tutorials category: `tutorials/sac/4`, `tutorials/dac/6`

If a family intentionally uses local IDs, document that explicitly in the family wrapper and validate it with family-specific tests.

For tutorials, numeric-only IDs are insufficient because IDs repeat across categories (`dac/1`, `sac/1`, `kac/1`, `general/1`).

## Useful verification script

```bash
python3 - <<'PY'
from pathlib import Path
import re, collections
root=Path('src/content/tutorials')
vals=[]
for p in root.glob('*/*.mdx'):
    text=p.read_text()
    m=re.search(r'^relatedIds:\n((?:  - .+\n)+)', text, re.M)
    if m:
        for line in m.group(1).splitlines():
            vals.append((str(p), line.split('-',1)[1].strip().strip('"\'')))
patterns=collections.Counter()
for _,v in vals:
    if re.fullmatch(r'\d+', v): patterns['numeric']+=1
    elif re.fullmatch(r'(dac|general|kac|sac)/\d+', v): patterns['category/id']+=1
    elif re.fullmatch(r'tutorials/(dac|general|kac|sac)/\d+', v): patterns['tutorials/category/id']+=1
    else: patterns['other']+=1
print('values', len(vals), dict(patterns))
files_by_key_locale={}
for p in root.glob('*/*.mdx'):
    cat=p.parent.name; loc=p.name.rsplit('.',2)[1]; id_=p.name.split('-',1)[0]
    files_by_key_locale[(cat,id_,loc)]=p
missing=[]
for p,v in vals:
    loc=Path(p).name.rsplit('.',2)[1]
    parts=v.split('/')
    if len(parts)==2:
        cat,id_=parts
        if (cat,id_,loc) not in files_by_key_locale:
            missing.append((p,v,loc))
    elif len(parts)==3 and parts[0]=='tutorials':
        _,cat,id_=parts
        if (cat,id_,loc) not in files_by_key_locale:
            missing.append((p,v,loc))
    else:
        missing.append((p,v,loc))
print('missing_or_unrecognized', len(missing))
for x in missing[:20]: print(x)
PY
```
