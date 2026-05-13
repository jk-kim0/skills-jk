---
name: marketing-typography-token-standardization
description: Standardize marketing-page body/lead typography with shared tokens while deliberately separating typography from layout overrides, and optionally stripping local spacing/width classes when the user wants to review the pure common style.
---

# Marketing typography token standardization

Use this when multiple marketing/static-page components have drifted body or lead text styles and need a common baseline.

## Goal

Create or apply a shared typography token for explanatory marketing copy without accidentally bundling layout decisions into the token.

Typical targets:
- lead paragraphs under page titles
- intro/body copy blocks on static marketing pages
- shared page-section components reused across routes

## Core rule

Separate these concerns:
- typography token = font size, line height, color, weight
- local layout override = max width, top margin, alignment, surrounding spacing

Do not hide layout overrides inside a typography token.

Good:
- `marketingBodyTextClassName = "text-[15px] leading-7 text-slate-600"`
- component adds `mt-5` or `max-w-[680px]` only when that local layout is intentionally part of the reviewed outcome

Bad:
- token includes page-specific margin/width
- leaving stray local overrides in place when the user explicitly wants to inspect the pure common style

## Default workflow

1. Inventory the current variants.
   - Identify current font size, line height, color, weight, tracking.
   - Separate true typography drift from spacing/width drift.
2. Choose the shared baseline.
   - For corp-web-japan marketing descriptive copy, a common baseline may be `15px / 28px / text-slate-600` when consistent with current site defaults.
3. Introduce a small shared token file.
   - Prefer a simple class-name export over a new wrapper component when semantic section components already exist.
4. Patch target components to use the shared token.
5. Decide whether local extra classes stay.
   - Keep `mt-*`, `max-w-*`, etc. if the task is only typography unification.
   - Remove those extra classes if the user asks to review the pure common setting itself.
6. Verify the diff is scoped.
   - Confirm only intended targets changed.
   - Use a light check like `git diff --check` if broader local verification is intentionally out of scope.

## User-preference lesson

When the user asks to "apply the common setting" and says they will review whether it is appropriate, treat that as a request to expose the pure shared style. In that case, remove extra per-component layout classes from the named target components instead of preserving them by default.

## Reporting template

Explain each changed class in two buckets:
- shared typography token: what text properties it standardizes
- retained/removed local overrides: margin, max width, alignment, and why they stayed or were removed

## Pitfalls

- conflating typography consistency with section spacing consistency
- putting margin/width into a shared token and reducing reuse
- claiming a width or margin was introduced by the standardization when it actually pre-existed
- preserving local overrides when the user explicitly wants to inspect the common style alone

## References

Add session-specific measurements, before/after inventories, or page-family notes under `references/` when the rollout spans many routes.
