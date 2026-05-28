# Git/worktree safety skill pack

Inactive detailed procedures for local branch/worktree cleanup, main-checkout safety, repo-root `.worktrees/` policy, and stale-branch classification.

Pack root: `.hermes/skill-packs/git-worktree-safety/`
Active entrypoint: ``.hermes/skills/software-development/git-worktree-safety-pack/SKILL.md``

## How to use

1. Load the active entrypoint skill first.
2. Read this `INDEX.md`.
3. Read only the detailed `SKILL.md` files below that match the current task; do not bulk-load the whole pack.

## Detailed skills

| skill | path | when to read |
| --- | --- | --- |
| `main-checkout-edit-taboo` | `.hermes/skill-packs/git-worktree-safety/skills/software-development/main-checkout-edit-taboo/SKILL.md` | Mandatory safety rule for repository work: never create local file changes in a workspace checked out to main; always use a non-main worktree unless explicitly authorized. |
| `repo-root-worktree-path-policy` | `.hermes/skill-packs/git-worktree-safety/skills/software-development/repo-root-worktree-path-policy/SKILL.md` | Common worktree path policy — create linked git worktrees under the repository's own `.worktrees/<flat-name>` directory, keep names flat, and verify the checkout before editing. |
| `git-worktree-file-edit-safety` | `.hermes/skill-packs/git-worktree-safety/skills/software-development/git-worktree-file-edit-safety/SKILL.md` | Safely edit files when working in a git worktree so Hermes file-edit tools do not accidentally modify the main checkout. |
| `safe-git-worktree-branch-cleanup` | `.hermes/skill-packs/git-worktree-safety/skills/software-development/safe-git-worktree-branch-cleanup/SKILL.md` | Safely update local main and clean stale local git branches/worktrees without deleting dirty or still-attached work. |
| `workspace-stale-git-cleanup` | `.hermes/skill-packs/git-worktree-safety/skills/software-development/workspace-stale-git-cleanup/SKILL.md` | Safely clean stale git branches and worktrees across many repositories under a workspace root, using conservative rules and explicit verification. |
| `branch-squash-validity-and-stale-cleanup` | `.hermes/skill-packs/git-worktree-safety/skills/software-development/branch-squash-validity-and-stale-cleanup/SKILL.md` | Audit each local branch by synthetic squash versus latest origin/main, test rebase portability, classify meaningful local work vs stale residue, and safely delete stale branches/worktrees. |

## Maintenance rule

- Keep detailed, situation-specific Git/GitHub workflow notes in this inactive pack rather than adding more active `.hermes/skills/**/SKILL.md` siblings.
- Prefer patching the active umbrella/entrypoint with one-line routing guidance and placing long procedures in this pack.
