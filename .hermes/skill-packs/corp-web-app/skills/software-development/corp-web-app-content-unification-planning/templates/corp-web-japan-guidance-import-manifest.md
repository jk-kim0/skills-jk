# corp-web-japan guidance import manifest

Use this as the tracked source-of-truth for corp-web-japan guidance, documentation, and repo-local skill imports into corp-web-app.

Purpose:
- make the imported guidance discoverable before endpoint/collection migration starts,
- make local adaptations explicit,
- make reimport checks cheap when corp-web-japan docs/skills change.

## Import batch metadata

- Import PR:
- corp-web-japan source ref/commit:
- corp-web-app target ref/commit:
- Imported by:
- Last reviewed:

## Manifest table

| Source path in corp-web-japan | Target path in corp-web-app | Last imported source commit | Disposition (`copy as-is` / `adapt` / `exclude`) | Local adaptation notes | Reimport check |
|---|---|---|---|---|---|
| `AGENTS.md` | `AGENTS.md` | `<sha>` | `adapt` | Adjust repo name, stage URL, PR language, CI/workflow assumptions. | pending |
| `docs/code-location-conventions.md` | `docs/code-location-conventions.md` | `<sha>` | `adapt` | Keep route-local/page/component principles; adapt Japan-only paths. | pending |
| `docs/static-page-route-local-authoring.md` | `docs/static-page-route-local-authoring.md` | `<sha>` | `adapt` | Preserve mandatory route-local refactoring contract. | pending |
| `docs/route-aligned-mdx-authoring-for-developers.md` | `docs/route-aligned-mdx-authoring-for-developers.md` | `<sha>` | `adapt` | Adapt locale/collection conventions for global EN/KO/JA. | pending |
| `.agents/skills/<skill>/SKILL.md` | `.agents/skills/<skill>/SKILL.md` | `<sha>` | `adapt` | Remove Japan-only route/launch assumptions. | pending |

## Fast reimport check

For each non-excluded source path, run in corp-web-japan:

```bash
git log -1 --format=%H -- <source-path>
```

If the returned SHA differs from `Last imported source commit`, inspect that path and update the corp-web-app target if the changed guidance still applies.

Recommended report format:

```text
source path: <path>
manifest sha: <sha>
latest sha: <sha>
status: unchanged | needs review | reimported | intentionally skipped
note: <why>
```

## Disposition rules

- `copy as-is`: only for repo-agnostic guidance that does not mention Japan-only URLs, launch assumptions, or language/copy policy.
- `adapt`: default for most docs and skills; preserve the workflow/pattern while translating repo names, URL policy, locale behavior, CI/Preview behavior, and release assumptions to corp-web-app.
- `exclude`: use when the source is purely Japan-only and would mislead corp-web-app work.
