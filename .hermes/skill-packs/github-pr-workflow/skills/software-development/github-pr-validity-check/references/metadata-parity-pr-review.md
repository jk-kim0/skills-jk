# Metadata parity PR review notes

Use this when reviewing a PR that claims to fix stage-vs-production page title, description, Open Graph, or small route-local content drift.

## Checklist

1. Verify PR state first.
   - `gh pr view <n> --json headRefName,headRefOid,mergeStateStatus,statusCheckRollup,body`
   - `gh pr diff <n> --name-only`
   - Fetch latest `origin/main` and compare PR head against it.

2. Compare three sources separately.
   - live production URL rendered metadata (`document.title`, `meta[property="og:title"]`, description)
   - current stage URL rendered metadata
   - latest `origin/main` source and PR head source

3. Treat exact strings as contracts.
   - Punctuation/separators matter for parity.
   - Example: production `QueryPie AI: 認証` is not the same as PR `QueryPie AI 認証`.

4. Separate parity from content correction.
   - If production and stage both show the same wrong card/body text, a PR changing it is not production parity.
   - Frame it as a content bug fix and verify the canonical wording from source content, product docs, or stakeholder-provided copy.

5. Check tests and CI scope.
   - Route-local metadata tests must be updated with the metadata change.
   - If tests still expect the old title, the PR is not valid as-is even if the runtime direction is right.
   - `mergeStateStatus=DIRTY` plus failing checks means the PR should not be merged as-is; classify whether the idea remains valid after rebase.

## Example case: certifications metadata

Observed facts from a corp-web-app certifications PR review:

- EN/KO production title: `QueryPie AI Certifications`.
- EN/KO stage/main had already reached `QueryPie AI Certifications`, so an old PR carrying that change became partly duplicate.
- JA production title: `QueryPie AI: 認証`; stage/main had `認証`; PR proposed `QueryPie AI 認証`, which missed the colon and therefore was not exact parity.
- ISMS-P card text duplicated ISO 22301 (`Business Continuity / Management`) on both production and stage, so changing it was a content bug fix rather than stage-production parity.
- The PR updated metadata source strings but did not update the route-local metadata test, causing targeted Vitest failure.

Recommended verdict shape for this class:

- `Partially valid, not mergeable as-is` when the correction intent is sound but exact metadata, tests, or latest-main conflicts are wrong.
- Recommended action: rebase/reset to latest main, keep only the true remaining delta, use exact production metadata strings where parity is the goal, source canonical wording for independent content fixes, and update tests in the same PR.
