# Next.js App Router Page-Type Classification Reference

## Common patterns in this user's repos

| Kind | Route shape | File traits | Examples |
|------|-------------|-------------|----------|
| **Static marketing page** | Flat `page.tsx`, no params | Direct JSX composition, imports section components, locale-specific `page.en.tsx` siblings | `/about-us`, `/solutions/ai-dashi`, `/contact-us` |
| **MDX publication list** | Flat `page.tsx` with loader | Calls a content loader, renders a grid/list of cards, may paginate | `/blog`, `/whitepapers`, `/news`, `/events`, `/demo/use-cases`, `/glossary`, `/introduction-deck`, `/tutorials` |
| **MDX publication detail** | Parametric `[id]/[slug]/page.tsx` | Loads MDX by id, canonicalizes slug, may gate/redirect | `/blog/[id]/[slug]`, `/whitepapers/[id]/[slug]`, `/demo/use-cases/[id]/[slug]` |
| **CMS / dynamic page** | Catch-all or remote-data page | Fetches from CMS, renders Tiptap/HTML, uses `DynamicPage` | `/features/demo/[slug]`, `/features/documentation/[...slug]` |
| **Legal / policy page** | Flat or `[slug]` parametric | Renders route-local MDX or static copy, versioned by slug | `/privacy-policy`, `/privacy-policy/[slug]`, `/terms-of-service` |

## How to disambiguate when the user says "static page"

In this user's context, "static page" almost always means **static marketing page** (thin `page.tsx` with direct JSX, not a content loader). If unsure, ask: "정적 마케팅 페이지(static marketing page)를 찾으시는 건가요, 아니면 `/t/*` 아래의 전체 페이지 구조를 보여드릴까요?"

Do **not** return every `page.tsx` under a prefix without classification. The user has explicitly reacted negatively when given a raw list that mixed MDX resource pages with static marketing pages.

## Finding archived / deleted routes

When a user asks for "archived" pages, they usually mean routes that existed in git history but are gone from the current filesystem.

```bash
# List all historical page.tsx paths under a prefix, then diff with current filesystem
git log --all --name-only --pretty=format: -- src/app/\[locale\]/t/ |
  sed '/^$/d' | sort -u | grep 'page.tsx' > /tmp/historical.txt

find src/app/\[locale\]/t -type f -name 'page.tsx' | sort > /tmp/current.txt

# Deleted routes (in history but not on disk)
comm -23 /tmp/historical.txt /tmp/current.txt
```

Typical deleted routes in this codebase: `/t/manuals/page.tsx`, `/t/manuals/[id]/[slug]/page.tsx`.
