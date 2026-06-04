# Campaign-scoped entity choice flow pattern

Use this reference when a Team-scoped UI card should open a Campaign-scoped choice/create flow for an existing Team asset and then assign the selected asset to the Campaign's child entity, for example Contact List -> Campaign Audience.

## Durable pattern

1. Preserve the Team-scoped route prefix.
   - User shorthand like `/campaign/{slug}/...` in outbound-agent usually means `/{teamSlug}/campaign/{slug}/...` for private app routes.
   - Keep route files under `front/src/app/[teamSlug]/...`.

2. Prefer a Campaign-scoped choice route when the user's intent is assignment into one Campaign.
   - Example routes:
     - `/{teamSlug}/campaign/{slug}/contact-list-choose`
     - `/{teamSlug}/campaign/{slug}/contact-list-new`
   - In Next App Router, these can live under the existing `front/src/app/[teamSlug]/campaign/[id]/...` segment while treating `[id]` as a Campaign slug for the new child routes.

3. Keep the global asset route separate from the assignment route.
   - `/{teamSlug}/contact-lists` remains the Team asset directory.
   - `/{teamSlug}/campaign/{slug}/contact-list-choose` is the Campaign-specific assignment screen.

4. Use Entity Cards for the choice screen when the active UI language is Entity Card-based.
   - Existing asset cards submit a server action with `teamSlug`, `campaignSlug`, and the selected asset id.
   - Include a required-creation Entity Card that links to the Campaign-scoped `*-new` route.

5. Implement assignment as a server action, not as client-only state.
   - Resolve Team scope from `teamSlug`.
   - Resolve Campaign by slug inside that Team scope.
   - Verify the Campaign child entity exists, e.g. `campaign.audience`.
   - Call the domain service that already performs Team-scope validation and side effects, e.g. `connectContactListsToCampaignAudience(campaign.id, { contactListIds: [...] }, user.id, scope)`.
   - Revalidate the Campaign detail, choice/new pages, affected child detail page, and relevant index pages.
   - Redirect back to the Campaign detail route using the slug route when that is the route the user entered.

6. If the detail page historically accepts only id, update the read model deliberately.
   - For a route like `front/src/app/[teamSlug]/campaign/[id]/page.tsx`, allow the read model to resolve `OR: [{ id }, { slug: id }]` when slug links become valid.
   - Add a source-level test so a future edit does not break slug detail links.

7. Update the route-specific UI design document and OpenSpec together.
   - Record the accepted UI decision in `docs/ui/<route>.md` with Component Name Map updates.
   - Add an observable route contract scenario in OpenSpec when new routes become canonical.

## Verification checklist

- Focused source-level test asserts:
  - the originating card links to `/{teamSlug}/campaign/${campaignSlug}/...`,
  - new route files exist,
  - server actions call the existing assignment domain service,
  - detail read model accepts id or slug.
- Run focused Vitest, focused ESLint, `npm run typecheck`, and `git diff --check`.

## Pitfalls

- Do not replace the Team asset directory with the Campaign-scoped assignment route.
- Do not add a Team-less private route just because the user omits `{teamSlug}` in shorthand.
- Do not create a separate plural detail route such as `/{teamSlug}/contact-lists/{id}` when the repo's route contract uses singular detail routes.
- Do not resolve assignment only by Campaign id if the new UI route is slug-based; keep the action payload and read model aligned with the route the user sees.
