# Stale generated skill-bundle residue during skills-jk cleanup

Pattern observed during repeated `main branch 업데이트하고, 로컬 변경사항 파악하여 PR 작성해줘` / `workspace 정리` requests.

## Symptom

After preserving or PR-ing a narrow requested payload and fast-forwarding root `main`, `git status` can reveal a very broad `.hermes/skills/**` diff, for example:

- dozens of bundled skill `SKILL.md` files modified
- `.hermes/skills/.bundled_manifest` hash churn
- support files deleted, such as a `references/*.md` file
- skill content appearing to downgrade to older versions, e.g. newer CLI guidance removed or frontmatter versions moving backward

This may appear only after root `main` is updated because the checkout was previously behind and dirty.

## Classification

Do not assume this broad diff is automatically a PR payload.

Treat it as stale generated skill-bundle residue when representative diffs show it would revert latest main skill-library content to an older bundled/runtime copy, such as:

- deleting useful reference files from latest `origin/main`
- changing skill versions or descriptions backward
- removing recently added guidance
- broad manifest churn matching regenerated bundle hashes rather than a focused authored change

## Correct handling

1. First finish the requested narrow preservation/PR work and verify the pushed branch head.
2. Fast-forward root `main` to latest `origin/main` when safe.
3. Inspect representative broad diffs before staging anything:
   ```bash
   git diff -- .hermes/skills/.bundled_manifest | sed -n '1,120p'
   git diff -- .hermes/skills/productivity/notion/SKILL.md | sed -n '1,160p'
   git diff -- .hermes/skills/creative/comfyui/references/template-integrity.md | sed -n '1,120p'
   ```
4. If the diff is stale generated residue, restore it from latest main instead of opening a PR:
   ```bash
   git restore .hermes/skills
   ```
5. Re-check root cleanliness and untracked files:
   ```bash
   git status --short --branch
   git ls-files --others --exclude-standard
   ```
6. Then remove stale merged worktrees/branches separately.

## Reporting rule

Report this as a separate fact from the PR payload:

- requested scoped config/memory files: no local payload, or PR payload if real dirt exists
- surviving authored skill guidance: PR payload, if present
- broad `.hermes/skills/**` downgrade/generated diff: restored as stale generated residue after representative diff inspection

Do not describe the restored broad generated residue as part of the PR.
