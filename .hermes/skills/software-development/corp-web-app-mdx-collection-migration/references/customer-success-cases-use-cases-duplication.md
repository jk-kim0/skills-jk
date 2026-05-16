# Customer success cases vs demo use-cases duplication

Session-derived review notes from corp-web-app PR 685.

## Finding

The first five legacy customer-success case records are duplicated in `corp-web-contents` under two source path families:

```text
page-archives/customers/customer-success-cases/<id>/<slug>/<locale>/content.mdx
pages/features/demo/use-cases/<id>/<slug>/<locale>/content.mdx
```

For IDs 1-5, the slug set is:

```text
1-allganize-changsu-lee
2-lovo-ai-tom-lee
3-air-company-mori-takeshi
4-superb-ai-hyun-kim
5-lg-uplus-daniel-ku
```

These should not automatically become a separate repo-local `customer-success-cases` MDX collection if the existing target already has demo/use-cases migrated.

## corp-web-japan precedent

corp-web-japan absorbed these records into the use-case publication family:

```text
src/content/use-cases/1-allganize-changsu-lee.mdx
src/content/use-cases/2-lovo-ai-tom-lee.mdx
src/content/use-cases/3-air-company-mori-takeshi.mdx
src/content/use-cases/4-superb-ai-hyun-kim.mdx
src/content/use-cases/5-lg-uplus-daniel-ku.mdx
```

Repo-local contract there:

```text
Content root: src/content/use-cases/*.mdx
Canonical detail route: /use-cases/:id/:slug
List route: /demo/use-cases
Asset root: public/use-cases/<id>/...
```

## corp-web-app review rule

Before approving or continuing a migration that adds `src/content/customer-success-cases/**`, check whether the same IDs/slugs already exist under:

```text
src/content/demo/use-cases/<id>-<slug>.<locale>.mdx
public/demo/use-cases/<id>/...
```

If present, treat a new `customer-success-cases` collection as likely duplicate data migration unless there is an explicit product/route requirement for a separate customer-success collection.

## Useful checks

List duplicate source roots in corp-web-contents:

```bash
git -C ../corp-web-contents ls-files \
  'page-archives/customers/customer-success-cases/*/*/*/content.mdx' \
  'pages/features/demo/use-cases/*/*/*/content.mdx' \
  | grep -E '(allganize-changsu-lee|lovo-ai-tom-lee|air-company-mori-takeshi|superb-ai-hyun-kim|lg-uplus-daniel-ku)'
```

Check whether corp-web-app already has the five records in demo/use-cases:

```bash
git ls-tree -r --name-only origin/main -- src/content/demo/use-cases \
  | grep -E '(allganize-changsu-lee|lovo-ai-tom-lee|air-company-mori-takeshi|superb-ai-hyun-kim|lg-uplus-daniel-ku)'
```

Compare a proposed `customer-success-cases` PR against existing demo/use-cases by slug and locale. Whitespace-only and `<br />` formatting differences should not be mistaken for distinct content.

## Recommendation

For corp-web-app, the route-aligned demo/use-cases target should remain the default for these five records. A separate `customer-success-cases` collection should require an explicit decision that the product needs separate public routes, list behavior, metadata ownership, and asset roots for that family.
