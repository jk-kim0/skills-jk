# Press release subtitle MDX formatting

Use this pattern when a news/press-release MDX record has a short two-line subtitle or emphasized deck immediately after frontmatter that should be visually centered and italic, but should not appear in the page table of contents or semantic heading outline.

## Trigger

- The copy is a press-release subtitle/deck, not a section title.
- Existing content is incorrectly written as consecutive `##` headings at the top of `src/content/news/<id>-<slug>.{locale}.mdx`.
- The same treatment should apply across localized EN/KO/JA records.

## Pattern

Replace the heading lines with an MDX block like:

```mdx
<Box center>
  <p style={{ textAlign: 'center' }}>
    <em>
      First subtitle line
      <br />
      Second subtitle line
    </em>
  </p>
</Box>
```

Why this shape:

- `<Box center>` matches the existing publication MDX component convention.
- `textAlign: 'center'` centers the text itself, not only the wrapper width.
- `<em>` preserves the editorial intent as italic emphasis.
- Avoiding `##` prevents the subtitle from being treated as a section heading or TOC entry.

## Verification

- Check each localized file for the same structural treatment.
- Confirm the intro area no longer contains unintended `##` headings before the first body paragraph.
- For this user's repo-work preference, avoid local build/test unless explicitly requested; commit and push the focused content change, then report PR head/check status if available.
