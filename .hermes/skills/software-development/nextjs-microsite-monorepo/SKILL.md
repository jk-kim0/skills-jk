---
name: nextjs-microsite-monorepo
description: Set up and maintain multiple small independent Next.js micro websites in a monorepo with shared UI/link packages and app-level deployment boundaries.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, monorepo, microsite, vercel, tailwind, route-local-authoring]
    related_skills: [nextjs-app-router-route-group-layouts, static-page-route-local-authoring, github-pr-workflow]
---

# Next.js micro-site monorepos

Use this skill when the user wants to create, compare, or maintain multiple small micro websites that share a design language but need separate URLs and efficient operations.

## Default recommendation

For micro websites that each have a separate URL/domain and should remain operationally understandable, prefer:

```text
apps/
  <site-slug>/              # one independent Next.js app per micro website
packages/
  microsite-ui/             # shared UI primitives only
  microsite-links/          # canonical links to the main/hub website
  microsite-seo/            # optional metadata/sitemap helpers
```

Use one Vercel project per app, with `apps/<site-slug>` as the project root.

This keeps:
- the monorepo benefits of shared code and one PR surface
- app-level deployment, rollback, asset, metadata, and URL boundaries
- each app's `/` route matching its actual production root URL
- less hidden routing than host-based middleware rewrites inside one app

## When one Next.js app is acceptable

A single Next.js app can host multiple micro-sites only when the user accepts shared deployment/rollback and the team is comfortable with explicit routing indirection.

If using one app, prefer explicit source paths plus declarative platform rewrites over hidden request logic:

```text
src/app/sites/<site-slug>/page.tsx
public/microsites/<site-slug>/...
vercel.json host-based rewrites
```

Avoid `middleware.ts` host-based rewrites when the user values code-path legibility. Middleware makes `/` render from a hidden internal tree and is easy to misunderstand in local development, sitemap generation, and asset handling.

## Page authoring rule

For small static marketing sites, keep visible copy and section order in `page.tsx`.

Good:

```tsx
<HeroSection>
  <HeroEyebrow>...</HeroEyebrow>
  <HeroTitle>...</HeroTitle>
  <HeroBody>...</HeroBody>
</HeroSection>
```

Avoid generic renderers and large content blobs:

```tsx
<GenericPageRenderer content={pageContent} />
```

Shared packages should expose primitives and small structural helpers, not site-specific story order or campaign copy.

## Asset rules

### Multiple app setup

If each micro-site is its own app, keep site assets in that app's `public/` directory:

```text
apps/finance/public/hero.png
apps/finance/public/og-image.svg
```

Reference them from code with root-absolute public URLs:

```tsx
<Image src="/hero.png" alt="" width={1200} height={630} />
```

### Single app setup

If multiple sites share one app, namespace public assets:

```text
public/microsites/<site-slug>/hero.png
```

Reference them with browser-root absolute paths, not filesystem paths and not relative paths:

```tsx
<Image src="/microsites/seminar-2026/hero.png" alt="" width={1200} height={630} />
```

Do not use `./hero.png`, `../hero.png`, or `/Users/.../hero.png` for website asset URLs.

## Main/hub website links

When micro-sites reuse company/contact/legal/resource surfaces from a main website, keep them as canonical external links rather than duplicating the pages. A tiny shared package is useful:

```ts
export const mainSiteLinks = {
  home: "https://querypie.ai",
  about: "https://querypie.ai/about-us",
  contact: "https://querypie.ai/contact-us",
  privacyPolicy: "https://querypie.ai/privacy-policy",
  termsOfService: "https://querypie.ai/terms-of-service",
  resources: "https://querypie.ai/resources",
} as const;
```

If a contact form supports stable query prefill keys, add a typed URL builder instead of hand-writing many contact URLs.

## Initial setup checklist

1. Confirm the user's desired repo strategy:
   - multiple Next.js apps in one monorepo
   - one Next.js app with explicit `/sites/<slug>` routes
   - one Next.js app with host rewrites
2. If the user wants separate URLs and dislikes hidden routing, recommend multiple apps.
3. Create a fresh branch/worktree from latest main for repo work.
4. Add root npm workspaces and Node LTS config.
5. Add `apps/<site>` with Next.js, TypeScript, Tailwind, sitemap, robots, app README, and site config.
6. Add minimal shared packages only when they prevent real duplication.
7. Add English repository guidance if the user wants docs/comments/PR text in English.
8. Keep public site copy in the requested locale.
9. Run app-level lint/typecheck/build plus a lightweight structure test.
10. Commit, push, and open the PR.

## Verification commands

From the monorepo root:

```bash
npm install
npm run lint --workspace @scope/microsite-<site>
npm run typecheck --workspace @scope/microsite-<site>
npm run build --workspace @scope/microsite-<site>
npm run test
```

For a baseline PR, expose a root command such as:

```bash
npm run test:ci
```

## Pitfalls

- Do not use route groups alone to separate multiple public homepages; route group segment names are invisible in URLs and `/` routes conflict.
- Do not use `middleware.ts` rewrites by default when the user is concerned about readability.
- Do not put site-specific campaign copy into shared UI packages.
- Do not add publication systems, CMS flows, contact form backends, or gated content just because the main website has them. Small micro-sites usually link back to the main website for those functions.
- Do not run `npm audit fix --force` blindly during setup; npm may propose downgrades or major changes. Document the advisory and choose a safe dependency path.

## Reference

- See `references/corp-web-micro-initial-finance.md` for a concrete session pattern: initializing `corp-web-micro`, adding `apps/finance`, shared packages, English guidance, Japanese content, and a PR.