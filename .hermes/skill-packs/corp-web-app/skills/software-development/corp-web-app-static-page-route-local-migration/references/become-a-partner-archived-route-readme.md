# PR 671: archived Become a Partner migration README pattern

This reference captures a reusable pattern from corp-web-app PR 671 follow-up work.

## Task shape

The migrated static page already existed on an open PR. The user requested:

- expose the page under `/{locale}/archived/become-a-parter`;
- move page-specific public images under `public/archived/become-a-partner/`;
- move the `benefits` image folder to `public/archived/become-a-partner/benefits`;
- move `public/meta-image/meta-partner.png` to `public/archived/become-a-partner/meta-partner.png`;
- add a colocated README next to `page.en.tsx` / `page.ko.tsx` documenting source provenance and migration method.

## Useful source-provenance commands

Search all historical file paths:

```bash
git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep -Ei 'partners/become|become-a-partner|become-a-parter|meta-partner|partners/benefits'
```

Inspect historical source:

```bash
git show 69bec90d:contents/pages/partners/become-a-partner/en/content.mdx
git show 69bec90d:contents/pages/partners/become-a-partner/en/meta.json
git show 69bec90d:contents/public/partners/benefits/customized-technical-and-sales-empowerment.png > /tmp/customized-technical-and-sales-empowerment.png
```

Historical commit used:

- `69bec90d` — `Mono: Merge corp-web-contents into /contents/`

## README sections that worked well

- Current route
- Current implementation files
- Original migration source
- Migration method
- Asset mapping
- Follow-up modification checklist

## Important pitfall

An initial broad replacement of `public/partners/` also changed unrelated references to `public/partners/form/done-icon.*` in shared form components. Those were not part of the page-specific migration and had to be reverted.

For future tasks, search references before moving broad folders and explicitly exclude shared subtrees unless the user requested them.

## Verification used

```bash
npm run test:run -- src/__tests__/app/partners-become-route-local.test.tsx
git ls-remote origin refs/heads/feat/partners-become-route-local
gh pr view 671 --json number,state,headRefOid,mergeStateStatus,statusCheckRollup,url
```
