# Translation coverage layout spacing follow-up

Session pattern from an internal translation coverage spacing review:

- Scope was internal-only corp-web-app pages under `src/app/[locale]/internal/translations/**`.
- The visible issue was excessive vertical space between the `Translation coverage` eyebrow/header area and the content/card region.
- The useful fix was not route-specific tweaks on only one page. Extract or reuse a shared internal layout primitive for the translation coverage family so blog/events pages keep the same spacing contract.
- When a later sibling route (for example another `/internal/translations/<family>` page) is added or merged after the shared primitive lands, update that sibling to consume the existing primitive instead of reintroducing a copy of the old inline style block. If both the original route PR and the primitive PR are already merged, start a fresh latest-main follow-up PR rather than reviving either merged branch.
- Final shared layout contract used in that session:
  - shell padding: `30px`
  - shell background: transparent/no page-specific background
  - content max width: `1200px`
  - list/content section top margin: `40px`
  - remove redundant right-side list-description helper copy when it visually inflates the hero-to-content gap
  - avoid a duplicate visible heading immediately above the list; if the list label is the meaningful page label, promote that text to the page-level `h1` and remove the list-level `h2`
  - for blog/events/news translation coverage, the h1 labels became `Blog content availability`, `Event content availability`, and `News content availability`; the old short `Blog`/`Events`/`News` h1 labels were replaced
- Implementation pattern:
  - keep the family pages thin and route-specific: pass the desired h1 title, description, summary label/items, and children into `TranslationCoverageLayout`
  - keep `TranslationCoverageLayout` responsible for the shared shell/hero/list spacing
  - if the visible list heading is removed, keep a non-visible section label such as `aria-label={`${title} list`}` so the content region remains identifiable without adding duplicate UI text
- Test pattern:
  - route tests should assert the content-availability label is an `h1`
  - add a negative assertion that the same label is not rendered as an `h2`, so duplicate list headings do not regress
- Browser verification should inspect the exact affected URL and a sibling route that shares the primitive. A practical computed-style probe checks:
  - page shell padding
  - page shell background color
  - eyebrow top position
  - content/list section `marginTop`
- If a local dev server was started for browser review, stop it before creating the PR and verify the port is clear.
- PR body should describe the final visual contract, not the intermediate spacing experiments.
