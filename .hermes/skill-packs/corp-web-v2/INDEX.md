# corp-web-v2 skill pack

Use when working in corp-web-v2 or related corp-web-contents migration/parity tasks.

This pack is intentionally stored outside active `.hermes/skills/` so its detailed skill index is not injected into every Hermes request. Load this index only when the current task matches this repository area, then read the specific `SKILL.md` files needed for the task.

## Summary

- skills: 14
- skill root: `.hermes/skill-packs/corp-web-v2/skills/`
- active entrypoint: `.hermes/skills/software-development/corp-web-v2-pack/SKILL.md`

## How to use

1. Read this `INDEX.md` first.
2. Pick the smallest relevant skill set from the trigger map below.
3. Read the selected `.hermes/skill-packs/.../SKILL.md` files directly with file tools.
4. Do not copy the whole pack into the prompt unless the task truly requires broad repo archaeology.

## Trigger map

### content/MDX migration

- `corp-web-v2` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2/SKILL.md`
  - Use when working in corp-web-v2 or related corp-web-contents migration tasks; contains migrated repo-specific memory and user preferences.
- `corp-web-v2-blog-mdx-migration` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-blog-mdx-migration/SKILL.md`
  - Migrate blog or white-paper MDX content from corp-web-contents into corp-web-v2, first verifying what is already on main so you only copy missing content or fix residual migration issues, then verify with tests and PR workflow.
- `corp-web-v2-demo-acp-mdx-migration` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-demo-acp-mdx-migration/SKILL.md`
  - Migrate corp-web-v2 legacy ACP demo content to short MDX-backed /demo/acp/:id/:slug routes, including redirects, asset relocation, tests, PR, and wiki updates.
- `corp-web-v2-demo-mdx-migration-all` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-demo-mdx-migration-all/SKILL.md`
  - Migrate remaining corp-web-v2 demo categories from corp-web-contents into MDX-backed short routes, normalize per-entry assets, preserve CMS-managed list/admin flows where needed, and finish with PR + wiki updates.
- `corp-web-v2-mdx-list-pagination` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-mdx-list-pagination/SKILL.md`
  - Implement blog/white-paper MDX list page.tsx routes in corp-web-v2 using button-based server pagination with ?page=, and align demo list UX to the same pattern without converting demo to MDX.
- `corp-web-v2-mdx-one-sentence-per-line` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-mdx-one-sentence-per-line/SKILL.md`
  - Safely refactor corp-web-v2 MDX content to one sentence per line and update repo guidance without breaking JSX tags, image paths, model IDs, or markdown links.
- `corp-web-v2-stage-content-e2e-wiki-report` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-stage-content-e2e-wiki-report/SKILL.md`
  - Validate migrated corp-web-v2 content directly on stage-v2.querypie.com by content type, then publish a GitHub wiki E2E report with pass/fail findings and follow-up gaps.

### general repo context

- `corp-web-v2-page-title-sync` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-page-title-sync/SKILL.md`
  - Diagnose and fix public-page browser titles in corp-web-v2 when pages incorrectly inherit the root `CMS` title or otherwise diverge from https://www.querypie.com.

### routes/SEO/rollout

- `corp-web-v2-public-route-aligned-assets` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-public-route-aligned-assets/SKILL.md`
  - In corp-web-v2, align migrated public assets to route-shaped public paths without inventing extra path segments, and watch for Vercel output-tracing side effects when large public trees are added.

### visual/render parity

- `corp-web-v2-article-author-box` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-article-author-box/SKILL.md`
  - Implement or refine localized author profile boxes for corp-web-v2 MDX article layouts by porting author registry data and assets from corp-web-contents / corp-web-app, matching MDX frontmatter author IDs, and shipping through the existing PR branch or a fresh worktree as appropriate.
- `corp-web-v2-demo-aip-short-route` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-demo-aip-short-route/SKILL.md`
  - Shorten corp-web-v2 AIP demo URLs to /demo/aip/:id/:slug while keeping the existing managed demo rendering, adding legacy redirects, canonical metadata, tests, and PR follow-up updates.
- `corp-web-v2-port-from-corp-web-app` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-port-from-corp-web-app/SKILL.md`
  - Port an existing feature from corp-web-app into corp-web-v2 by locating the original commit(s), reproducing behavior with tests first, and delivering the change through a clean worktree PR.
- `corp-web-v2-preview-deploy-timeout` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-preview-deploy-timeout/SKILL.md`
  - Diagnose and fix Preview Deploy GitHub Actions failures in corp-web-v2 when Vercel stays BUILDING and the local polling script times out.
- `corp-web-v2-solutions-parity` — `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-solutions-parity/SKILL.md`
  - Migrate the missing QueryPie Solutions parity area into corp-web-v2 by porting legacy AIP/ACP solution families into individual static page.tsx routes, route-aligned assets, navigation links, tests, and Draft PR verification.

## Full skill list

| skill | path | description |
| --- | --- | --- |
| `corp-web-v2` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2/SKILL.md` | Use when working in corp-web-v2 or related corp-web-contents migration tasks; contains migrated repo-specific memory and user preferences. |
| `corp-web-v2-article-author-box` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-article-author-box/SKILL.md` | Implement or refine localized author profile boxes for corp-web-v2 MDX article layouts by porting author registry data and assets from corp-web-contents / corp-web-app, matching MDX frontmatter author IDs, and shipping through the existing  |
| `corp-web-v2-blog-mdx-migration` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-blog-mdx-migration/SKILL.md` | Migrate blog or white-paper MDX content from corp-web-contents into corp-web-v2, first verifying what is already on main so you only copy missing content or fix residual migration issues, then verify with tests and PR workflow. |
| `corp-web-v2-demo-acp-mdx-migration` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-demo-acp-mdx-migration/SKILL.md` | Migrate corp-web-v2 legacy ACP demo content to short MDX-backed /demo/acp/:id/:slug routes, including redirects, asset relocation, tests, PR, and wiki updates. |
| `corp-web-v2-demo-aip-short-route` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-demo-aip-short-route/SKILL.md` | Shorten corp-web-v2 AIP demo URLs to /demo/aip/:id/:slug while keeping the existing managed demo rendering, adding legacy redirects, canonical metadata, tests, and PR follow-up updates. |
| `corp-web-v2-demo-mdx-migration-all` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-demo-mdx-migration-all/SKILL.md` | Migrate remaining corp-web-v2 demo categories from corp-web-contents into MDX-backed short routes, normalize per-entry assets, preserve CMS-managed list/admin flows where needed, and finish with PR + wiki updates. |
| `corp-web-v2-mdx-list-pagination` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-mdx-list-pagination/SKILL.md` | Implement blog/white-paper MDX list page.tsx routes in corp-web-v2 using button-based server pagination with ?page=, and align demo list UX to the same pattern without converting demo to MDX. |
| `corp-web-v2-mdx-one-sentence-per-line` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-mdx-one-sentence-per-line/SKILL.md` | Safely refactor corp-web-v2 MDX content to one sentence per line and update repo guidance without breaking JSX tags, image paths, model IDs, or markdown links. |
| `corp-web-v2-page-title-sync` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-page-title-sync/SKILL.md` | Diagnose and fix public-page browser titles in corp-web-v2 when pages incorrectly inherit the root `CMS` title or otherwise diverge from https://www.querypie.com. |
| `corp-web-v2-port-from-corp-web-app` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-port-from-corp-web-app/SKILL.md` | Port an existing feature from corp-web-app into corp-web-v2 by locating the original commit(s), reproducing behavior with tests first, and delivering the change through a clean worktree PR. |
| `corp-web-v2-preview-deploy-timeout` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-preview-deploy-timeout/SKILL.md` | Diagnose and fix Preview Deploy GitHub Actions failures in corp-web-v2 when Vercel stays BUILDING and the local polling script times out. |
| `corp-web-v2-public-route-aligned-assets` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-public-route-aligned-assets/SKILL.md` | In corp-web-v2, align migrated public assets to route-shaped public paths without inventing extra path segments, and watch for Vercel output-tracing side effects when large public trees are added. |
| `corp-web-v2-solutions-parity` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-solutions-parity/SKILL.md` | Migrate the missing QueryPie Solutions parity area into corp-web-v2 by porting legacy AIP/ACP solution families into individual static page.tsx routes, route-aligned assets, navigation links, tests, and Draft PR verification. |
| `corp-web-v2-stage-content-e2e-wiki-report` | `.hermes/skill-packs/corp-web-v2/skills/software-development/corp-web-v2-stage-content-e2e-wiki-report/SKILL.md` | Validate migrated corp-web-v2 content directly on stage-v2.querypie.com by content type, then publish a GitHub wiki E2E report with pass/fail findings and follow-up gaps. |
