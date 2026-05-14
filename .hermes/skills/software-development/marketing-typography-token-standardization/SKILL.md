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

## Lists and checklist-style body copy

When a page mixes ordinary body paragraphs with short checklist or bullet guidance (for example `contact-us` support bullets), do not leave the list on a smaller or lighter ad hoc text style if the user's goal is cross-page text consistency.

Preferred pattern:
- apply the same shared body typography token to the `ul`/`ol` itself
- use real list semantics (`list-disc`, `list-decimal`, marker utilities, padding) instead of hardcoded leading characters like `"• "`
- keep marker styling close to the body text color unless there is an explicit design exception

Why:
- manual bullet characters make spacing and wrapping inconsistent
- ad hoc `text-sm` lists can visually break the intended company-page body-text baseline
- shared paragraph/list typography makes pages like `about-us`, `certifications`, `news`, and `contact-us` feel authored in one system

Practical example:
- replace `ul` classes like `text-sm leading-6 text-slate-500` plus `li` content prefixed with `"• "`
- with `ul` classes like `list-disc space-y-3 pl-5 marker:text-slate-600` plus the shared body token
- and render plain `{children}` inside each `li`

## Reporting template

Explain each changed class in two buckets:
- shared typography token: what text properties it standardizes
- retained/removed local overrides: margin, max width, alignment, and why they stayed or were removed

## Pitfalls

## Pitfalls

- conflating typography consistency with section spacing consistency
- putting margin/width into a shared token and reducing reuse
- claiming a width or margin was introduced by the standardization when it actually pre-existed
- preserving local overrides when the user explicitly wants to inspect the common style alone
- standardizing only one axis of a page-intro contract and accidentally leaving another axis divergent on one page

## Company-info intro standardization follow-up

When standardizing several company/info pages together (for example `about-us`, `certifications`, `news`, and `contact-us`), do not stop after moving spacing ownership into intro wrappers.

Re-check all of these axes explicitly on every target page:
- GNB/header -> `h1` top spacing
- `h1` -> first descriptive block spacing
- descriptive text typography token (`font-size`, `line-height`, `weight`, `tracking`, `color`)
- descriptive block width policy (`max-w-*` or full intro width)

Important lesson:
- a route can look "standardized" structurally while still violating the intended common contract because one page keeps an older text token such as `marketingBodyTextClassName` or a narrower width like `max-w-[760px]`
- if the user says to use one page as the baseline, treat that as applying to all four axes above unless they explicitly scope it more narrowly

User-specific rule from the company-page intro pass:
- if the user says "use about-us as the baseline" for page-intro commonization, do not leave sibling pages on older `pt-[112px] / lg:pt-[144px]`, `gap-[56px]`, or a page-specific lead token/width just because those values pre-existed
- align `GNB -> h1`, `h1 -> first block`, and lead/body typography-width together, or clearly report any deliberate exception before finalizing

Verification reminder:
- after changing shared page-intro spacing values, search the affected source-based tests for hardcoded old values and update those expectations in the same PR
- otherwise CI can fail even when the runtime code already matches the new contract
- when the user explicitly asks to standardize several pages against one chosen baseline page, do not keep an old page-specific typography or width exception just because that component is not rendered yet or may be used in a future follow-up
- practical example: if a future `Lead` component is being prepared on one page, its definition still needs to adopt the same shared body token and width policy now when the user asked for cross-page standardization; "we will add the lead later" is not a valid reason to leave `text-[15px]` or `max-w-[760px]` exceptions behind

## Cross-page baseline adoption rule

When the user says to use one page as the baseline for several sibling page intros, treat that as a full contract, not just a spacing sample.

Apply the baseline consistently to the relevant intro surfaces:
- title-to-first-block spacing ownership
- spacing value
- lead/body typography token
- width policy for the first descriptive block

Do not standardize only the visible currently-rendered path while leaving a future/optional intro component on an older token or narrower width.
If a page has a prepared-but-not-yet-rendered `Lead` component, update that component too so the next follow-up cannot silently reintroduce a broken exception.

## Reference-page standardization checklist

When the user says to align several pages to one reference page, audit and normalize all applicable axes together for the target surface:
- ownership of spacing
- spacing value
- typography token (`font-size`, `line-height`, `weight`, `tracking`, `color`)
- width policy (`max-w-*` or lack of it)

Do not stop after matching only spacing if another page still keeps a different intro/lead token or a narrower width cap. If a target component is not rendered yet but is being prepared for an upcoming follow-up (for example a lead component on `/news`), align that dormant component to the same contract now so the future feature does not reintroduce the divergence.

## References

Add session-specific measurements, before/after inventories, or page-family notes under `references/` when the rollout spans many routes.
