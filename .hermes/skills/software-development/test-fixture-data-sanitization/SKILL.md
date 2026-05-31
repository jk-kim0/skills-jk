---
name: test-fixture-data-sanitization
description: Sanitize CSV/JSON/test fixture data before committing it, especially contact lists or customer/license exports that may contain email-like values across multiple columns.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [fixtures, CSV, PII, data-sanitization, tests]
    related_skills: [github-pr-workflow, codebase-inspection]
---

# Test Fixture Data Sanitization

Use this skill when adding, trimming, or reviewing fixture files derived from local exports, customer/contact lists, license exports, spreadsheets, CSVs, or other real-ish datasets.

The goal is to preserve the original file shape needed by tests while removing rows or fields that would leak unintended personal/customer data.

## References

- `references/contact-list-csv-email-domain-sanitization.md` — concrete example of filtering by a primary CSV email column, then scanning all cells for residual external email-like values.

## Core workflow

1. Confirm repository state and target branch/worktree rules before writing files.
2. Identify the intended fixture path and the columns that tests actually care about.
3. Preserve the source file format unless the user asks for transformation:
   - keep header order
   - keep delimiter and quoting semantics
   - keep line endings when possible, especially CRLF in CSV exports
   - avoid reserializing CSV with different quoting unless necessary
4. Apply the user's explicit keep/delete rule.
5. Run a broad residual-data scan before committing.
6. Commit and push according to the repository's PR workflow.

## CSV domain/email filtering checklist

When the user says to keep only rows where a specific email column belongs to allowed domains:

1. Filter rows using that exact column first. If the user names both a column label and ordinal position, verify they match before filtering.
   - Example: `requested_by`, 4th column.
2. Do not stop there if the fixture comes from real exports. Scan every cell for email-like strings after filtering.
3. If any email-like value remains outside the allowed domains, report it and either remove the containing rows or redact the specific field according to the user's instruction.
4. Re-run the scan until the count of non-allowed email-like values is zero.

Typical Python probe:

```python
import csv, re
from pathlib import Path

p = Path("front/fixtures/contact-list-example.local.csv")
allowed = {"chequer.io", "querypie.com"}
email_re = re.compile(r"(?i)\\b[A-Z0-9._%+-]+@([A-Z0-9.-]+\\.[A-Z]{2,})\\b")

with p.open("r", encoding="utf-8", newline="") as f:
    rows = list(csv.reader(f))

header = rows[0]
violations = []
for line_no, row in enumerate(rows[1:], start=2):
    for col_idx, value in enumerate(row, start=1):
        col = header[col_idx - 1] if col_idx <= len(header) else f"column_{col_idx}"
        for m in email_re.finditer(value):
            email = m.group(0)
            domain = email.rsplit("@", 1)[1].lower()
            if domain not in allowed:
                violations.append((line_no, col_idx, col, email, domain))

print("non_allowed_email_like_count", len(violations))
for item in violations:
    print(item)
```

## Row removal pattern that preserves line endings

For CSV exports where preserving shape matters, remove whole raw lines instead of round-tripping through `csv.writer` unless you need to change individual fields.

```python
from pathlib import Path

p = Path("front/fixtures/contact-list-example.local.csv")
needle = "external@example.com"
with p.open("r", encoding="utf-8", newline="") as f:
    lines = f.read().splitlines(keepends=True)

kept = [lines[0]]
removed = []
for line_no, line in enumerate(lines[1:], start=2):
    if needle in line:
        removed.append(line_no)
    else:
        kept.append(line)

with p.open("w", encoding="utf-8", newline="") as f:
    f.write("".join(kept))

print("removed_lines", removed)
print("crlf_preserved", all(line.endswith("\r\n") for line in kept))
```

## Verification before final report

Run and report:

- target file path
- remaining data row count
- primary filter column and allowed domains
- count of residual email-like values outside allowed domains
- whether line endings/format were preserved when relevant
- `git diff --check`
- PR branch/head SHA and CI run state if you pushed

## Pitfalls

- Do not assume the primary email column is the only place email addresses appear. Real exports may place email-like strings in `name`, organization, notes, or raw metadata columns.
- If another column such as `issued_by` contains an internal service email in every row, using "any allowed email in row" as the keep rule will fail to delete external rows. Use the user's named/ordinal column for row eligibility, then scan all cells for residual leaks.
- Do not commit source exports directly if the user asked for a filtered fixture; create a sanitized fixture file under the repo's fixture directory.
- Do not add broad `.gitignore` rules for new fixture paths unless the repo policy explicitly calls for ignoring generated files.
- If a fixture-only update is made on an existing PR branch and latest `origin/main` has advanced, rebase may surface unrelated conflicts. Resolve them by preserving latest main's UI/contract changes plus the PR's intended feature changes, then verify the fixture-specific sanitization again before pushing.
