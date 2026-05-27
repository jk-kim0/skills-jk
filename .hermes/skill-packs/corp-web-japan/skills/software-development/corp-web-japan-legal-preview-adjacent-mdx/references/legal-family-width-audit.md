# Legal family width audit notes

Use this note when reviewing corp-web-japan legal preview pages (`/t/privacy-policy`, `/t/terms-of-service`, `/t/eula`) for width policy and family classification.

## Main conclusion
- `max-w-[920px]` in the current preview legal pages is not supported by live rendering, upstream layout contracts, or the current source-material evidence.
- Treat `920px` as a wrong local divergence unless new evidence appears.

## Live browser evidence
Direct browser inspection during the audit showed:
- `https://www.querypie.com/ja/terms-of-service` main legal content span: about `1200px`
- `https://www.querypie.com/ja/eula` main legal content span: about `1200px`
- `https://www.querypie.com/ja/privacy-policy` title/selector/body section span: about `1200px`

Representative measurements captured during the audit:
- live `/ja/terms-of-service`: `h1` / document section width `1200px`
- live `/ja/eula`: `h1` / document section width `1200px`
- preview `/t/terms-of-service`: route wrapper `max-w-[920px]`
- preview `/t/privacy-policy`: title block rendered inside a `920px`-limited wrapper

## Upstream implementation evidence
Relevant upstream files:
- `../corp-web-app/src/components/foundation/layout/center-section.component.tsx`
- `../corp-web-app/src/components/foundation/layout/center-section.module.css`
- `../corp-web-app/src/app/globals.css`

Key facts:
- `CenterSection` uses `max-width: var(--content-max-width)`
- `--content-max-width: 1200px`
- Live legal pages visibly use the `center-section` DOM/layout path

Interpretation:
- the legal target pages inherit the standard upstream `1200px` content-width contract
- there is no evidence here for a legal-only `920px` outer shell

## Source-material evidence
Checked source families such as:
- `../corp-web-contents/pages/terms-of-service-en/en/content.mdx`
- `../corp-web-contents/pages/terms-of-service-ja/en/content.mdx`
- privacy-policy / eula source counterparts

Observed structure:
- legal source content uses `CenterSection` / `Box`-style composition
- no direct source-of-truth for a legal-document-wide `920px` cap was found in the audited source set

## Repo-history evidence
The local `920px` shell appeared from the initial preview legal-page implementations:
- PR #206 `feat: add terms of service preview page`
- PR #321 `feat: add eula preview page`
- PR #320 `feat: add privacy policy preview page`

Those PRs referenced live/source evidence in general, but the audit found no explicit rationale for changing the legal shell from the live/upstream `1200px` behavior to `920px`.

Later refactors such as:
- PR #411 `refactor: move legal preview section components into family directories`
- PR #422 `refactor: move privacy policy preview renderer into route pages`

changed structure/location, not the width decision itself.

## Family-classification rule
Do not classify privacy-policy as a family-level exception just because it uses:
- latest-version alias route
- per-version detail routes
- selector row
- versioned MDX corpus

Correct framing:
- legal/document family
  - single-version legal MDX pattern
  - multi-version legal MDX pattern

Privacy-policy is the multi-version pattern.
EULA / Terms of Service are currently single-version patterns, but may evolve to the same multi-version shape if historical versions are later published.

## Review checklist
When auditing future legal-page changes:
1. compare live `querypie.com/ja` rendering before assuming a narrow legal shell
2. check upstream `corp-web-app` layout contracts before introducing a special width
3. separate outer shell width from inner prose measure
4. treat privacy-policy as the multi-version legal pattern, not an out-of-family exception
5. avoid primitive-izing a local width that is already known to be inconsistent with live/upstream behavior
