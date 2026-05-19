# corp-web-app certifications rollout note

Session pattern: `/[locale]/t/company/certifications` was promoted to `/[locale]/company/certifications` while an older public route implementation already existed.

Useful steps captured:

1. Start from latest `origin/main` in a fresh worktree.
2. Remove/overwrite the existing public target route with the reviewed preview implementation rather than adding a wrapper or preserving the old public page.
3. Move the reviewed route-local files into the public target and remove the preview route entrypoint.
4. Update the route README from verification-route language to public-rollout language.
5. Remove the promoted page from `src/lib/internal-preview-routes.ts` and `src/lib/preview-navigation.ts` so preview navigation does not send `/company/certifications` back to `/t/company/certifications`.
6. Collapse tests to the public route test file, update imports/source path assertions to `src/app/[locale]/company/certifications`, and add an absence assertion for `src/app/[locale]/t/company/certifications/page.tsx`.
7. Verify with targeted route/preview-navigation/internal-preview-index tests, test-group assignment, `git diff --check`, and a grep for stale preview-route contracts.

Pitfall: when the public target directory already exists, `git mv` over the target after `git rm -r` can leave staged modifications and deletions that make `git diff` look small. Use `git diff HEAD --name-status` / `git diff HEAD --stat` before commit to see the true PR diff.