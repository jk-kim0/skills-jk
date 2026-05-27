# Route-Local Authoring Wiki Status Pattern

Use this reference when creating or refreshing the corp-web-app GitHub wiki page `Route-Local-Authoring`.

## Trigger

- User asks to write/update the corp-web-app wiki for route-local authoring status.
- User asks to summarize static marketing page coverage or route-local authoring scope.

## Key rules

- corp-web-app wiki pages are Korean by default unless explicitly requested otherwise.
- Use latest `origin/main` as the implementation source of truth.
- Keep the wiki concise and status-oriented; do not make it a full migration dashboard.
- Focus on static/semistatic marketing pages and rollout candidates.
- Exclude MDX/publication/detail families from the static-page backlog: blog, whitepapers, news, events/webinars, demo details, introduction deck, glossary, manuals, and tutorials.
- Treat `src/app/[locale]/internal/**`, API routes, search, and `src/app/[...slug]/page.tsx` fallback as excluded from route-local static-page status.

## Command sequence

From the corp-web-app repo root:

```bash
pwd
git rev-parse --show-toplevel
git status --short --branch
git fetch origin main
git pull --ff-only origin main
git rev-parse origin/main
git show -s --format='%ci%n%s' origin/main
git ls-files 'src/app/**/page.tsx' | sort
```

For wiki editing, prefer an existing local wiki clone when present:

```bash
git -C ../corp-web-app.wiki status --short --branch
git -C ../corp-web-app.wiki pull --ff-only origin master
```

If no local clone exists, clone `git@github.com:querypie/corp-web-app.wiki.git` or `https://github.com/querypie/corp-web-app.wiki.git` into a temporary isolated directory.

## Recommended page shape

1. Purpose
   - Ask what static/semistatic marketing pages are route-local, preview candidates, or scope decisions.
2. Snapshot
   - repo, latest `origin/main` SHA, commit time/title, stage URL.
3. Definition
   - `page.tsx` is thin; `page.en.tsx`, `page.ko.tsx`, `page.ja.tsx` own visible copy/composition.
4. Developer docs
   - `docs/static-page-route-local-authoring.md`
   - `docs/route-local-refactoring-for-developers.ko.md`
   - `.agents/skills/static-page-route-local-authoring/SKILL.md`
5. Status inventory
   - Public / locale route-local pages.
   - Archived static routes.
   - `/[locale]/t/*` preview / public-rollout candidates.
6. Explicit exclusions
   - MDX/publication/detail families and internal/API/fallback routes.
7. Current priorities
   - Rollout decisions, partial locale decisions, root/default route relationship, archived maintenance.
8. Short update instructions
   - Re-run route listing; classify as `route-local`, `preview / rollout candidate`, `partial / scope decision`, or `excluded`.

## Verification

Before commit/push:

```bash
git -C ../corp-web-app.wiki status --short
git -C ../corp-web-app.wiki diff -- Route-Local-Authoring.md _Sidebar.md
```

After edit:

```bash
git -C ../corp-web-app.wiki add Route-Local-Authoring.md _Sidebar.md
git -C ../corp-web-app.wiki commit -m "Add route-local authoring wiki"
git -C ../corp-web-app.wiki push origin master
git -C ../corp-web-app.wiki status --short --branch
git -C ../corp-web-app.wiki log -1 --oneline
git -C ../corp-web-app.wiki ls-remote origin refs/heads/master
```
