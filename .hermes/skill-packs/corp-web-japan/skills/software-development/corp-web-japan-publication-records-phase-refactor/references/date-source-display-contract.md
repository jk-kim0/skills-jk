# Date source/display contract (2026-05 session)

Context: the repo had many MDX frontmatter dates stored as Japanese display strings, e.g. `date: "2024年11月22日"`, while newer event/resource records were already ISO `YYYY-MM-DD`.

## Contract to preserve

- MDX frontmatter source data uses ISO calendar dates:
  - `date: "YYYY-MM-DD"`
  - `eventDate: "YYYY-MM-DD"`
  - legal route-adjacent MDX may also use `effectiveDate: "YYYY-MM-DD"`.
- Public publication/resource UI should render source dates as Japanese display strings, e.g. `2024年11月22日`.
- Legal pages are an exception for visible body labels: keep effective-date body text ISO, e.g. `**Effective from 2025-07-17**`.

## Loader surfaces that need date formatting

When source dates are normalized to ISO, verify all web-visible date paths, not just detail pages:

- standard publication list items from `create-standard-records-repository.ts`
- standard publication details and related items from `create-standard-publication-post-loader.ts`
- gated whitepaper details and related items from `create-gated-publication-post-loader.ts`
- resource publication list items from `base-resource-publication.ts`
- resource detail and related items from `base-resource-publication-post-loader.ts`
- custom list item builders such as `news/records.ts`
- event-specific list/detail logic already uses `formatJapaneseDateFromIsoDate` and `eventDate` handling.

## Verification pattern

Add/maintain a source-level test like `tests/src/lib/publications/date-formatting.test.mjs` that:

1. walks `src/content/**/*.mdx` and route-adjacent `src/app/**/*.mdx`
2. inspects frontmatter only
3. fails if `date`, `eventDate`, or `effectiveDate` contains `YYYY年M月D日`
4. asserts loader source code routes ISO dates through `formatJapaneseDateFromIsoDate`
5. asserts legal visible effective-date labels remain ISO.

Run with the affected publication architecture/legal tests and `node scripts/ci/assert-test-groups.mjs`.

## Repo-local skill alignment

If a repo-local `.agents/skills/*/SKILL.md` still instructs agents to convert source `YYYY-MM-DD` into Japanese date strings, patch it in the same PR. Otherwise future migration/posting work will reintroduce non-ISO frontmatter.
