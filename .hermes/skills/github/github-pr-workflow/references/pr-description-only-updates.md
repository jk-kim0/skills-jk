# PR description-only updates

Use this when the user asks to update only a pull request description/body, without requesting code changes.

## Workflow

1. Inspect the current PR state and scope first:
   `gh pr view <pr> --json number,title,body,headRefName,baseRefName,state,isDraft,url,commits,files`
2. Rewrite the body from the actual commits/files and current title, not from memory or stale assumptions.
3. Prefer writing the new body to a temporary markdown file and applying it with:
   `gh pr edit <pr> --body-file <file>`
   This avoids shell quoting and newline escaping issues.
4. Verify the edit by re-reading the PR body:
   `gh pr view <pr> --json number,title,body,url`
5. Match the repository/user's PR language convention. For this user's repo-work PR descriptions, Korean is preferred unless the task explicitly asks otherwise.

## Notes

- Do not commit, push, rebase, or run code verification for a description-only edit unless the user asks for broader PR work.
- If the existing body references stale validation or outdated asset details, replace those with concise statements grounded in the current PR files/commits.
