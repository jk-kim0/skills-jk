---
name: corp-web-japan-contact-us-preview-form
description: Implement a local /t/contact-us preview form in corp-web-japan while keeping the public /contact-us redirect unchanged until rollout.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, contact-us, preview, nextjs, salesforce, query-prefill]
---

# corp-web-japan contact-us preview form

Use this when the user wants local contact-us form functionality implemented in `corp-web-japan`, but does **not** want to open it on the public `/contact-us` route yet.

## Goal

Implement the form on an isolated preview path such as:
- `/t/contact-us`

while keeping:
- existing `/contact-us` redirect behavior unchanged
- stable CTA query-string prefills working (`inquiry`, repeated `product`)
- rollout safety for environments that do not yet have upstream submission secrets configured

## Proven approach

### 1. Keep `/contact-us` redirect-only

Do not modify:
- `src/app/contact-us/route.ts`

This route should continue to 307 redirect to the Japan contact page and preserve the query string.

Reason:
- the user explicitly wanted the current redirect behavior preserved until the new implementation is sufficiently tested

### 2. Add a separate preview page under `/t/contact-us`

Create:
- `src/app/t/contact-us/page.tsx`

Recommended page behavior:
- render a local form UI
- set `robots.index = false` and `robots.follow = false`
- use canonical `/t/contact-us`
- keep the existing site header/footer for realistic validation

### 3. Put form option definitions and query-prefill helpers in a shared lib

Create a repo-local helper like:
- `src/lib/contact-us.ts`

Include:
- form state type
- inquiry options using stable keys
- product options using stable keys
- `getPrefilledContactUsFormState(searchParams)`
- submit body builder for the Salesforce-style upstream request
- client/server shared validation helper

Recommended stable inquiry keys:
- `ai-consulting`
- `download`
- `demo-request`
- `quote-request`
- `technical-question`
- `partnership`
- `other`

Recommended stable product keys:
- `ai-crew`
- `ai-dashi`
- `aip`
- `acp`
- `fde`
- `partnership`

Important:
- store keys in the URL/query layer
- convert keys to Japanese labels only when building the upstream request body

### 4. In Next.js App Router, do prefill resolution on the server page, not with `useSearchParams()` in the client form

Initial attempt using `useSearchParams()` inside the client form caused build issues:
- `useSearchParams() should be wrapped in a suspense boundary at page "/t/contact-us"`

A follow-up effect-based sync also triggered lint failure:
- `react-hooks/set-state-in-effect`

Working fix:
- let `page.tsx` accept `searchParams`
- convert them into `URLSearchParams`
- call `getPrefilledContactUsFormState(urlSearchParams)` on the server
- pass the result to the client form as `initialPrefills`

Pattern:

```tsx
type PageProps = {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

export default async function ContactUsPreviewPage({ searchParams }: PageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const urlSearchParams = new URLSearchParams();

  for (const [key, value] of Object.entries(resolvedSearchParams)) {
    if (Array.isArray(value)) value.forEach(item => urlSearchParams.append(key, item));
    else if (typeof value === 'string') urlSearchParams.set(key, value);
  }

  const initialPrefills = getPrefilledContactUsFormState(urlSearchParams);

  return <ContactUsPreviewForm initialPrefills={initialPrefills} />;
}
```

This avoids both:
- suspense bailout build failure
- setState-in-effect lint failure

### 5. Keep the preview form client-side, but isolated

Create a dedicated client component such as:
- `src/components/sections/contact-us-preview-form.tsx`

Recommended behavior:
- initialize form state from `initialPrefills`
- keep Japanese labels consistent with the upstream JP contact form
- disable submit until required fields are valid
- POST to a preview-only submit endpoint such as `/t/contact-us/submit`

### 6. Add a preview-only submit endpoint with graceful degradation

Create:
- `src/app/t/contact-us/submit/route.ts`

Recommended behavior:
- validate request body shape minimally
- require the local form fields to be valid
- read `process.env.SALESFORCE_ENDPOINT`
- if missing, return `503` with a clear preview-stage message
- if present, POST a Salesforce-style payload and require `recordUUID` in the upstream response

Important lesson:
- this repo did **not** already contain the full `corp-web-app` server action stack or its secrets wiring
- copying the whole `corp-web-app` form system would have been unnecessarily large and brittle
- a thin repo-local route is the safer migration step

Recommended graceful-degradation message:
- explain that the preview route is implemented but the upstream endpoint is not configured in the current environment yet

### 7. Build the upstream body in the same shape as the corp-web-app integration pattern

Useful conventions copied from the working upstream pattern:
- top-level `processType: "LEAD_MS"`
- `requestBody` object
- convert `Objective__c` from stable key -> localized JP label
- put selected products and implementation timeline into `Description`
- use `Referrer_URL__c`
- use `HasOptedInMarketing__c`

This keeps the preview path compatible with the likely future production integration shape.

### 8. Add repo-local regression tests focused on isolation and prefill behavior

Add a node test such as:
- `tests/contact-us-preview-route.test.mjs`

Recommended assertions:
- `/t/contact-us` page is `noindex`
- canonical is `/t/contact-us`
- page uses local preview form component
- stable query keys exist in the helper
- form submits to `/t/contact-us/submit`
- submit route checks `process.env.SALESFORCE_ENDPOINT`
- submit route expects upstream `recordUUID`

These tests can remain string-based and lightweight, consistent with the repo’s existing test style.

## Verification steps that worked

Run from the worktree:

```bash
npm run test:ci
npm run build
```

Do not start local preview by default for this user.

Important user/environment finding:
- local dev servers consume too many resources in this environment and interfere with work
- prefer PR + Preview Deployment validation over local `npm run dev`
- only start a local dev server if the user explicitly instructs it

If the user explicitly asks for local verification, then use:

```bash
npm run dev
```

Useful browser checks when local verification is explicitly requested:
- `http://localhost:3003/t/contact-us`
- `http://localhost:3003/t/contact-us?inquiry=demo-request&product=ai-dashi&product=aip`

Expected browser result for the second URL:
- inquiry select prefilled to `デモを依頼`
- product checkboxes for `AI Dashi` and `AIP` checked

## Pitfalls found

1. `useSearchParams()` in the preview page path triggered a build-time suspense requirement.
   - Do not keep prefill resolution purely in the client unless you intentionally wrap the page with suspense.
   - Server-side `searchParams` handling was cleaner here.

2. Syncing prefills with `setState()` in `useEffect()` triggered `react-hooks/set-state-in-effect` lint errors.
   - Prefer server-derived initial state props instead.

3. This repo may not have `node_modules` installed yet.
   - `npm run test:ci` and `npm run build` can fail with `command not found` for `eslint`/`next` until dependencies are installed.
   - Installing once at the repo root may be enough for worktree verification.

4. `npm run test:ci` can still print unrelated existing warnings.
   - Example observed: an existing `@next/next/no-img-element` warning in `src/components/sections/zoomable-figure.tsx`.
   - If there are no errors, this does not block the feature work.

5. Browser verification is useful here because checkbox/select prefill correctness is easiest to confirm visually.

## Done criteria

- `/contact-us` still redirects unchanged
- `/t/contact-us` renders a working local preview form
- stable `inquiry` and repeated `product` query prefills work
- preview submit endpoint exists and degrades safely when upstream env is absent
- `npm run test:ci` passes
- `npm run build` passes
- browser verification confirms rendered form and prefill behavior
