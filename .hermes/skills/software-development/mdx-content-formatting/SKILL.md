---
name: mdx-content-formatting
description: Format MDX content files consistently across a repository, covering frontmatter style, prose layout (one sentence per line), embedded JSX indentation, and CJK-aware punctuation handling.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# MDX Content Formatting

Use when normalizing, refactoring, or reviewing the formatting style of MDX files that contain frontmatter, prose paragraphs, or embedded JSX blocks.

Typical triggers:
- A PR review asks to “format this MDX file consistently”
- Bulk migration of MDX content from upstream where formatting is inconsistent
- Adding or updating repo guidance about MDX authoring conventions
- A user expresses a preference about MDX formatting (blank lines after frontmatter, sentence-per-line layout, table indentation, etc.)

## Guiding principle

Formatting changes should never alter rendered output.
They affect only:
- blank-line placement
- line breaks inside prose
- indentation inside JSX blocks

If a formatting change could change how the page renders, it is not a formatting change — treat it as a content edit and get explicit confirmation.

---

## Rule 1: Frontmatter

### Blank line after the closing `---`

Always keep one blank line between the frontmatter closing `---` and the first body element (heading, paragraph, JSX block, etc.).

Preferred:
```mdx
---
id: "17"
title: "Some Title"
---

# First Heading
```

Avoid:
```mdx
---
id: "17"
title: "Some Title"
---
# First Heading
```

This applies to every MDX file with YAML frontmatter, regardless of locale.

### Why
- The blank line creates a clear visual boundary between metadata and content
- Many parsers and human readers treat the first line after `---` as potentially continued frontmatter when there is no blank line
- Consistency across all locale variants (en, ko, ja) reduces review friction

---

## Rule 2: Prose — one sentence per line

Inside standard Markdown paragraphs (outside JSX blocks, outside code fences), keep one sentence per physical line.

Preferred:
```mdx
First sentence here.
Second sentence here.
Third sentence here.
```

Avoid:
```mdx
First sentence here. Second sentence here. Third sentence here.
```

### Safe splitting rules

1. Skip this rule inside:
   - YAML frontmatter
   - fenced code blocks (```)
   - inline JSX attribute values such as `title="..."` or `description="..."`
2. Do NOT split raw JSX tags themselves:
   - `<Table.Tbody>` — never split into `<Table.` + `Tbody>`
   - `</Table.Td>` — keep intact
3. Do NOT split URLs or Markdown links:
   - `https://example.com/path` must stay on one line
   - `[text](https://example.com/path)` must stay on one line
4. Do NOT split dotted identifiers or file extensions:
   - model IDs like `anthropic.claude-sonnet-4-...`
   - file paths like `image.png`, `document.pdf`
5. CJK text handling:
   - Japanese/Korean sentences may end with `。`, `！`, `？` without a following space
   - A splitter that only looks for punctuation + ASCII whitespace will miss CJK boundaries
   - Treat any of `。！？` as sentence terminators even if the next character is not a space
6. Blockquote prefixes:
   - If a line starts with `>`, continuation lines that belong to the same quote block should keep the `>` prefix
7. List markers:
   - Lines like `1. ...` or `- ...` already carry a marker; the first sentence of a list item may need special care

### Practical automation guidance

If scripting the refactor, the script should:
1. Read the file line-by-line
2. Skip frontmatter
3. Skip code fences
4. Leave lines untouched when they contain:
   - JSX tag-only structure
   - URLs
   - markdown-link destinations
   - attribute assignments such as `filepath=` or `src=`
5. Optionally split plain text inside one-line text containers such as:
   - `<Table.Td>Sentence one. Sentence two.</Table.Td>` — only if there are no nested tags inside
6. Preserve indentation on continuation lines

### Recovery if automation breaks content

1. Revert immediately (`git checkout -- src/content/**`)
2. Tighten the splitter rules
3. Re-run and re-verify representative files before finalizing

---

## Rule 3: JSX block indentation

For embedded JSX blocks such as `<Table>` components, use 2 spaces per nesting level.

Preferred:
```mdx
<Table>
  <Table.Tbody>
    <Table.Tr>
      <Table.Td>Cell content</Table.Td>
    </Table.Tr>
  </Table.Tbody>
</Table>
```

Avoid:
```mdx
<Table>
    <Table.Tbody>
        <Table.Tr>
            <Table.Td>Cell content</Table.Td>
        </Table.Tr>
    </Table.Tbody>
</Table>
```

See `scripts/normalize-table-indentation.py` for a reusable Python script that normalizes `<Table>` block indentation in bulk.

## References

- `scripts/normalize-table-indentation.py` — bulk table indentation normalizer
- `references/table-indentation-script.md` — detailed usage notes (if needed beyond the script docstring)

---

## Verification checklist

After any formatting change:

1. Inspect at least one representative file for each pattern:
   - frontmatter blank line placement
   - a normal prose paragraph (one sentence per line)
   - a numbered/bullet list item
   - a `<Table.Td>` multi-sentence cell
   - a blockquote
   - a references section with full URLs
   - an image component using `filepath="...png"`
2. Search for obvious corruption patterns:
   - `<Table.` or `</Table.` (broken tags)
   - broken `filepath="...` lines
   - split `https://` domains
   - split dotted model IDs
3. Run the narrowest repo tests that cover the affected MDX family
4. Summarize both the content refactor and any policy-doc updates

---

## When to update repo guidance

If the task includes “document this rule in repo guidance”, update:

1. `AGENTS.md` — add under the content-editing section
2. `README.md` — add a short “MDX 작성 규칙” or equivalent section
3. Any design docs in `docs/` that mention MDX file rules

---

## Pitfalls

1. **Formatting is not a content change.** If rearranging whitespace could change rendered output (e.g., inside `<pre>` or inline HTML), get explicit confirmation first.
2. **Locale parity matters.** A formatting change on an EN file should usually be matched on KO and JA variants of the same content to avoid future diff noise.
3. **Don't invent formatting rules the repo doesn't follow.** If the repo already has a stable formatter or lint rule, prefer that over ad-hoc manual formatting.
4. **Frontmatter delimiters are structural.** Never add or remove blank lines inside frontmatter itself — only between the closing `---` and the body.
