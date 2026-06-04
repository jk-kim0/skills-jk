# News MDX rebase, newsType, and certificate asset follow-up

Use this when rebasing or amending a `corp-web-app` PR that adds news MDX records and main has advanced with new news IDs or loader contracts.

## Durable workflow

1. Rebase onto the latest `origin/main` and verify the PR is still open before force-pushing.
2. If main added more news records, move new PR news entries to IDs after the current max ID and update all of these together:
   - `src/content/news/<id>-<slug>.{en,ko,ja}.mdx`
   - `public/news/<id>/...`
   - `relatedIds`
   - tests and PR body references
3. During conflict resolution, preserve latest-main loader/UI contracts and reapply only the PR payload. In particular, do not resurrect old `sourceLabel`-based news labels if main uses `newsType`.
4. After rebase or squash, check that every new news MDX file has the final contract fields, especially:
   - `id`
   - `slug`
   - `heroImageSrc`
   - `newsType`
   - `hidden`
   - `relatedIds`
5. If CI publication tests show `post.newsType` is `undefined` even though MDX frontmatter contains `newsType`, inspect the shared resource loader before editing content. The durable root cause can be that `ResourceRecord`/`readRecord()` fails to preserve a newly introduced frontmatter field.
6. For news detail badge failures such as expected `メディア掲載` but rendered `ニュース`, trace both pieces:
   - whether `newsType` survives frontmatter parsing into the record
   - whether the detail UI maps `newsType` to locale-specific labels and falls back only when absent
7. For certificate or article body images, keep assets route-aligned under `public/news/<id>/...` and use the final filename literally in MDX. When replacing an image after a squash, remove the old asset and old references, amend the single PR commit, force-push with lease, and update the PR body.
8. When a news article body image needs presentation constraints that markdown image syntax cannot express, use the route-supported MDX image component instead of adding ad-hoc HTML. For news detail pages this is typically `ArticleFileImage` with:
   - `filepath="public/news/<id>/<filename>"` for the route-aligned asset
   - `className="!mx-auto !w-2/3"` on the figure when the user asks for two-thirds content width
   - `imageClassName="w-full !border !border-[#e5e7eb]"` for a subtle light 1px Tailwind border on the image itself
   - localized `alt` text in each locale file
9. After any amend/force-push, do not reuse old successful CI output as current status. Reconfirm local/remote head equality, `origin/main..HEAD` commit count, clean working tree, and PR `headRefOid`/`baseRefOid`/`mergeStateStatus`/check rollup. If checks have not appeared yet immediately after the force-push, report that they are not generated yet rather than implying the previous run covers the new SHA.

## Focused verification commands

```bash
git diff --check origin/main...HEAD
git grep -n 'certificate-of-approval.png' -- src public || true
git grep -n '00053210-ICT-ENGUS-UKAS.png' -- src/content/news/24-iso-42001-certification-announcement.*.mdx
npx vitest run src/__tests__/app/[locale]/news-public-route.test.tsx src/lib/resources/__tests__/news-migration.test.ts
```

Use the exact filenames/IDs from the active task; the commands above are examples from the ISO/IEC 42001 news PR pattern.
