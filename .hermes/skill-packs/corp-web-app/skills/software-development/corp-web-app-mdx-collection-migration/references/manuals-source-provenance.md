# Manuals source provenance for corp-web-app MDX migration

Use this when reviewing or improving a corp-web-app `manuals` collection migration that was seeded from corp-web-japan.

## Key lesson

`corp-web-japan` is only an implementation/pattern source for manuals. It contains local Japanese MDX records under `src/content/manuals/**`, but it is not the complete global content source.

For corp-web-app, first audit `corp-web-contents` because it contains the global EN/KO/JA source MDX and `public/documentation/**` assets.

## Source priority

1. Current `corp-web-contents` source files when the relevant documentation/manual MDX exists on current main.
2. `corp-web-contents` git history when source files were removed from current main.
3. `corp-web-japan` only as a pattern/seed for repo-local collection shape or supplemental Japan-only wording where no richer corp-web-contents source exists.

## Proven mappings from PR 686 review

- ID 1 `acp-community-install-guide`
  - Current source: `corp-web-contents@5d426a02e86cbc55f99dcfb7e8710789898c5340:pages/features/documentation/querypie-install-guide/{en,ja,ko}/content.mdx`
  - Full EN/JA/KO article body exists. Use that body, not a shortened translation-derived copy.
  - Rewrite inline image refs from `public/documentation/install-guide-*.png` to route-aligned `public/manuals/1/install-guide-*.png`.
  - Thumbnail source: `public/documentation/docu-thumb-community-install-guide.png` -> `public/manuals/1/thumbnail.png`.
- ID 2 `acp-administrator-manual`
  - Historical source: `corp-web-contents@8d48209f493f9ad1fade6370bb6ba565547b6c2d^:pages/resources/learn/documentation/manual/{en,ja,ko}/content.mdx`
  - Old list item labels: Admin Manual / 管理者マニュアル / 관리자 매뉴얼.
  - Thumbnail source: `public/documentation/docu-thumb-admin.png` -> `public/manuals/2/thumbnail.png`.
- ID 3 `acp-user-manual`
  - Historical source: same old `manual/{en,ja,ko}/content.mdx` files.
  - Old list item labels: User Manual / ユーザーマニュアル / 사용자 매뉴얼.
  - Thumbnail source: `public/documentation/docu-thumb-user.png` -> `public/manuals/3/thumbnail.png`.
- ID 4 `acp-api-reference`
  - Historical source: `pages/resources/learn/documentation/api-docs/{en,ja,ko}/content.mdx` at `8d48209f...^`.
  - Current documentation index also still has an API Docs card.
  - Thumbnail source: `public/documentation/docu-thumb-api.png` -> `public/manuals/4/thumbnail.png`.
- ID 5 `acp-manual`
  - Current source: `pages/features/documentation/{en,ja,ko}/content.mdx` at `5d426a02...`.
  - Current cards point to `https://docs.querypie.com/{locale}`.
  - Thumbnail source: `public/documentation/docu-thumb-acp-manual.png` -> `public/manuals/5/thumbnail.png`.
- ID 6 `aip-manual`
  - Current source: `pages/features/documentation/{en,ja,ko}/content.mdx` at `5d426a02...`.
  - Current cards point to `https://aip-docs.app.querypie.com/{locale}/user-guide`.
  - EN/JA source cards use `docu-thumb-aip-manual.png`; KO source card uses `docu-thumb-ai-hub-user-manual.png`. A normalized target `public/manuals/6/thumbnail.png` is acceptable if documented.
- ID 7 `acp-release-notes`
  - Historical source: `pages/resources/learn/documentation/release-notes/{en,ja,ko}/content.mdx` at `8d48209f...^`.
  - Thumbnail source: `public/documentation/docu-thumb-notes.png` -> `public/manuals/7/thumbnail.png`.

## Useful commands

```bash
# Current install guide source
git -C ../corp-web-contents show 5d426a02e86cbc55f99dcfb7e8710789898c5340:pages/features/documentation/querypie-install-guide/en/content.mdx

# Current documentation index cards
git -C ../corp-web-contents show 5d426a02e86cbc55f99dcfb7e8710789898c5340:pages/features/documentation/en/content.mdx

# Historical removed resources/learn sources
git -C ../corp-web-contents show 8d48209f493f9ad1fade6370bb6ba565547b6c2d^:pages/resources/learn/documentation/manual/en/content.mdx
git -C ../corp-web-contents show 8d48209f493f9ad1fade6370bb6ba565547b6c2d^:pages/resources/learn/documentation/api-docs/en/content.mdx
git -C ../corp-web-contents show 8d48209f493f9ad1fade6370bb6ba565547b6c2d^:pages/resources/learn/documentation/release-notes/en/content.mdx
```

## Verification pattern

For the install guide, compare source body after only the route-aligned image rewrite:

```bash
python3 - <<'PY'
from pathlib import Path
import subprocess, re
contents='../corp-web-contents'
def body(s):
    m=re.match(r'^---\n.*?\n---\n?', s, re.S)
    return s[m.end():].strip()
def norm(s):
    return re.sub(r'\s+',' ',s.replace('public/documentation/install-guide-','public/manuals/1/install-guide-').strip())
for loc in ['en','ja','ko']:
    src=subprocess.check_output(['git','-C',contents,'show','5d426a02e86cbc55f99dcfb7e8710789898c5340:pages/features/documentation/querypie-install-guide/'+loc+'/content.mdx'], text=True)
    tgt=Path(f'src/content/manuals/1-acp-community-install-guide.{loc}.mdx').read_text()
    print(loc, norm(body(src)) == norm(body(tgt)))
PY
```
