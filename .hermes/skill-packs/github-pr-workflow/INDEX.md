# GitHub PR workflow skill pack

Inactive detailed procedures for PR body safety, stacked rebase/body updates, merged-PR follow-up, existing-PR worktree updates, and PR validity audits.

Pack root: `.hermes/skill-packs/github-pr-workflow/`
Active entrypoint: ``.hermes/skills/github/github-pr-workflow/SKILL.md``

## How to use

1. Load the active entrypoint skill first.
2. Read this `INDEX.md`.
3. Read only the detailed `SKILL.md` files below that match the current task; do not bulk-load the whole pack.

## Detailed skills

| skill | path | when to read |
| --- | --- | --- |
| `github-pr-body-file-safety` | `.hermes/skill-packs/github-pr-workflow/skills/github/github-pr-body-file-safety/SKILL.md` | Use gh PR body files instead of inline shell strings when markdown contains backticks or shell-sensitive content. |
| `github-pr-body-file-and-stacked-rebase` | `.hermes/skill-packs/github-pr-workflow/skills/github/github-pr-body-file-and-stacked-rebase/SKILL.md` | Safely edit PR bodies with gh using body files, and rebase stacked PRs onto the latest main after upstream/base changes land. |
| `merged-pr-followup-workflow` | `.hermes/skill-packs/github-pr-workflow/skills/github/merged-pr-followup-workflow/SKILL.md` | Handle follow-up work requested against a pull request that is already merged or otherwise closed by creating a new PR from latest main instead of reviving the old branch. |
| `existing-pr-followup-worktree` | `.hermes/skill-packs/github-pr-workflow/skills/software-development/existing-pr-followup-worktree/SKILL.md` | When a user asks for follow-up changes to work already under review, use a fresh worktree on the existing PR branch and update the same PR instead of creating a new one. |
| `github-pr-validity-check` | `.hermes/skill-packs/github-pr-workflow/skills/software-development/github-pr-validity-check/SKILL.md` | Validate whether an open GitHub PR is still a clean, reviewable, merge-worthy PR against the latest base branch, especially when scope drift or stale approvals may exist. |

## Maintenance rule

- Keep detailed, situation-specific Git/GitHub workflow notes in this inactive pack rather than adding more active `.hermes/skills/**/SKILL.md` siblings.
- Prefer patching the active umbrella/entrypoint with one-line routing guidance and placing long procedures in this pack.
