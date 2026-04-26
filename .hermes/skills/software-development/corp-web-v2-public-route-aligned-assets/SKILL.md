---
name: corp-web-v2-public-route-aligned-assets
description: In corp-web-v2, align migrated public assets to route-shaped public paths without inventing extra path segments, and watch for Vercel output-tracing side effects when large public trees are added.
---

When to use
- User asks to reorganize public assets so they match app route / URI structure.
- You are migrating large content trees with many inline images/files into corp-web-v2.
- A Vercel Preview deploy starts failing after adding many files under public/.

Key rules
1. Treat example path strings as examples unless the user explicitly says they are literal.
2. In corp-web-v2, route-aligned asset paths should mirror the public URI shape directly under public/.
3. Do not invent an extra intermediate segment such as public/path/... unless the repo already uses that convention and the user explicitly wants it.
4. For Solutions content, route-aligned assets should use public/solutions/... to match /solutions/..., not public/path/solutions/....
5. Page-specific non-image assets (for example animation JSON, Lottie payloads, or other page-only data files) should be colocated with the related route's asset directory under public/solutions/<route>/... rather than left in a generic shared root like public/assets/.

Recommended workflow
1. Inspect the actual page route family under src/app before moving any assets.
   - Example: src/app/[locale]/solutions/[[...slug]]/page.tsx implies public-facing URI family /solutions/...
2. Search migrated content for current asset references.
   - Look for filepath=, image=, thumbnailImg=, titleImage=, iconFilepath= and plain public/... strings.
3. Convert both content references and actual files together.
   - Rewrite MDX/TSX references first or in the same scripted pass.
   - Move/rename the corresponding files under public/ so the URL path and file path stay consistent.
4. Verify there are zero stale references to the old pattern.
   - Search for the old prefix globally after the move.
5. Run focused tests, then typecheck and build.
6. If Preview deploy fails on Vercel after adding many public assets, inspect trace-related causes before changing unrelated feature code.

Vercel tracing lesson
- Large new public trees can expose pre-existing generic filesystem access in API routes.
- Watch for code that reads from generic public roots such as process.cwd()/public or broad path joins involving public.
- Prefer narrowing file access to explicit subdirectory roots used by that route.
- But keep the architectural boundary in mind: if the user’s task is unrelated to CMS, avoid casually reframing the solution as a CMS API change. First consider whether route/config/tracing-level solutions can solve it more cleanly.

Verification checklist
- Asset URLs match route family directly, e.g. public/solutions/acp/... for /solutions/acp/...
- Page-specific non-image assets (for example animation JSON such as dac-analyzer.json) are colocated with the related route assets instead of being left in generic roots like public/assets/.
- No invented prefix like public/path/solutions/... remains.
- Global search for the old prefix returns zero relevant matches.
- Use short, targeted verification first: search for stale references, confirm the file exists at the new path, and inspect git status/diff before deciding whether heavier checks are necessary.
- npm run test:run (focused or relevant scope) passes when the change touches tested rendering or loaders.
- npm run typecheck passes.
- npm run build passes.
- If PR deploys on Vercel, verify Preview passes after the path move.

Pitfalls
- Misreading a user’s example path as a mandatory literal segment.
- Leaving page-specific JSON, media, or other auxiliary assets in generic shared roots after moving the page’s main images into route-aligned directories.
- Updating content references without moving files, or moving files without updating references.
- Assuming local next build alone proves Vercel will accept the serverless trace size.
- Fixing a deploy-size issue by editing unrelated CMS/API code without first checking whether the user expects a route/content-only solution.
