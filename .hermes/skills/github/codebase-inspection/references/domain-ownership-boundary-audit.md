# Domain Ownership Boundary Audit Reference

Use this when a session establishes that a field/concept belongs to exactly one owner entity and must disappear from all child/peer entities.

## Trigger examples

- “Country/language are Team attributes only; no other entity should set them.”
- “Market exists only on Team; build separate Teams per market.”
- “Remove market selection/display/input from Campaign/Product/Audience/etc.”
- “Verify all schema/docs/UI are aligned with this ownership rule.”

## Audit checklist

1. Define the owner and forbidden non-owner surfaces.
   - Owner: Team, Organization, Workspace, Tenant, Project, etc.
   - Non-owners: child entities, join models, forms, DTOs, fixtures, tests, docs, UI mockups.

2. Search for current and legacy field names.
   - Exact fields: `country`, `language`, `market`, `targetMarket`.
   - Related names: `locale`, `region`, `territory`, `geo`, `marketScope`.
   - Human copy: “country”, “language”, “market”, “국가”, “언어”, “市場”, etc.

3. Verify implementation layers in order.
   - Database/schema/ORM models.
   - API route handlers, server actions, DTO/Zod schemas, generated clients.
   - Forms, filters, tables, detail views, badges, import/export mappings.
   - Seeds/fixtures/test factories.
   - Regression/source tests that may still assert old fields.

4. Verify non-code source-of-truth.
   - OpenSpec/project requirements.
   - Feature specs and change specs.
   - UI design docs, screen maps, URI maps, page inventories.
   - Planning docs and PR bodies if they are reviewer-facing source-of-truth.

5. Edit the requirement positively.
   - Good: “Market is Team-scoped. Market-specific operation is represented by separate Teams. Campaigns inherit the Team context and do not expose market/country/language inputs.”
   - Bad: “Campaign market will not be supported for now” (sounds temporary) or “Campaign has inherited market field” (implies a child field still exists).

6. Post-edit proof.
   - Run targeted searches over code + docs.
   - Classify remaining hits as: owner-scoped, requirement statement, historical reference intentionally retained, or still stale.
   - If a stale hit remains in docs/design, fix it before reporting completion.

## Report shape

```text
정리 완료:
- Owner requirement/spec: <paths>
- Implementation verified/changed: <paths>
- UI/docs stale references removed: <paths>

남은 검색 hit:
- <path>: owner-scoped / new requirement text / intentional history

검증:
- <search/check command> — <result>
```

## Pitfalls

- Database-only verification is insufficient. User-facing stale copy can still contradict the product rule.
- Do not introduce shadow/inherited fields on the child entity when the product rule is “use owner context implicitly.”
- Do not leave “Market per Campaign/Audience” language in design docs when the operation model is “Team per Market.”
- If a merged PR established the initial rule, treat that PR as context and start follow-up work from latest main rather than reviving its branch.
