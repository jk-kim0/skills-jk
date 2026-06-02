# PR body shell quoting safety

Use this reference when creating or editing GitHub PR bodies with `gh pr create` or `gh pr edit`, especially when the body contains Markdown code spans, GitHub expressions like `${{ ... }}`, shell snippets, `$`, backticks, parentheses, angle brackets, or multiline prose.

Do not pass Markdown containing backticks or `$()` through a shell double-quoted `--body "..."` argument.
The shell can execute command substitutions or expand expressions before `gh` receives the body.
`gh pr create` may still succeed, leaving a corrupted PR body and noisy local errors.

## Preferred pattern

1. Write the PR body to a temporary Markdown file using a file tool or safely quoted heredoc.
2. Create or update the PR with `--body-file`.
3. Verify the stored body with `gh pr view <pr> --json body,url,title` when the body contained shell metacharacters.
4. Remove the temporary body file after verification if it was created inside the worktree.

## Example

```bash
mkdir -p .hermes/tmp
python3 - <<'PY'
from pathlib import Path
Path('.hermes/tmp/pr-body.md').write_text('''## 요약
- Markdown/code snippets are safe here.
- Backticks like `chat.delete` are preserved.
''')
PY

gh pr create \
  --base main \
  --head <branch> \
  --title "<title>" \
  --body-file .hermes/tmp/pr-body.md
```

If an inline `--body` attempt already corrupted the PR body, repair it immediately:

```bash
gh pr edit <pr-number> --body-file .hermes/tmp/pr-body.md
gh pr view <pr-number> --json title,body,url
rm -f .hermes/tmp/pr-body.md
rmdir .hermes/tmp 2>/dev/null || true
```

Use this especially for workflow/action PRs, where the body often includes backticks, `${{ ... }}` expressions, and paths under `.github/`.
