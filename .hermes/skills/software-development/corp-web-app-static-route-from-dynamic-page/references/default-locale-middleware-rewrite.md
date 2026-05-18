# Default-locale middleware rewrite for route-local pages

Use this when a corp-web-app public English canonical URL should remain unprefixed, but the implementation should live only under `src/app/[locale]/<path>/...`.

## Public URL policy

- English canonical: unprefixed, e.g. `/plans`, `/plans/aip`, `/company/contact-us`.
- Non-English canonical: locale-prefixed, e.g. `/ko/plans`, `/ja/plans`.
- Direct `/en/...` routes may still render through `src/app/[locale]/...`, but they are not necessarily the English canonical URL.

## Runtime routing pattern

- `/plans` for EN or `force_en_locale=1` users: middleware rewrites internally to `/en/plans`; browser URL remains `/plans`.
- `/plans` for KO/JA users: middleware redirects to `/ko/plans` or `/ja/plans`.
- `/ko/plans`, `/ja/plans`, `/en/plans`: render `src/app/[locale]/plans/page.tsx` directly.

## Implementation notes from PR 730

1. Add a small allowlist in `src/middleware.ts` for public unprefixed routes whose implementation should be centralized under `[locale]`:
   - `/plans`
   - `/plans/aip`
   - `/plans/acp`
   - `/company/contact-us`
2. Keep the existing non-English redirect branch first.
3. For allowlisted English/default requests, set `request.nextUrl.pathname = `/en${request.nextUrl.pathname}`` before calling `NextResponse.rewrite(rewriteRequest(request).nextUrl)`.
4. Delete redundant unprefixed page/handler entries only when the `[locale]` target exists:
   - `src/app/plans/page.tsx`
   - `src/app/plans/aip/page.tsx`
   - `src/app/plans/acp/page.tsx`
   - `src/app/company/contact-us/route.ts`
5. Adjust English metadata/canonical in the `[locale]` pages so `Locale.EN` returns the unprefixed canonical path (`/plans`, `/plans/aip`, `/company/contact-us`) even though the runtime path is internally `/en/...`.
6. For page-level legacy query redirects after middleware rewrite, strip internal `baseUrl` from the redirect target.
   - Example: rewritten `/en/plans?acp&baseUrl=...` should redirect to `/plans/acp`, not `/en/plans/acp` and not include `baseUrl`.
7. Update middleware tests to assert both:
   - EN unprefixed rewrite has no `location` and has `x-middleware-rewrite` pointing to `/en/...`.
   - KO/JA unprefixed requests still redirect to locale-prefixed public URLs.

## Pitfalls

- Do not globally rewrite every unprefixed route to `/en/...`; many legacy routes still depend on unprefixed `src/app/<path>/page.tsx` or the catch-all dynamic route. Use an allowlist.
- Do not leave route-specific compatibility handlers like `src/app/company/contact-us/route.ts` once middleware owns the unprefixed compatibility behavior.
- Do not let internal `baseUrl` leak into public redirect URLs.
- Do not change the English canonical to `/en/...` unless the public URL policy explicitly changes.
