# corp-web-micro initial Finance setup

This reference captures a concrete pattern for initializing a small micro-site monorepo.

## User requirements

- New repo: `~/workspace/corp-web-micro`.
- Repository documentation, README, guidance, comments, PR title/body should default to English.
- Public website content should be Japanese for now.
- Use `corp-web-japan` as a reference for workflow and guidance, not as a full code copy.
- Prefer a monorepo strategy.
- The user initially explored a single Next.js app with route groups/rewrites, but found `middleware.ts` host rewrites non-intuitive.
- Final implementation used multiple Next.js apps under one monorepo.
- First site: Finance AIP, based on `https://finance-ow7i0ad0t-jane-na-querypies-projects.vercel.app/`.

## Implemented repo shape

```text
corp-web-micro/
  apps/
    finance/
      src/app/page.tsx
      src/app/layout.tsx
      src/app/sitemap.ts
      src/app/robots.ts
      src/lib/site-config.ts
      public/
  packages/
    microsite-ui/
    microsite-links/
  .agents/skills/
    micro-site-authoring/
    micro-site-setup/
  tests/
    repo-structure.test.mjs
```

## Dependency choices

At the time of the session, current package versions were:

- Next.js `16.2.6`
- React `19.2.6`
- React DOM `19.2.6`
- Tailwind CSS `4.3.0`
- TypeScript `6.0.3`
- Node runtime target: Node `24` LTS

Use the latest stable/LTS versions at implementation time rather than freezing to these exact values forever.

## npm workspace caveat

In this setup, `workspace:*` dependency specifiers failed with:

```text
EUNSUPPORTEDPROTOCOL Unsupported URL Type "workspace:"
```

The practical workaround for app dependencies on local packages was:

```json
{
  "dependencies": {
    "@querypie/microsite-links": "file:../../packages/microsite-links",
    "@querypie/microsite-ui": "file:../../packages/microsite-ui"
  }
}
```

This is a setup-specific workaround, not a universal rule. Prefer the package manager's standard workspace protocol when it works in the target repo.

## Finance page conversion approach

The reference site was a static HTML/CSS page. The implementation extracted the rendered text and rebuilt the page in React/Tailwind rather than copying raw CSS wholesale.

Key sections captured:

- Hero: `信頼できるAIが / 金融の現場を動かす`
- Trust stats: `90%`, `24/7`, `<5分`
- Platform/solution introduction
- Finance AIP value cards
- Three YouTube demo cards
- Core capability cards
- Use cases
- Roadmap and final CTA

The copy stayed directly in `apps/finance/src/app/page.tsx`; shared packages provided only primitives.

## Guidance/skills copied forward

The new repo received English guidance in:

- `README.md`
- `AGENTS.md`
- `apps/finance/README.md`
- `.agents/skills/micro-site-authoring/SKILL.md`
- `.agents/skills/micro-site-setup/SKILL.md`

The repo-local skills were adapted from the `corp-web-japan` route-local authoring and repo-local skill conventions, but narrowed for small independent micro-sites.

## Verification

Baseline verification used:

```bash
npm run test:ci
```

This ran:

- app lint
- app typecheck
- structure test
- app build

CI used GitHub Actions with Node 24 and `npm install`.

## Audit note pattern

`npm audit --audit-level=moderate` reported a PostCSS advisory through the current Next.js release. npm suggested a forced fix that would downgrade Next to `9.3.3`, so the PR documented the advisory rather than applying an unsafe downgrade.

Reusable lesson: do not blindly run `npm audit fix --force` during scaffold/setup work; inspect the suggested fix and document/adapt safely.
