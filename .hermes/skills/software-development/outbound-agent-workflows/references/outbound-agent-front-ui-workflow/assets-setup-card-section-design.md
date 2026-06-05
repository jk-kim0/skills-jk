# Assets setup card section design pattern

Use this reference when updating or implementing `/{teamSlug}/assets` UI design around Entity Card state variants.

## Canonical content structure

`/{teamSlug}/assets` should not keep a separate `Assets Overview` summary section when the product direction is card-first setup review.
Use three content sections under `PageHeader`:

1. `Setup checklist`
   - Shows only Required Create cards.
   - Required Create means the missing asset blocks the setup/Campaign flow enough to require immediate creation.
2. `Optional Create`
   - Shows only Optional Create cards.
   - Optional Create means the user can add another setup asset, but the current flow is not blocked.
3. `Current assets`
   - Shows only real Entity Cards for existing assets.
   - Do not mix create cards into this section.

## Entity count mapping

| Entity type | Count = 0 | Count >= 1 |
| --- | --- | --- |
| Company | Optional Create | Entity Card |
| Product | Optional Create | Optional Create + Entity Card |
| Audience Source | Required Create | Optional Create + Entity Card |
| Sales Person | Required Create | Optional Create + Entity Card |
| Email Template | Required Create | Optional Create + Entity Card |

Notes:

- Product always has an Optional Create card so the user can add reusable Products even when Products already exist.
- Company with zero records is Optional Create, not Required Create.
- Audience Source currently maps Contact List as a subtype; use `Audience Source` as the card eyebrow and `Contact List` as subtype/meta.
- Current assets should omit empty groups instead of adding State-only Cards; the empty/creation state is already handled by Required/Optional Create sections.

## Docs to update together

For docs-only design changes, update the route-specific doc and cross-links in the same PR:

- `docs/ui/assets.md`
- `docs/ui/README.md`
- `docs/ui/screen-overview.md`
- `docs/ui/uri-map.md`
- `docs/ui/sidebar-navigation-ia-plan.md` when the Assets/Sidebar IA section mentions old overview/tab language

PR bodies for these docs-only UI design changes should still include a `UI 변경` section listing `/{teamSlug}/assets` because the PR changes screen design expectations.
