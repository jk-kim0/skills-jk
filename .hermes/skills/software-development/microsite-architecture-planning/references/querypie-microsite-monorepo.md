# QueryPie-style micro-sites monorepo decision record

## Session context

The user wanted a way to implement multiple micro websites with a similar design and code structure to `corp-web-japan`.

Resolved constraints:

- Each micro-site will have a separate URL/domain/subdomain.
- Each micro-site is small: roughly 1-5 `page.tsx` pages.
- Common functions such as company profile, contact, legal pages, and resources should link back to the main `corp-web-japan` website instead of being reimplemented.
- The user selected repo strategy B: a `micro-sites` monorepo.

## Recommended architecture

Use one monorepo containing independent Next.js apps:

```text
micro-sites/
  apps/
    seminar-2026/
    aip-campaign/
    partner-lp/
  packages/
    microsite-ui/
    microsite-theme/
    microsite-seo/
    microsite-links/
  scripts/
    create-microsite.mjs
```

Each app should have its own Vercel project, root directory, domain, env vars, and rollback history.

## Main idea

Centralize code and reuse, decentralize runtime ownership.

This gives the user:

- one place to manage many small sites
- shared design primitives and SEO/link helpers
- fast new-site creation through a generator
- site-specific deployment and rollback through separate Vercel projects

## What to keep lightweight

Do not copy the full `corp-web-japan` application shape into micro-sites. Exclude by default:

- publication systems
- gated whitepaper flows
- local contact form backends
- complex missing-route redirects
- resource sidebars
- internal preview routes
- full main-site navigation

For micro-sites, use simple headers/footers and link out to the main website:

- logo/home -> `https://querypie.ai`
- company/about -> `https://querypie.ai/about-us`
- contact -> `https://querypie.ai/contact-us`
- privacy policy -> `https://querypie.ai/privacy-policy`
- terms -> `https://querypie.ai/terms-of-service`
- resources -> `https://querypie.ai/resources`

## Page authoring preference

Even in a shared monorepo, static marketing copy should remain directly readable in each app's `page.tsx`.

Use shared packages for primitives, not for full page rendering. Avoid JSON-like `pageContent` registries and generic page renderers for these small sites.

## Contact link rule

When linking from micro-sites to the QueryPie AI Japan contact form, prefer the main site's stable public query-string contract:

- `inquiry=demo-request`
- `inquiry=ai-consulting`
- repeatable `product=...` params when appropriate

Example:

```text
https://querypie.ai/contact-us?inquiry=demo-request
https://querypie.ai/contact-us?inquiry=ai-consulting&product=ai-dashi
```

## Implementation sequence

1. Create the monorepo with npm workspaces.
2. Create one first real app, not an abstract mega-framework.
3. Add shared packages for only obvious primitives: UI, theme, SEO, links.
4. Connect the first app to its own Vercel project using `apps/<site>` as Root Directory.
5. Add minimal CI: app build for changed app; all-app build when shared packages change.
6. Add `create-microsite` once a second or third site is expected.
7. Move only repeated, copy-free primitives into shared packages.

## Pitfall to avoid

A monorepo can still become operationally coupled if all sites share one deployment target. Keep Vercel projects separate if the requirement is independent operation.
