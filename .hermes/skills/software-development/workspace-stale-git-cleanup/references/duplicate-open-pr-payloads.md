# Repeated cleanup: duplicate open PR payloads

Use this note when repeated repo-local cleanup creates or discovers more than one cleanup/follow-up branch with the same payload.

## Detection

Before creating a fresh PR for cleanup notes or local sweep residue, compare the candidate branch against existing open PR branches:

```bash
env -u GITHUB_TOKEN gh pr list --state open --json number,headRefName,url,title
git diff --name-status <existing-open-pr-branch>..<candidate-branch>
```

If the branch-to-branch diff is empty, the payload is identical even if the branch names and PR titles differ.

## Handling

- Do not dispatch another PR creation workflow if an open bot-authored PR already carries the same tree.
- If duplicate open PRs already exist, do not close either PR during cleanup unless the user explicitly asks to close one.
- Preserve the open-PR worktrees/branches and report the duplicate plainly.
- Only delete a duplicate branch/worktree automatically when it has no PR metadata and its tree is identical to the kept branch.
