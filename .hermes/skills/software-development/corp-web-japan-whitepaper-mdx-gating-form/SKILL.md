---
name: corp-web-japan-whitepaper-mdx-gating-form
description: "Implement whitepaper-only MDX gating in corp-web-japan using gated frontmatter, a GatingCut MDX marker, same-page unlock, and cookie persistence via a dummy API route."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, mdx, whitepaper, gating, cookie, nextjs]
    related_skills:
      - corp-web-japan-origin-main-worktree-safety
      - test-driven-development
---

# corp-web-japan: whitepaper MDX gating form

Use this when the user asks for gated whitepaper-style content in `corp-web-japan`, especially when the gated content should live inside MDX and unlock inline on the same page.

## Scope and policy

This pattern is for:
- `whitepaper` MDX only
- per-document control via frontmatter `gated: true`
- explicit content split via custom MDX marker `<GatingCut />`
- same-page unlock after form submission
- persistence via cookie
- a backend API that can either stay dummy or submit through the shared contact-style backend modules while setting the unlock cookie, depending on the current repo state

Do not apply this by default to blog/event unless the user explicitly broadens scope.

## Required contract

### In the MDX file

Add frontmatter:

```yaml
gated: true
```

Add an explicit cut marker where the form wall should appear:

```mdx
<GatingCut />
```

Behavior:
- content before `<GatingCut />` remains visible
- content after `<GatingCut />` is hidden until unlocked

### Cookie TTL

Use host-based TTL:
- stage hosts (`stage.*`) -> 5 minutes
- all other hosts -> 48 hours

## Files and architecture

### Gating helper

Create a small helper module to centralize:
- cut marker constant
- content key generation
- cookie name generation
- host-based max-age
- source splitting at `<GatingCut />`
- frontmatter stripping for rendering the gated-only MDX fragment

Suggested file:
- `src/lib/publications/gating.ts`

Useful exports:
- `GATING_CUT_MARKER`
- `buildGatingContentKey(scope, id)`
- `buildGatingCookieName(contentKey)`
- `getGatingCookieMaxAgeSeconds(hostname)`
- `splitMdxSourceAtGatingCut(source)`
- `stripFrontmatterBlock(source)`

### Gating unlock API route

Add or update:
- `src/app/api/gating-form/unlock/route.ts`

Behavior:
- accept `POST`
- require `contentKey` in JSON body
- return `400` if missing
- delegate the form submission to a dedicated gating submit helper
- set an httpOnly cookie for the content key only after a successful submit result
- respond with `{ success: true }` on success

Preferred implementation in the current repo state:
- keep the route thin
- reuse the shared server modules already introduced for contact-us submit handling
- create a dedicated `src/lib/gating-form-submit.ts` orchestrator that mirrors `src/lib/contact-us-submit.ts` while reusing:
  - `src/lib/forms/server/sanitize.ts`
  - `src/lib/forms/server/email-deliverability.ts`
  - `src/lib/forms/server/utm-attribution.ts`
  - `src/lib/forms/server/slack-notification.ts`
  - `src/lib/forms/server/salesforce-delivery.ts`
- keep Salesforce delivery best-effort and Slack notification required, matching the current contact-us backend behavior unless the user asks to diverge
Cookie settings:
- `httpOnly: true`
- `sameSite: "lax"`
- `secure` only for https requests
- `path: "/"`
- `maxAge` based on host

### MDX renderer support

Update the publication MDX components to include:

```tsx
function GatingCut() {
  return null
}
```

and register it in `buildPublicationMdxComponents()`.

Do not rely on the legacy `ArticleGatingForm` wrapper. If it still exists for compatibility, leave it inert and move new documents to `<GatingCut />`.

### Whitepaper loader behavior

In `src/lib/publications/get-whitepaper-publication-post.ts`:

1. Read the raw MDX source
2. Split at `<GatingCut />`
3. Render the preview segment with frontmatter parsing on
4. If `frontmatter.gated` is true:
   - require that a gated segment exists; throw if missing
   - render the gated segment separately after stripping frontmatter and with `parseFrontmatter: false`
5. Build a `PublicationPost` with:
   - `bodyMdx` = preview content
   - `gatedBodyMdx` = gated content or `null`
   - `gating` = `{ contentKey, initiallyUnlocked: false }` or `null`
6. Build TOC from the preview segment only for gated whitepapers

Important: for non-gated whitepapers, keep normal full-body rendering behavior.

### Publication type shape

Extend `PublicationPost` to support the new contract:
- `gatedBodyMdx: ReactNode | null`
- `gating: PublicationPostGating | null`

with:

```ts
export type PublicationPostGating = {
  contentKey: string
  initiallyUnlocked: boolean
}
```

Also update blog loaders and any legacy `ResourcePost` types so they explicitly provide:
- `gatedBodyMdx: null`
- `gating: null`

Otherwise `PublicationPostPage` type usage will break in event/legacy routes.

### Client gating component

Reuse or adapt `src/components/sections/resource-lead-form.tsx` and `src/components/sections/resource-post-gated.tsx`.

Expected form fields should match the `corp-web-app` JA gating form shape:
- last name
- first name
- business email
- company
- department/title
- phone (optional)
- inquiry type
- product multi-checkbox
- implementation date
- marketing opt-in
- legal helper text using `/terms-of-service` and `/privacy-policy`

Expected client flow:
- show form when `initiallyUnlocked` is false
- validate required fields client-side before submit
- POST to `/api/gating-form/unlock`
- include `contentKey`, `form`, `referrerUrl`, and optional `utmAttribution` when available
- on success, reveal gated content inline on the same page
- on failure, surface the backend error message in Japanese instead of collapsing everything into a generic failure
### Whitepaper detail route

In `src/app/whitepapers/[id]/[slug]/page.tsx`:
- read cookies via `cookies()`
- if `post.gating` exists, set `post.gating.initiallyUnlocked = cookieStore.has(buildGatingCookieName(post.gating.contentKey))`
- then render `PublicationPostPage`

### Internal demo route

If the user wants a test page, add an internal MDX-backed route such as:
- `src/app/internal/whitepaper-gating-demo/page.tsx`
- `src/content/internal/whitepaper-gating-demo.mdx`

Use the same split/render/cookie pattern as the whitepaper loader so the demo exercises the real gating flow.

Set metadata robots to noindex/nofollow.

## PublicationPostPage integration

Update `PublicationPostPage` to render:
- preview `bodyMdx` first
- then gated form / gated content block if `post.gating` exists

Prefer a single MDX body class export that can style both preview and revealed content uniformly.

## Migration notes for existing content

If a whitepaper already uses legacy wrapper markup like:

```mdx
<ArticleGatingForm>
...
</ArticleGatingForm>
```

migrate it to:
- frontmatter `gated: true`
- a single `<GatingCut />` marker
- normal MDX content after the marker

Do not preserve the wrapper around the hidden section.

## Testing strategy

A lightweight source-based regression test is effective here.

Add or update a test like `tests/whitepaper-gating-source.test.mjs` to verify:
- a target whitepaper contains `gated: true`
- it contains `<GatingCut />`
- it no longer contains legacy `<ArticleGatingForm>` wrappers
- MDX components define `GatingCut`
- the whitepaper loader references `gatedBodyMdx` and `contentKey`
- `PublicationPost` includes `gating`
- an internal `/internal/...` demo page and MDX source exist

Run first:

```bash
node --test tests/whitepaper-gating-source.test.mjs
```

## Common pitfalls

### 1. Breaking shared `PublicationPostPage` typing

If you add `gatedBodyMdx` and `gating` to `PublicationPost`, you must also update:
- blog loader
- legacy resource/event post type(s)

Otherwise type errors appear in:
- `src/app/events/[id]/[slug]/page.tsx`
- `src/app/posts/[category]/[slug]/page.tsx`

### 2. Leaving legacy gating fields around

Old `gatingHtml` / `gatedContentHtml` fields from historical HTML flows are not the right contract for MDX gating. Remove or isolate them from the shared publication type path.

### 3. parseFrontmatter on gated fragment

The post-cut fragment should usually be rendered with `parseFrontmatter: false` after stripping the original frontmatter block. Otherwise the gated fragment render can mis-handle the source.

### 4. Missing `<GatingCut />` in a gated whitepaper

If `gated: true` is set but no cut marker exists, throw an explicit error. Silent fallback makes authoring mistakes hard to catch.

### 5. Stage TTL handling

Keep TTL logic centralized. Do not hardcode separate durations in multiple components/routes.

### 6. Verification environment issues

If local shell commands start failing with process-limit errors like:
- `spawn sh EAGAIN`
- `Resource temporarily unavailable`

stop retrying long verification loops. Report the environment issue and preserve the already-passing focused regression test result.

## Done criteria

The feature is done when:
- whitepaper MDX supports `gated: true`
- `<GatingCut />` splits preview vs hidden content
- unlock happens inline on the same page
- cookie persistence works with 5m on stage and 48h elsewhere
- dummy API route sets the cookie without real submission
- `/internal/...` demo route exists if requested
- focused regression test passes
