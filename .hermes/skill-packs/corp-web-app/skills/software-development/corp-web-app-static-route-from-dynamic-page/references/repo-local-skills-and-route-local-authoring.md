# corp-web-app repo-local skills and route-local authoring correction

Session learning:
- A user requested footer route-local refactoring after PR 657.
- The incorrect implementation only converted `src/components/layout/footer/data/{en,ja,ko}.json` into `src/components/layout/footer.{en,ja,ko}.tsx` object literals typed with `FooterType`.
- The user corrected this: route-local refactoring means no JSON/data-registry style; locale TSX files should own authored JSX/composition.

Repo-local skill discovery:
- `corp-web-app` contains repo-local skills under `.agents/skills/`.
- Relevant skill: `.agents/skills/static-page-route-local-authoring/SKILL.md`.
- At the time of this session, `AGENTS.md` was absent in the repo/worktree, so Hermes did not automatically receive a directive to read `.agents/skills/`.
- Future corp-web-app route-local/static/semistatic work should explicitly read `.agents/skills/README.md` and the relevant skill file before coding.

Practical guardrail:
- If the requested output path is named like `footer.en.tsx`, `footer.ja.tsx`, `footer.ko.tsx`, do not assume that means "TS object instead of JSON." For this user, it usually means locale-specific TSX authoring with visible JSX/markup/composition.
- Search for existing object-array renderers and decide whether to replace them with JSX primitives/components, not just change the file extension.
