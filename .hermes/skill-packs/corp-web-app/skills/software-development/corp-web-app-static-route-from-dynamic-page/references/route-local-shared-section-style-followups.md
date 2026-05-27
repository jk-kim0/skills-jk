# Route-local shared section style follow-ups

Use this reference when a user asks for small visual/layout follow-ups on a corp-web-app route-local static or preview page after a PR is already open.

## Pattern from certifications preview route

Context:
- Target route: `src/app/[locale]/t/company/certifications/**`
- The page had been refactored to use shared section primitives similar to corp-web-japan:
  - `src/components/sections/company/page-primitives.component.tsx`
  - `src/components/sections/company/page-primitives.module.css`
  - `src/components/sections/certifications/section.component.tsx`
- User requested visual changes to the intro block containing the route title and lead copy.

Working approach:
1. Treat requests such as “make this area left aligned”, “move this block up 30px”, or “add spacing below it” as component-style follow-ups when the user explicitly says to change the common component style.
2. Do not add route-local one-off classes or inline styles to `page.{locale}.tsx` when the common section primitive owns the layout.
3. Patch the shared CSS module for the primitive, for example:
   ```css
   .intro {
     text-align: left;
     transform: translateY(-30px);
     margin: 0 auto 30px;
   }
   ```
4. Add or update a lightweight source-level test that reads the CSS module and asserts the shared style contract, rather than relying only on rendered text assertions.
5. Keep locale page files focused on content/composition and avoid adding visual overrides there.

## PR follow-up workflow

- First verify the PR is still open and the branch/worktree is clean.
- Commit the follow-up as a small separate commit on the existing PR branch.
- If `origin/main` advanced, rebase the PR branch onto latest `origin/main` before pushing.
- After a rebase, use `git push --force-with-lease` for the PR branch; a plain push can be rejected as non-fast-forward.
- Verify the PR head SHA after push with `gh pr view` and/or `git ls-remote`.

## Pitfall

A CSS transform (`translateY(-30px)`) changes visual position but not layout flow by itself. If the user asks both to move a block upward and add space below it, pair the transform with an explicit bottom margin or equivalent spacing on the shared primitive.
