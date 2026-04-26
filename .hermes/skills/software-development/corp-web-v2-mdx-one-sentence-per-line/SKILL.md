---
name: corp-web-v2-mdx-one-sentence-per-line
description: Safely refactor corp-web-v2 MDX content to one sentence per line and update repo guidance without breaking JSX tags, image paths, model IDs, or markdown links.
---

# When to use

Use this when a corp-web-v2 task asks to normalize `src/content/mdx/**` content so paragraphs use one sentence per line, or when the repo guidance needs to explicitly document that convention.

# Goal

Convert prose in `src/content/mdx/**` to one sentence per line while preserving MDX/JSX correctness.
Also update the repo guidance documents so future edits keep the convention.

# Required repo guidance context

Before editing, read at least:

1. `README.md`
2. `next.config.ts`
3. `src/features/content/config.ts`
4. `src/constants/navigation.ts`
5. `AGENTS.md`

The repo guidance explicitly expects these to be checked first.

# Files that should usually be updated for policy changes

When the task includes “document this rule in repo guidance”, update these:

1. `AGENTS.md`
   - Add the rule under the content-editing section.
2. `README.md`
   - Add a short “MDX 작성 규칙” or equivalent section near the existing workflow/guidance links.
3. `docs/superpowers/specs/2026-04-16-mdx-rendering-design.md`
   - Add the formatting rule near the MDX file rules so the implementation/design doc matches the repository policy.

# Safe editing strategy

Do NOT start with a blind regex replacement across raw MDX.
That breaks JSX and inline URLs surprisingly easily.

Use this order:

1. Inspect a few representative MDX files from:
   - normal paragraphs
   - bullet/numbered lists
   - blockquotes
   - JSX text containers like `<Table.Td>text...</Table.Td>`
   - files with references / markdown links / URLs
2. If doing automation, use a script that skips frontmatter and code fences.
3. Split only prose-bearing lines.
4. Re-check representative files after each pass.
5. If automation corrupts JSX or URLs, immediately revert the MDX tree and retry with narrower rules.

# Important pitfalls discovered

## 1. Never split raw JSX tags themselves

A naive sentence splitter can corrupt things like:

- `<Table.Tbody>` into `<Table.` + `Tbody>`
- `</Table.Td>` into `</Table.` + `Td>`
- attribute values like `filepath="...png"`

Only split text content, not tag names, closing tags, or attribute lines.

## 2. Never split URLs or markdown links

Naive period splitting can break:

- `https://...`
- markdown links like `[text](https://example.com/path)`
- filenames like `.png`, `.pdf`
- model IDs / dotted identifiers like `anthropic.claude-sonnet-4-...`

Treat URLs, markdown-link destinations, file extensions, and dotted IDs as protected tokens.

## 3. Blockquotes need quote prefixes preserved

For lines beginning with `>`, continuation lines should keep the `>` prefix if they remain part of the same quote block.
Do not convert quoted text into plain paragraphs accidentally.

## 4. CJK text may not have spaces after punctuation

Japanese/Korean sentences may continue immediately after `。`, `！`, `？` without a space.
A splitter that only looks for punctuation + whitespace will miss many real sentence boundaries.

## 5. Numbered lists are ambiguous

Lines like `1. ...` contain a period that is not a sentence boundary.
Protect the list marker before sentence splitting.

# Practical automation guidance

If scripting the refactor, the script should:

1. Skip YAML frontmatter.
2. Skip fenced code blocks.
3. Leave lines untouched when they contain:
   - JSX tag-only structure
   - URLs
   - markdown-link destinations
   - image/file extensions in attributes
   - attribute assignments such as `filepath=` or `src=`
4. Optionally split plain text inside one-line text containers such as:
   - `<Table.Td>Sentence one. Sentence two.</Table.Td>`
   but only if the open tag, text, and close tag are all on one line and the text body contains no nested tags.
5. Preserve indentation on continuation lines.

# Verification checklist

After editing:

1. Inspect at least these patterns again with `read_file`:
   - a normal prose paragraph
   - a numbered list item
   - a `<Table.Td>` multi-sentence cell
   - a blockquote
   - a references section with full URLs
   - an image component using `filepath="...png"`
2. Search for obvious corruption patterns, for example:
   - `<Table.`
   - `</Table.`
   - broken `filepath="...` lines
   - split `https://` domains across lines
   - split dotted model IDs
3. Run `git diff --stat` to confirm scope.
4. Summarize both the content refactor and the policy-doc updates.

# Recovery strategy if automation goes wrong

If the first scripted pass breaks JSX/URLs:

1. Revert the MDX tree immediately, e.g. `git checkout -- src/content/mdx`
2. Tighten the splitter rules.
3. Re-run on the MDX tree.
4. Re-verify representative files before finalizing.

# Expected outcome

- MDX prose under `src/content/mdx/**` is reformatted to one sentence per line.
- JSX structure, image paths, links, references, and identifiers remain intact.
- `AGENTS.md`, `README.md`, and the MDX rendering design doc all explicitly state the one-sentence-per-line rule.
