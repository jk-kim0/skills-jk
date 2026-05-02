---
name: corp-web-japan-sibling-source-parity-tests
description: Add or maintain corp-web-japan tests that compare local content against sibling corp-web-contents source data without breaking CI environments where the sibling repo is absent.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, tests, ci, content-migration, parity, sibling-repo]
---

# corp-web-japan sibling source parity tests

Use this when adding regression tests that compare local `corp-web-japan` content against source data stored in the sibling checkout `../corp-web-contents`.

## Why this skill exists

A local machine may have both repos checked out side-by-side, but GitHub Actions for `corp-web-japan` only checks out the current repo. A parity test that unconditionally reads `../corp-web-contents/...` will pass locally and fail in CI with `ENOENT`.

This happened with news source parity coverage after moving tests under `tests/news/`.

## When to use

Use this pattern when:
- validating migrated local content against `../corp-web-contents`
- checking item count/title order/frontmatter parity against a sibling repo
- writing tests that are valuable locally but cannot assume the sibling repo exists in CI

## Safe pattern

### 1. Compute the sibling source path from `process.cwd()`
For tests run from repo root, prefer an explicit path such as:

```js
const sourcePath = path.join(
  process.cwd(),
  '../../../corp-web-contents/pages/company/news/ja/content.mdx',
);
```

Adjust the `..` depth based on the test file location if you are using `import.meta.url`; or avoid that complexity by resolving from `process.cwd()` as above.

### 2. Check existence first

```js
import { existsSync, readFileSync } from 'node:fs';

const sourceExists = existsSync(sourcePath);
```

### 3. Skip only the sibling-dependent assertion
Do not skip the whole file if some assertions can still run in CI.

Good pattern:

```js
test(
  'local news corpus includes every source news item in the same visible order',
  { skip: !sourceExists },
  () => {
    const sourceItems = parseSourceItems();
    const localItems = readLocalItems();
    assert.equal(localItems.length, sourceItems.length);
    assert.deepEqual(
      localItems.map((item) => item.title),
      sourceItems.map((item) => item.title),
    );
  },
);

test('local news corpus keeps one MDX file per source item with non-empty metadata', () => {
  const localItems = readLocalItems();
  for (const item of localItems) {
    assert.ok(item.id);
    assert.ok(item.title);
    assert.ok(item.date);
  }
});
```

This preserves CI value while allowing stronger local parity checks.

## Recommended assertions

For sibling-source parity tests, split assertions into two groups:

1. **Sibling-dependent parity checks**
- source count == local count
- visible order matches
- title/slug/date parity

2. **Repo-local invariant checks**
- every local MDX file has required frontmatter
- expected asset paths exist
- canonical route shape remains correct

Only group 1 should be conditional on sibling source existence.

## Good fit example

For news migration work in `corp-web-japan`:
- put source-parity checks under `tests/news/source-parity.test.mjs`
- compare against `corp-web-contents/pages/company/news/ja/content.mdx`
- skip the source-order comparison in CI if the sibling repo is absent
- keep local metadata sanity checks active everywhere

## Pitfalls

- Unconditionally reading `../corp-web-contents/...` in CI
- Skipping the entire test file when only one assertion needs the sibling repo
- Resolving paths relative to a local worktree layout that differs from CI
- Moving tests into subdirectories without updating relative path assumptions

## Done criteria

- Local parity assertions run when the sibling repo exists
- CI does not fail just because `corp-web-contents` is not checked out
- Repo-local content invariants still run in CI
