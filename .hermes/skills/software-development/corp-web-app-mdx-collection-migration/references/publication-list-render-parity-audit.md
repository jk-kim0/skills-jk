# Publication list render-parity audit notes

Use this when a corp-web-app MDX/publication collection has repo-local content and `/t/<locale>/...` routes, but the user asks whether the migrated page visually/functionally matches an existing reference list page.

## Session-derived example

Compared pages:
- Target: `https://stage.querypie.com/t/ja/blog`
- Reference: `https://stage.querypie.ai/blog`
- Scope: page body only; GNB/footer explicitly excluded.

Finding:
- The target was not a finished blog feature page. It was a raw repo-local verification route: localized MDX records loaded, but the route rendered a plain H1, developer verification sentence, and text-only `<ul>`.
- The reference rendered a production resource-list UX: localized hero, category sidebar/drawer, 2-column desktop card grid, mobile cards, thumbnails, badge, dates, and Load More.
- When the user confirmed that corresponding GNB menu/link targets already exist, the resource category-set question was no longer open: adopt the reference category set (`全て`, `紹介資料`, `用語集`, `マニュアル`, `ホワイトペーパー`, `ブログ`) for the page-body resource navigation, constrained to existing/intended verification routes.
- When the user accepted `stage.querypie.ai/blog` as the corpus source of truth, the migration plan had to move from documentation-only diagnosis to corpus parity work: copy missing JA blog records and assets from corp-web-japan, preserve hidden redirect records (for example IDs that should not appear in the list), and update inventory/tests accordingly.

## Audit sequence

1. Browser-render both URLs.
   - Capture desktop and mobile viewport observations.
   - If the user excludes GNB/footer, inspect only the body sections between them.
   - Record major landmarks: hero, category nav, cards/list, progressive controls.

2. Inspect target route source.
   - Read `src/app/t/[locale]/<family>/page.tsx`.
   - Identify whether it is a production list shell or only a verification list.
   - Check for developer-facing copy such as `Repo-local verification route...` leaking into visible UI.

3. Inspect loader/list item contract.
   - Verify whether records expose fields needed by the reference UI: `id`, `slug`, `title`, `description`, `date`, `heroImageSrc`, and href.
   - Note display-only gaps such as localized badge/category label or date formatting.

4. Inspect corpus parity separately from layout parity.
   - Count target MDX records by locale.
   - Compare visible/reference IDs, especially top-of-list items.
   - Document missing IDs/locales separately from visual shell gaps.
   - If corp-web-japan becomes the accepted reference corpus, copy records/assets from that repo and preserve source list-visibility semantics such as `hidden` and `redirectUrl`; hidden redirect records can count toward corpus parity but should not be expected in the visible list.

5. Inspect assets.
   - Verify `heroImageSrc` values point to existing files under `public/**`.
   - Note naming differences such as `b-thumb-<id>.png` vs `thumbnail.png`; decide whether to normalize or map.

6. Write the plan as a feature-migration completion plan, not a styling-only fix.
   - Include what is currently migrated: content, loader, verification route.
   - Include what is not migrated: production shell, resource nav, card UI, responsive behavior, load-more, metadata, tests, corpus/assets.
   - Include an implementation checklist and PR split.
   - When user feedback resolves a decision (for example, matching resource categories are already represented in GNB links), update the plan from "open decision" to "decision accepted" and reflect it in checklist/implementation steps.

## Useful corpus count snippet

```bash
python3 - <<'PY'
from pathlib import Path
from collections import Counter, defaultdict
import re
root=Path('src/content/blog')
by_locale=Counter(); ids=defaultdict(list)
for p in root.glob('*.mdx'):
    m=re.search(r'\.(en|ko|ja)\.mdx$', p.name)
    if not m:
        continue
    loc=m.group(1); by_locale[loc]+=1
    text=p.read_text(encoding='utf-8')[:1000]
    mid=re.search(r'^id:\s*["\']?([^"\'\n]+)', text, re.M)
    if mid:
        ids[mid.group(1).strip()].append(loc)
print('counts by locale', dict(by_locale))
print('unique IDs', len(ids), sorted(ids, key=lambda x:int(x) if x.isdigit() else 999))
print('missing JA', [i for i,locs in sorted(ids.items(), key=lambda kv:int(kv[0]) if kv[0].isdigit() else 999) if 'ja' not in locs])
PY
```

## Done criteria for a render-parity migration plan

- Browser evidence from both pages, including mobile.
- Source evidence from the target route and loader.
- Corpus/locale gap separated from UI/layout gap.
- GNB/footer explicitly included or excluded according to user scope.
- Concrete implementation phases and tests, not only a list of visual differences.
