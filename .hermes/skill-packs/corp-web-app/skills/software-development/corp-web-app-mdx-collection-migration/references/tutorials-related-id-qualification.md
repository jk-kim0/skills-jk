# Tutorials related ID qualification

Session lesson from reviewing corp-web-app PR 639 after the tutorials migration landed.

## Issue

PR 639 migrated tutorials into category subcollections:

```text
src/content/tutorials/<category>/<id>-<slug>.{locale}.mdx
public/tutorials/<category>/<id>/...
```

The generic publication loader accepts `relatedIds` as arbitrary string arrays and does not currently resolve them. This means values like `sac/4` do not break at runtime, but they are ambiguous once related references are treated as collection identifiers.

## Correct policy

For tutorials, `relatedIds` should be collection-qualified:

```yaml
relatedIds:
  - tutorials/sac/4
  - tutorials/dac/6
```

Avoid category-only values:

```yaml
relatedIds:
  - sac/4
```

Rationale:
- Tutorial numeric IDs are only unique inside each category.
- `src/lib/repo-content/tutorials.ts` models category repositories with family identifiers like `tutorials/sac`.
- Collection-qualified references are safer for any future shared related-item resolver or cross-family related handling.

## Verification recipe

After any migration/fix, verify all tutorial related IDs are qualified and same-locale resolvable:

```bash
python3 - <<'PY'
from pathlib import Path
import re
root=Path('src/content/tutorials')
values=[]; bad=[]; missing=[]
files_by_key_locale={}
for p in root.glob('*/*.mdx'):
    cat=p.parent.name; loc=p.name.rsplit('.',2)[1]; id_=p.name.split('-',1)[0]
    files_by_key_locale[(cat,id_,loc)]=p
for p in root.glob('*/*.mdx'):
    loc=p.name.rsplit('.',2)[1]
    text=p.read_text()
    m=re.search(r'^relatedIds:\n((?:  - .+\n)+)', text, re.M)
    if not m: continue
    for line in m.group(1).splitlines():
        v=line.split('-',1)[1].strip().strip('"\'')
        values.append(v)
        mm=re.fullmatch(r'tutorials/(dac|general|kac|sac)/(\d+)', v)
        if not mm:
            bad.append((str(p),v)); continue
        if (mm.group(1), mm.group(2), loc) not in files_by_key_locale:
            missing.append((str(p),v,loc))
print('related values', len(values))
print('bad format', len(bad))
print('missing', len(missing))
PY
```

Also keep a Vitest assertion in `src/lib/repo-content/__tests__/tutorials-migration.test.ts` that enforces the same grammar and same-locale existence.
