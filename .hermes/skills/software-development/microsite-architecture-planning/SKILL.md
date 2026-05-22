---
name: microsite-architecture-planning
description: Plan and design small, independently operated marketing micro-sites that reuse a main website's design language without copying its full application complexity.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [microsites, architecture, nextjs, monorepo, marketing-sites, operations]
---

# Microsite Architecture Planning

Use this skill when the user asks how to implement, structure, operate, or scale multiple small marketing micro-sites, especially when they should resemble an existing main website but remain lightweight and independently operated.

## Trigger conditions

Use this skill for requests like:

- planning multiple campaign, event, partner, product, or landing micro-sites
- deciding between per-site repos, a micro-sites monorepo, or one multi-site application
- reusing a main website's design/code style across many small sites
- planning micro-sites with separate URLs/domains/subdomains
- keeping common company/about/contact/legal/resource functions on the main website while micro-sites link out
- designing a starter template, generator, shared UI kit, or shared SEO/link helpers for small sites

## Default recommendation shape

For 1-5 page micro-sites that each have a separate URL but should be efficient to operate, prefer:

- one `micro-sites` monorepo when the user chooses centralized repo management
- `apps/<site-name>` as independent Next.js apps
- site-specific Vercel projects/domains/env vars for deployment independence
- shared internal packages for UI primitives, theme, SEO, analytics, and main-site links
- route-local `page.tsx` authoring for marketing copy and page composition
- main website links for company/about/contact/legal/resources instead of copying those flows into each micro-site

The key operating model is: centralize code/reuse, decentralize runtime ownership.

## Repo strategy decision guide

### Prefer a micro-sites monorepo when

- the user wants one place to manage many similar small sites
- sites are built by the same team or agents
- shared UI/theme/SEO updates should be easy to apply
- new site creation speed matters
- sites can share dependency and CI conventions
- each site can still have its own Vercel project/root directory

### Prefer per-site repos when

- sites have independent owners, lifecycles, or compliance requirements
- archival/deletion per site is more important than shared code velocity
- each site should pin shared kit versions and upgrade intentionally
- repository permissions differ by site

### Avoid one giant multi-site Next.js app when

- each micro-site needs separate URL/deploy/rollback ownership
- site routes, SEO, analytics, and campaign timelines should stay isolated
- conditional `siteId` branching would spread throughout components and config

## Recommended monorepo layout

```text
micro-sites/
  package.json
  tsconfig.base.json
  .github/workflows/
  apps/
    <site-name>/
      package.json
      next.config.ts
      tsconfig.json
      src/app/layout.tsx
      src/app/page.tsx
      src/app/sitemap.ts
      src/app/robots.ts
      src/app/not-found.tsx
      src/lib/site-config.ts
      public/og-image.png
  packages/
    microsite-ui/
    microsite-theme/
    microsite-seo/
    microsite-links/
  scripts/
    create-microsite.mjs
```

Each app should be deployable by setting the Vercel Project Root Directory to `apps/<site-name>`.

## What to share

Good shared packages:

- `microsite-ui`: header, footer, hero shell, section shell, CTA buttons, cards, FAQ primitives, final CTA, media frames
- `microsite-theme`: global CSS, CSS variables, typography scale, max-width defaults, color/radius/shadow/motion tokens
- `microsite-seo`: metadata helpers, sitemap helpers, robots helpers, Google Analytics component, site URL helpers
- `microsite-links`: canonical main-site links and contact URL builders

Keep shared package components copy-free. They should expose UI primitives and compound components, not own campaign text or page order.

## What not to copy from a full main website

Do not pull heavy main-site systems into tiny micro-sites unless explicitly needed:

- publication/blog/whitepaper/news loaders
- gated content systems
- contact form submit backends
- complex missing-route redirect allowlists
- large resource-list sidebars
- internal preview/migration routes
- full main-site GNB or site map
- broad app-specific migration skills and tests

For small micro-sites, link to the main website for company profile, contact, legal, and resources.

## Page authoring rule

For static marketing micro-sites, keep visible copy and page composition directly readable in `src/app/**/page.tsx`.

Prefer:

```tsx
<HeroSection>
  <HeroEyebrow>AI Seminar 2026</HeroEyebrow>
  <HeroTitle>AI活用を、現場の成果につなげる</HeroTitle>
  <HeroBody>...</HeroBody>
  <HeroActions>
    <PrimaryCta href={siteConfig.contactUrl}>お問い合わせ</PrimaryCta>
  </HeroActions>
</HeroSection>
```

Avoid:

```tsx
<GenericPageRenderer content={pageContent} />
```

Also avoid large `sections = [...]` or `hero = { ... }` registries for one-off marketing pages. These hide visual hierarchy and make review harder.

## Main-site link package pattern

Use a small helper package for stable main-site links:

```ts
export const mainSiteLinks = {
  home: "https://querypie.ai",
  about: "https://querypie.ai/about-us",
  contact: "https://querypie.ai/contact-us",
  privacyPolicy: "https://querypie.ai/privacy-policy",
  termsOfService: "https://querypie.ai/terms-of-service",
  resources: "https://querypie.ai/resources",
};

export function buildContactUrl(params?: {
  inquiry?: string;
  product?: string | string[];
}) {
  const url = new URL(mainSiteLinks.contact);

  if (params?.inquiry) {
    url.searchParams.set("inquiry", params.inquiry);
  }

  const products = Array.isArray(params?.product)
    ? params.product
    : params?.product
      ? [params.product]
      : [];

  for (const product of products) {
    url.searchParams.append("product", product);
  }

  return url.toString();
}
```

When adapting for a specific main website, use its real route and query-param contract.

## Site config pattern

Each app should have a small `src/lib/site-config.ts`:

```ts
export const siteConfig = {
  id: "seminar-2026",
  name: "QueryPie AI Seminar 2026",
  productionUrl: "https://seminar-2026.querypie.ai",
  locale: "ja",
  gaMeasurementId: "G-XXXXXXX",
  mainSiteUrl: "https://querypie.ai",
  contactUrl: "https://querypie.ai/contact-us?inquiry=demo-request",
  ogImagePath: "/og-image.png",
};
```

Keep site-wide settings here. Do not turn this into a page content registry.

## Deployment guidance

For independent operation inside one monorepo:

1. Create a separate Vercel project per micro-site.
2. Set the Vercel Root Directory to `apps/<site-name>`.
3. Attach each project's own domain or subdomain.
4. Keep environment variables per Vercel project.
5. Roll back site-by-site through each project's deployment history.
6. In CI, build only affected apps when possible; build all apps when shared packages change until dependency graph optimization exists.

## Generator guidance

If there will be more than a couple of micro-sites, add a generator such as:

```bash
npm run create:microsite -- seminar-2026
```

It should create:

- app package file
- `next.config.ts`
- `tsconfig.json`
- `src/app/layout.tsx`
- `src/app/page.tsx`
- `src/app/sitemap.ts`
- `src/app/robots.ts`
- `src/app/not-found.tsx`
- `src/lib/site-config.ts`
- placeholder OG image or documented asset path
- app README with Vercel setup notes

## Common pitfalls

- Do not over-share campaign-specific sections into `packages/microsite-ui` after only one use.
- Do not make a generic page renderer for small marketing pages.
- Do not copy the full main website's publication, contact form, or redirect machinery into each micro-site.
- Do not use one Vercel project for all sites if independent rollback/deploy is a requirement.
- Do not let shared package updates silently redesign all active campaigns; keep primitives stable and review package changes carefully.
- Do not confuse repo centralization with deployment centralization.

## Reference files

- `references/querypie-microsite-monorepo.md` captures the session-specific decision record for QueryPie-style micro-sites: separate URLs, 1-5 page sites, common functions linked back to the main site, and the selected micro-sites monorepo strategy.
