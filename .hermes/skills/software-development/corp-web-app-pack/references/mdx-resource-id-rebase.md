# corp-web-app MDX resource id rebase and renumbering

Use this when rebasing a corp-web-app PR that adds or edits MDX-backed publication/resource content with numeric frontmatter ids.

## Pattern

1. Start from the exact PR the user named. Re-query it with `gh pr view <number> --json number,headRefName,baseRefName,headRefOid,url` before checking out or pushing.
2. Update local `main` from `origin/main`, then rebase the PR branch onto that latest `origin/main`.
3. After conflict resolution, scan the relevant `src/content/**` family for existing numeric `id` frontmatter values on the rebased branch.
4. Treat latest `main` as authoritative for already-assigned ids. Assign any newly introduced MDX entries to the next available ids after the current maximum in that content family.
5. If multiple locale files represent the same publication/resource entry, keep their id values aligned according to the repository's existing convention for that family.
6. Verify there are no duplicate ids in the affected family before pushing.
7. Push with `--force-with-lease`, then re-query the same PR number and verify its `headRefOid` matches the pushed branch tip and that `origin/main` is an ancestor of the PR head.

## Pitfalls

- Do not infer the active PR from the current branch or from a nearby PR number after context compaction. The requested PR number is the source of truth.
- Do not renumber against stale local main. Always fetch and use latest `origin/main` first.
- Do not only resolve textual MDX conflicts; numeric id conflicts can remain invisible until list/detail ordering or duplicate-id validation fails.
- When latest `main` has evolved the content schema while the PR is stale, keep latest-main schema fields for existing entries and reapply only the PR's scoped new content. For example, if old PR commits added or removed legacy `sourceLabel` while `main` now uses `newsType`, resolve existing content files to `main`, remove stale `sourceLabel` from new entries, and add the current required `newsType` values to the newly introduced entries.
- Do not trust a single ad hoc frontmatter scan that only handles one quoting style. Frontmatter ids may be single-quoted, double-quoted, or unquoted; validation scripts should parse all three before reporting max id or duplicates.
- A cleanup/scope-splitting commit near the end of a PR can become mostly empty after rebase but still affect newly introduced files. Before continuing or skipping, inspect the final diff for the new entries and verify required current-contract fields (`id`, `slug`, visibility fields, type fields, related ids) are still present.

## Verification snippets

Use a quote-tolerant scan for the affected family after conflict resolution:

```bash
python3 - <<'PY'
from pathlib import Path
import re, collections
root = Path('src/content/news')
rows = []
for p in root.glob('*.mdx'):
    text = p.read_text()
    id_match = re.search(r"^id:\s*[\"']?([^\"'\n]+)[\"']?", text, re.M)
    slug_match = re.search(r"^slug:\s*[\"']?([^\"'\n]+)[\"']?", text, re.M)
    type_match = re.search(r"^newsType:\s*([^\n]+)$", text, re.M)
    hidden_match = re.search(r"^hidden:\s*([^\n]+)$", text, re.M)
    if id_match:
        rows.append((id_match.group(1).strip(), p.name, slug_match.group(1).strip() if slug_match else '', type_match.group(1).strip() if type_match else '', hidden_match.group(1).strip() if hidden_match else ''))
counts = collections.Counter(row[0] for row in rows)
print('max_id', max(int(row[0]) for row in rows if row[0].isdigit()))
print('duplicate_or_unexpected_counts', {k: v for k, v in counts.items() if v not in (1, 3)})
for row in sorted(rows, key=lambda x: (int(x[0]) if x[0].isdigit() else 999999, x[1])):
    print(row)
PY
```

Also grep for stale schema fields after rebase, scoped to the affected content family and loaders, before pushing:

```bash
git grep -n "sourceLabel" -- src/content/news src/lib/resources src/app/'(tailwind)'/'[locale]'/news .agents/skills/news-posting/SKILL.md || true
```
