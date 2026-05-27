# Legal MDX source-formatting cleanup notes

Session-derived notes from refactoring corp-web-japan legal MDX after comparing local legal files with `../corp-web-contents`.

## Scope to classify as legal MDX
- Single-version adjacent legal pages: `src/app/t/eula/content.mdx`, `src/app/t/terms-of-service/content.mdx`.
- Multi-version legal collections: `src/content/privacy-policy/*.mdx` rendered through the legal document body primitives.
- Source comparison targets in `../corp-web-contents`: `pages/eula/en/content.mdx`, `pages/terms-of-service-*/en/content.mdx`, and `pages/privacy-policy-{en,ko}/*/en/content.mdx`.

## Source artifacts to remove or normalize
- Wrapper-only layout components from old MDX stacks, especially `Box` and `CenterSection`, should not remain in legal MDX bodies.
- Headings should start at column 1. Remove wrapper-era leading spaces before `#` headings.
- Paragraph-spacing `<br />` outside table cells should be replaced with normal Markdown blank lines.
- JSX string expressions used only for plain text table-cell children, e.g. `{'Purpose of collection'}`, should become ordinary text nodes.
- Long prose in JSX table cells can be wrapped across lines at word boundaries; JSX collapses whitespace in text nodes.

## What to keep
- `Table` / `Table.*` components are acceptable when they represent legal table content, cell styling, spans, or structured rendering that plain Markdown cannot express safely.
- `<br />` may remain inside `Table.Td` / `Table.Th` when it is the least risky way to preserve a cell-internal line break.
- Nested Markdown lists must retain valid indentation; do not flatten nested bullets or numbered subitems during cleanup.

## Verification pattern
Add or update a source-structure test that iterates all legal MDX files and asserts:
- no heading line matches `/^[ \t]+#{1,6}\s/m`
- no wrapper-only components such as `<Box` or `<CenterSection`
- no `<br />` outside `Table.Td` / `Table.Th`
- no plain-text-only JSX string-expression lines matching `/^\s*\{["'][^{}<>]+["']\}\s*$/m`

Pitfall: do not use `/^\s+#{1,6}\s/m` for heading indentation. `\s` can cross a newline and falsely match a normal heading after a blank line. Use `[ \t]` for same-line indentation checks.

Run at least the static page/source tests that include legal routes plus `git diff --check` after mechanical MDX rewrites.
