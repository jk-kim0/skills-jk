# Skill pack split measurement

Measured after moving repo-specific skills for `corp-web-japan`, `corp-web-app`, `corp-web-v2`, and `querypie-docs` out of active `.hermes/skills/` into inactive `.hermes/skill-packs/`.

## Counts

- Baseline active skills before split: 294
- Moved repo-specific skills: 98
  - corp-web-japan: 69
  - corp-web-app: 13
  - corp-web-v2: 14
  - querypie-docs: 2
- Thin active pack entrypoint skills added: 4
- Active `.hermes/skills/**/SKILL.md` after split: 200
- Inactive `.hermes/skill-packs/**/SKILL.md`: 98

`HERMES_HOME=<worktree>/.hermes hermes skills list` produced 207 output lines, consistent with the 200 active skill files plus table/header lines. Skills under `.hermes/skill-packs/` were not counted as active skills.

## Index token estimate

The estimate uses a `name: description` line per active skill and `tiktoken` `cl100k_base` as a stable rough tokenizer. It is not the exact provider tokenizer, but it is useful for before/after comparison.

- Baseline reconstructed index: 13,782 tokens estimated
- Active index after split: 8,485 tokens estimated
- Estimated reduction: 5,297 tokens
- Baseline reconstructed index characters: 55,127
- Active index characters after split: 33,939

The absolute number differs from the live Kimi/Hermes prompt-size probe, but the relative result confirms that removing 98 repo-specific skills from active discovery materially shrinks the default skills index.
