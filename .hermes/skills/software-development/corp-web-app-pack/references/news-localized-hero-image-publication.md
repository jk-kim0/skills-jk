# News localized hero image publication pattern

Use when a corp-web-app news MDX task provides language-specific launch/press images from a draft workspace and asks for EN/KO/JA news documents to use them as hero images.

## Pattern

1. Load the repo-local publication skills first:
   - `.agents/skills/mdx-publication-operations/SKILL.md`
   - `.agents/skills/news-posting/SKILL.md`
2. Work on the active news PR branch/worktree when the task is a follow-up to an existing PR; verify the PR is still open/mergeable before committing.
3. Locate draft assets under the requested draft folder. If the named folder is not present, check the nearest matching `docs/draft-*-<topic>/` folder before asking; in one Lingo session the user cited `docs/draft-250624-lingo/` but the repo contained `docs/draft-260604-lingo/`.
4. Prefer route-aligned public assets for publication hero images:
   - source draft images: `docs/draft-*/assets/open-graph/lingo-og-{en,ko,ja}.png`
   - destination: `public/news/<id>/hero-{en,ko,ja}.png`
5. Set each localized MDX frontmatter to the matching public URL:
   - EN: `heroImageSrc: /news/<id>/hero-en.png`
   - KO: `heroImageSrc: /news/<id>/hero-ko.png`
   - JA: `heroImageSrc: /news/<id>/hero-ja.png`
6. If an earlier placeholder thumbnail was created only for the draft PR, remove it when replacing with approved language-specific assets.
7. When only one locale exists but the user asks for English, Korean, and Japanese documents, add the missing localized MDX files with the same `id`, `slug`, `date`, `newsType`, `hidden`, `redirectUrl`, `gated`, and `noindex` contract. Keep `hidden: false` when the item should appear in lists.

## Lightweight verification

Run file-level checks instead of a local dev server unless explicitly requested:

```bash
file public/news/<id>/hero-*.png
python3 - <<'PY'
from pathlib import Path
id = '26'
expected = {'en': f'/news/{id}/hero-en.png', 'ko': f'/news/{id}/hero-ko.png', 'ja': f'/news/{id}/hero-ja.png'}
for loc, hero in expected.items():
    p = Path(f'src/content/news/{id}-<slug>.{loc}.mdx')
    assert p.exists(), p
    s = p.read_text()
    assert f'heroImageSrc: {hero}' in s, (loc, hero)
    assert 'hidden: false' in s, loc
    assert 'newsType: press-release' in s, loc
    assert Path('public' + hero).exists(), hero
print('localized-news-hero-frontmatter-ok')
PY
```

Remember that `heroImageSrc` is a public URL path (`/news/...`), so local existence checks must prefix it with `public`.