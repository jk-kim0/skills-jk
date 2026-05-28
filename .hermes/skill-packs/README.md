# Repo-specific skill packs

Repo-specific skills in this directory are intentionally stored outside active `.hermes/skills/` so their detailed name/description index is not injected into every default Hermes request.

Active `.hermes/skills/` keeps only thin `<repo>-pack` entrypoint skills. When a task belongs to a repository pack, read that pack's `INDEX.md` and then read only the specific detailed skill files needed for the task.

Current packs:

Repo-specific packs:

- `corp-web-japan/` — Japanese public-site and querypie.ai/querypie.jp migration/parity workflows.
- `corp-web-app/` — corp-web-app route-local, Tailwind, content, and stage E2E workflows.
- `corp-web-v2/` — corp-web-v2 and corp-web-contents migration/parity workflows.
- `querypie-docs/` — querypie-docs confluence/MDX translation workflows.

Workflow consolidation packs:

- `git-worktree-safety/` — local main/worktree/branch cleanup and stale-branch classification procedures.
- `github-pr-workflow/` — detailed PR body, stacked rebase, follow-up, and validity procedures governed by the active `github-pr-workflow` skill.

See `INVENTORY.md` for the original repo-specific split inventory and each pack's `INDEX.md` for current detailed contents.
