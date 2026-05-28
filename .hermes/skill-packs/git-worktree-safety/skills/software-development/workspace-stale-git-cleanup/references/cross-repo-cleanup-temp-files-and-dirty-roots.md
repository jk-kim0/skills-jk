# Cross-repo cleanup: temp files, runtime caches, and dirty roots

Session pattern from a broad `/Users/jk/workspace` cleanup:

## Safe disposable residue examples

These were safe to remove during workspace cleanup after brief inspection:

- `querypie-docs-translation-1/confluence-mdx/var/list.txt`
  - a one-line temporary page-id/title list
  - not a source MDX/content change
  - removing it allowed the root `main` checkout to become clean and fast-forward to `origin/main`
- `skills-jk/.hermes/lsp/`
  - local Hermes/LSP runtime cache
  - do not preserve as project work

## Preserve rather than delete

Do not delete files just because they are untracked if they look like substantive notes or project edits:

- `cms/comparison.txt` was an untracked 164-line working memo and was preserved.
- `deck/docs/plans/*.md` were untracked plan docs and were preserved.
- `querypie-docs` release-note/product-version edits were real content changes and were preserved.
- `skills-jk/.hermes/skills/**` edits were meaningful skill-library changes and were preserved.

## Execution lesson

After removing obvious disposable residue from a dirty root checkout, immediately re-check `git status --short --branch`. If the root becomes clean, continue the standard cleanup flow and fast-forward the default branch with `git pull --ff-only origin <default>`.

If the root still contains substantive files or modifications, leave it dirty and report the preserved paths instead of hiding them in a stash or deleting them.