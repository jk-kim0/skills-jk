# AIP integrations category query compatibility

Context: corp-web-japan local preview/canonical AIP integrations pages should keep semantic category keys internally, but copied URLs from the live QueryPie Japan page may contain numeric category query values.

Observed live behavior:
- `https://www.querypie.com/ja/solutions/aip/integrations?category=0` filters to the first category, workflow automation.
- Numeric category values follow the UI order from the live page.
- Representative mapping captured during the fix:
  - `0` -> `workflow-automation`
  - `1` -> `google-workspace`
  - `2` -> `project-management`
  - `9` -> `search-navigation`

Recommended implementation pattern:
1. Keep authored category constants and `categoryKeys` semantic.
2. Define a route-local numeric-to-semantic mapping at the search-param boundary.
3. Normalize incoming `searchParams.category` before selecting the active filter.
4. Add tests for representative numeric query values.
5. Add a guard test that canonical category keys are not numeric strings.

Pitfall:
- Do not convert the source-of-truth category model to numeric IDs just because live URLs accept numbers. Numeric query support is a backwards/live-URL compatibility shim, not the canonical local data model.
