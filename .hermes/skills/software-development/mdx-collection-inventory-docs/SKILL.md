---
name: mdx-collection-inventory-docs
description: Document the current state of MDX-backed content collections in a web repository, including routes, source roots, public assets, loaders, frontmatter support, and legal-page exceptions.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [mdx, documentation, content-inventory, frontmatter, nextjs]
---

# MDX collection inventory documentation

Use this skill when the user asks for a documentation PR that summarizes MDX-backed collections or content families rather than adding/editing individual MDX posts.

## Output contract

Create a repo documentation page, usually under `docs/`, that includes:

1. A main public collection inventory table.
2. Collection name and item count.
3. Endpoint shape: list route, detail route, ID-only redirect route, and any special routes such as PDF/download routes.
4. MDX source root under `src/content/**` or route-adjacent MDX path.
5. Public image/asset root under `public/**`.
6. Loader, records, or route source files that make the collection work.
7. A shared/common frontmatter field set.
8. A per-collection frontmatter support matrix showing functional support, not merely fields observed in current files.
9. A separate legal-pages section when legal pages use a different renderer or route-owned composition.

## Workflow

1. Start from latest `origin/main` in a fresh non-main worktree.
2. Read repo guidance first (`README.md`, `AGENTS.md`, and any repo-local skills index).
3. Inspect actual code and files, not just memory or existing docs:
   - `find src/content -name '*.mdx'`
   - App Router paths under `src/app/**/page.tsx` and route handlers.
   - loader/records modules under `src/lib/**`.
   - public asset directories under `public/**`.
4. Count MDX files by family from the filesystem.
5. Read each family loader/records module to determine supported frontmatter fields.
6. Separate code-supported fields from merely observed frontmatter keys in current MDX files.
7. Document family boundaries explicitly, for example:
   - standard publication families with shared hidden/redirect behavior,
   - gated publication families such as whitepapers,
   - resource publication families with explicit `relatedItems`,
   - legal MDX pages with separate renderers.
8. Keep legal pages out of the main collection inventory unless the user explicitly asks to mix them in.
9. Verify with `git diff --check` and at least one lightweight sanity check that required sections and important collection counts are present.
10. Commit, push, open PR, and verify remote branch SHA plus PR head SHA.

## Frontmatter investigation checklist

For each collection, identify:

- Required common fields such as `id`, `slug`, `title`, `description`, `heroImageSrc`.
- Date behavior: required, optional, formatted, or event-specific effective date.
- Author support and whether it resolves through an author registry.
- Related item support: same-family `relatedIds` versus explicit `relatedItems` objects.
- Visibility/redirect support: `hidden` and `redirectUrl`.
- Gating support: `gated`, `<GatingCut />`, and download CTA behavior.
- Detail rendering flags such as `hideHeroImageOnDetail` or `hideTocOnDetail`.
- Collection-specific fields such as event labels, source labels, list descriptions, or download cover images.

## Verification guidance

Prefer lightweight verification for docs-only inventory PRs:

```bash
git diff --check -- docs/<inventory-doc>.md
python3 - <<'PY'
from pathlib import Path
s = Path('docs/<inventory-doc>.md').read_text()
for needle in ['Public MDX collection inventory', 'Frontmatter', 'Legal']:
    assert needle in s
print('doc sanity ok')
PY
```

Do not start a local dev server for documentation-only inventory work unless the user explicitly asks.

## Pitfalls

- Do not rely only on existing skills or README summaries; inventory docs must reflect latest code.
- Do not infer frontmatter support only from current MDX files. Read the normalizer/loader code.
- Do not merge legal pages into ordinary publication/resource collection tables when they use separate legal renderers.
- Do not call a field unsupported merely because current content does not use it; check the loader.
- For repo-internal docs/PR text in corp-web-japan, use English.
- For docs-only PRs, CI may still attach required scope/deploy checks; verify PR status after creation instead of assuming no checks.

## References

- `references/corp-web-japan-mdx-collection-inventory.md` captures a concrete corp-web-japan inventory pass from 2026-05 for route families, loader families, and frontmatter categories.