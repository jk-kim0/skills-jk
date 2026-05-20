# Distinguishing `.hermes/skills/` generated noise from meaningful work

During or between agent sessions, the root working tree can accumulate a large number of `M` (modified) and `D` (deleted) files under `.hermes/skills/`. Before treating this as meaningful local work:

## Quick classification checklist

1. Check whether HEAD is already at `origin/main`:
   ```bash
   git rev-parse HEAD
   git rev-parse origin/main
   ```
2. If they match, check whether there are any ahead commits:
   ```bash
   git diff --stat origin/main..HEAD
   ```
3. If empty, the changes are **uncommitted working tree changes**, not ahead commits.
4. Inspect a sample of the working tree diff to classify:
   - `.bundled_manifest` hash churn alone → generated noise
   - SKILL.md `version:` fields rolling back/forward → generated noise
   - `references/*.md` files deleted that were added in an earlier session → session artifact residue
   - Scripts or references that differ only by formatting or import style → generated noise
5. If the bulk of the diff is generated noise, discard with:
   ```bash
   git restore .hermes/skills/
   ```

## What NOT to do

- Do NOT create a preserve branch for generated skill-library churn.
- Preserve branches should be reserved for intentional human or agent-authored changes (new references, meaningful skill patches, new frontmatter).

## Historical context

This pattern appeared during repeated `workspace 정리` sessions in the `skills-jk` repo, where root `main` showed 60+ modified `.hermes/skills/` files with a net diff of 3,200+ lines. The diff turned out to be entirely generated noise (bundled manifest hash updates, version field rollbacks, and deleted session artifact references). Running `git restore .hermes/skills/` cleanly discarded the noise without losing any authored work.
