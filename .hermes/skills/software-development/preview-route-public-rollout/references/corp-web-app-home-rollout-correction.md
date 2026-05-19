# corp-web-app home preview rollout correction

This reference captures a concrete correction pattern for preview-route public rollout work.

## Situation

The user asked to create a PR to publish-rollout the reviewed home page that had been verified under:

- `/ko/t`
- `/{locale}/t`

The route implementation lived under the Next.js App Router preview path:

- `src/app/[locale]/t/page.tsx`
- `src/app/[locale]/t/page.en.tsx`
- `src/app/[locale]/t/page.ko.tsx`
- `src/app/[locale]/t/page.ja.tsx`

## Mistake

The initial implementation added a new public wrapper route:

- `src/app/[locale]/page.tsx`

while leaving the preview route in place and keeping tests that asserted preview canonical metadata such as:

- `canonical: '/ko/t'`

The user corrected this as a guideline violation: rollout should move the existing `page.tsx` files, not add a duplicate route while preserving preview canonical state.

## Corrected pattern

Use `git mv` to move the reviewed route files to the public route:

```bash
git mv 'src/app/[locale]/t/page.tsx' 'src/app/[locale]/page.tsx'
git mv 'src/app/[locale]/t/page.en.tsx' 'src/app/[locale]/page.en.tsx'
git mv 'src/app/[locale]/t/page.ko.tsx' 'src/app/[locale]/page.ko.tsx'
git mv 'src/app/[locale]/t/page.ja.tsx' 'src/app/[locale]/page.ja.tsx'
```

Move the mirrored route test as well:

```bash
git mv 'src/__tests__/app/[locale]/t/page.test.tsx' 'src/__tests__/app/[locale]/page.test.tsx'
```

Then update:

- imports inside the moved `page.tsx` from `./t/page.*` or old preview paths to colocated `./page.*`
- metadata canonical values from `/en/t`, `/ko/t`, `/ja/t` to `/en`, `/ko`, `/ja`
- internal preview-route indexes to remove the promoted page's preview entry
- route-local README/provenance notes to say the preview entrypoint was removed during rollout
- middleware default-locale behavior so exact `/t` no longer rewrites to the removed preview home page; keep `/t/...` subroutes working if they still exist
- production redirects that previously intercepted locale roots, such as `/ja -> external site`, so the new public locale page is actually reachable

For the corp-web-app home rollout, the important middleware distinction was exact `/t` versus `/t/`-prefixed subroutes: exact `/t` should land on the public locale home, but `/t/blog`-style preview subroutes should not be broken by the home-page rollout.

## Verification commands used

Targeted route tests:

```bash
npm test -- --run src/__tests__/app/[locale]/page.test.tsx src/__tests__/app/[locale]/internal/preview/page.test.tsx
```

Test-group mapping check:

```bash
node scripts/ci/assert-test-groups.mjs
```

Diff whitespace check:

```bash
git diff --check
```

Stale contract grep examples:

```bash
git grep "src/app/\[locale\]/t/page\.tsx\|canonical: '/ko/t'\|canonical: '/en/t'\|canonical: '/ja/t'\|Home preview"
```

Also grep middleware/tests for exact `/t` handling and locale-root redirects when promoting a home page:

```bash
git grep "pathname === '/t'\|pathname.startsWith('/t')\|querypie.ai\|/ja"
```

## Durable lesson

For a public rollout, the old preview route should disappear by default. Keeping it is an explicit compatibility exception, not the default rollout behavior.