# Author profile image validation pattern

Use when investigating broken author/profile images on corp-web-app publication pages, especially MDX-backed resources such as blog, whitepapers, news, events, and demos.

## What to check

1. Inspect the target MDX frontmatter for `author`.
   - Example path shape: `src/content/whitepapers/<id>-<slug>.{locale}.mdx`.
   - `author` may be a string or list of ids.
2. Resolve the author id through the repo-local author data:
   - `src/utils/author/author-data.ts`
   - `src/utils/author/author.ts`
   - `src/content/authors/en.yaml`
   - `src/content/authors/ko.yaml`
   - `src/content/authors/ja.yaml`
3. Check whether every resolved `profileImage` points at a real file under `public/`.
   - Current corp-web-app convention mirrors corp-web-japan: YAML stores `crew/<name>.png`, the normalized public URL is `/crew/<name>.png`, and the file lives at `public/crew/<name>.png`.
   - Legacy values may still include a `public/` prefix or older `querypie-company/crew/*` path; normalize deliberately before concluding the asset is missing.
4. If the page is deployed, verify both the raw public URL and Next image optimizer URL.
   - Raw: `https://<host>/crew/kenny.png`
   - Optimized: `https://<host>/_next/image?url=%2Fcrew%2Fkenny.png&w=256&q=75`

## Corp-web-japan comparison and migration pattern

corp-web-japan stores author data in content YAML and validates profile-image assets explicitly:

- Author data: `src/content/authors/ja.yaml`
- Resolver: `src/lib/authors/resolve-authors.ts`
- Image convention: `profileImage: crew/kenny.png`
- Served URL: `/crew/kenny.png`
- File location: `public/crew/kenny.png`
- Guard test: `tests/author-profile-image-paths.test.mjs`

corp-web-app has been aligned to the same content/asset convention:

- Author data: `src/content/authors/{en,ko,ja}.yaml`
- Resolver/normalizer: `src/utils/author/author-data.ts` and `src/utils/author/author.ts`
- Image convention: `profileImage: crew/kenny.png`
- Served URL: `/crew/kenny.png`
- File location: `public/crew/kenny.png`

Migration lesson: when moving from locale JSON to YAML, update both the data source and every renderer/loader that consumed the old shape. In corp-web-app that included resource detail author boxes and legacy article author components, not only the primary resource page loader. Keep locale-specific author lookup, and if the implementation supports fallback, verify missing locale records fall back to EN intentionally rather than silently rendering empty author metadata.

## Failure mode observed

A profile image can be broken even when the author id is registered correctly. The durable bug class is: author record exists, but `profileImage` points to a missing public asset or a stale path convention.

For example, a stage page rendered Kenny with an older `/querypie-company/crew/kenny.png`-style path while the desired cross-repo convention was `crew/kenny.png` -> `/crew/kenny.png` -> `public/crew/kenny.png`. Fix the source author data and asset placement together; do not paper over the symptom in a single component.

## Recommended hardening

If author data or author rendering is part of the task, add or run validation similar to corp-web-japan's `tests/author-profile-image-paths.test.mjs`:

- keep behavior tests and asset-existence tests separate;
- keep `src/utils/author/__tests__/author.test.ts` focused on `composeAuthors` behavior: localized lookup, fallback, unknown author handling, and normalized `profileImageSrc`;
- add a dedicated filesystem guard such as `src/utils/author/__tests__/author-profile-image-paths.test.ts`;
- read `profileImage: crew/...` directly from every author YAML file (`src/content/authors/en.yaml`, `ko.yaml`, `ja.yaml`), rather than depending on runtime loader behavior;
- assert every referenced `crew/<filename>` exists at `public/crew/<filename>`;
- when the repo convention is flat `public/crew/<filename>`, also assert the old nested location `public/crew/authors/<filename>` is absent so regressions do not silently reintroduce the wrong placement;
- include locale coverage for `en`, `ko`, and `ja` where corp-web-app uses locale-specific YAML;
- if the task touches MDX author usage, also flag author ids used in MDX but missing from one or more locale YAML files;
- run the focused Vitest files and `node scripts/ci/assert-test-groups.mjs` so the new test is covered by the repository's CI grouping.

Do not conclude that a broken image is a Next.js image optimizer issue until the raw public asset URL has been checked.