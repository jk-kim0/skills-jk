# Migration provenance README for route-local/static page migrations

Use this when a corp-web-app static/semistatic page is migrated from corp-web-contents, corp-web-japan, or historical source content into route-local `page.{locale}.tsx` files.

## When to create it

Create a maintainer-facing README when any of these are true:

- MDX source is converted into route-local TSX authoring files.
- Source content lives in a different repo, deleted tree, historical commit, archive, or other non-obvious place.
- Source path and target path are not a simple 1:1 move.
- Assets are relocated to route-aligned `public/**` paths.
- Future copy/metadata/asset fixes will likely need the original source path, source commit, or recovery commands.

## Where to put it

Colocate the README with the migrated page authoring files, not in a stale source-style directory and not only in broad `docs/**`.

For route-local page migrations, put it next to:

```text
src/app/<target-route>/page.en.tsx
src/app/<target-route>/page.ko.tsx
src/app/<target-route>/page.ja.tsx
src/app/<target-route>/README.md
```

If locale route entry wrappers live elsewhere, document them inside the colocated README, but keep the README beside the shared locale authoring files.

Example shape from the why-querypie ACP migration:

```text
src/app/archived/why-querypie-acp/README.md
src/app/archived/why-querypie-acp/page.en.tsx
src/app/archived/why-querypie-acp/page.ko.tsx
src/app/archived/why-querypie-acp/page.ja.tsx
```

## Minimum content

Include:

- Source repository and source paths.
- Source commit or historical lookup basis when the source is no longer on main.
- Original public URI path and new target URI path.
- Target implementation paths and locale authoring files.
- Metadata/frontmatter migration approach.
- MDX component or legacy component mapping to TSX composition.
- Asset source paths, target public paths, and image/PDF/link rewrites.
- Exact commands to re-open source content from history.
- Scope boundaries and follow-up cautions for future edits.

## Pitfalls

- Do not put the README in a removed legacy route directory just because that was the old source name.
- Do not treat this as customer-facing website copy.
- Do not use broad docs-only placement as the only provenance record when the page files themselves need local context.
- Keep the README concise and operational; it is for future maintainers fixing the migrated page.
