# corp-web-app MDX plan/inventory refresh notes

Use this reference when the task is not migrating MDX files themselves, but refreshing planning docs and inventories against the latest `origin/main` state.

## Session-derived checks

Current pattern to verify repo-local MDX state:

```bash
python3 - <<'PY'
from pathlib import Path
from collections import Counter, defaultdict
import re, subprocess
root=Path('.')
print('HEAD', subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip())
for fam in ['blog','whitepapers','events','demo/use-cases','news','manuals','glossary','introduction-deck','privacy-policy']:
    p=root/'src/content'/fam
    files=sorted(p.glob('*.mdx')) if p.exists() else []
    c=Counter(); ids=defaultdict(set)
    for f in files:
        m=re.match(r'(.+)\.(en|ko|ja)\.mdx$', f.name)
        if m:
            loc=m.group(2); c[loc]+=1; ids[m.group(1)].add(loc)
    print(f'CONTENT {fam}: files={len(files)} items={len(ids)} locales={dict(c)}')
PY
```

Current pattern to verify `/t/*` MDX routes exist:

```bash
python3 - <<'PY'
from pathlib import Path
root=Path('.')
for pat in [
  'src/app/**/blog/**/page.tsx',
  'src/app/**/whitepapers/**/page.tsx',
  'src/app/**/events/**/page.tsx',
  'src/app/**/demo/use-cases/**/page.tsx',
]:
    matches=sorted(root.glob(pat))
    print(pat, len(matches))
    for m in matches: print(' ', m)
PY
```

## Stale-doc search checklist

After editing migration plans/inventories, grep for old assumptions:

```bash
rg -n \
  '86a3ab|first repo-local|no repo-local|white-papers collection|webinars collection|src/content/use-cases|Target collection \| `use-cases`|Phase 2 should use|Phase 2 should add|current route inventory has no|25 items|24 items have|22 items|public/webinars|^use-cases$' \
  docs --glob '*.md'
```

The important distinction is that legacy source paths may still include `discover/webinars`, but target repo-local paths should use `src/content/events/**`; demo use cases should use `src/content/demo/use-cases/**`, not `src/content/use-cases/**`.

## Rebase pitfall

If `origin/main` advances while the docs task is in progress:

1. Rebase the docs branch onto latest `origin/main`.
2. Re-run the MDX state/count script above.
3. Update any docs baseline SHA references from the pre-rebase `origin/main` to the new `git rev-parse origin/main`.
4. Amend before pushing.

This avoids publishing plan docs that claim to be based on the latest main while embedding the previous main SHA.
