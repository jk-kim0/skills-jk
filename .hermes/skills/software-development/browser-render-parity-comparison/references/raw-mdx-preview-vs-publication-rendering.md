# Raw MDX preview vs publication rendering parity pitfall

Session pattern: a migrated verification/detail route looked unlike its live reference because the target page rendered the MDX body as a plain string instead of evaluating MDX and composing the article/publication layout.

Symptoms to check in the browser:

- Literal MDX/JSX tags appear in the page text, e.g. `<Box>`, `<ArticleFileImage>`, `<br />`.
- Markdown links remain `[label](url)` instead of anchors.
- Hero image, body images, TOC, related-post sidebar, share controls, contact CTA, or other downstream article landmarks are missing.
- The target may still show the correct title/description, so heading-only checks can falsely pass.

Source inspection pattern:

1. Inspect the route file for helper names like `renderBodyPreview`, `bodyPreview`, or direct `{post.body}` / `{detail.post.body}` inside text components.
2. Compare against the reference implementation's publication/detail route. A correct implementation usually evaluates MDX with the route's MDX component map, extracts headings/TOC, resolves related records, and renders a publication detail page component.
3. Verify the MDX component map includes the content's custom components (`Box`, `ArticleFileImage`, `ButtonLink`, `Table`, `Link`, etc.) before assuming the content is malformed.
4. Add a regression test that proves literal component tags do not appear and that at least one image/sidebar landmark renders.

Implementation shape that generalized from the session:

- Keep the route file focused on params, locale checks, redirect/notFound handling, metadata, MDX evaluation, TOC/related resolution, and page composition.
- Put the publication detail layout and MDX component map in a colocated component module when the route is still a verification `/t/*` route and no shared global publication detail component exists.
- If related cards depend on `relatedIds`, expose a repository method such as locale-aware `getById` rather than duplicating record scans in the route.
