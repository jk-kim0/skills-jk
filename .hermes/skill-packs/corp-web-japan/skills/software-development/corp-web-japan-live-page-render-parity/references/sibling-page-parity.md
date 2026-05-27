# Sibling-page layout parity in corp-web-japan

Use this note when the user asks one corp-web-japan page to look like another already-good local/published sibling page, rather than comparing to the upstream QueryPie live site.

## Pattern

1. Treat the named sibling page as the reference contract for the requested surface.
2. Open/measure both exact URLs under the same deployment when available, for example:
   - reference: `https://stage.querypie.ai/platforms/aip/usage-based-llm`
   - target: `https://stage.querypie.ai/t/platforms/aip/mcp-gateway`
3. Capture DOM geometry and computed styles for:
   - `h1`
   - lead paragraph
   - hero media
   - first content heading
   - first few section wrappers
4. Compare `top`, `height`, `fontSize`, `lineHeight`, `paddingTop`, `paddingBottom`, and `marginTop` before changing CSS.
5. Inspect the reference page's section primitives and prefer reusing its page shell/content-section rhythm rather than inventing route-local offsets.

## Concrete lesson from MCP gateway vs usage-based LLM

The visual mismatch was not primarily font size. The target page had extra nested hero copy padding:

- reference hero section: `PlatformContentSection` with `pt-[134px] lg:pt-[144px]`, `pb-[120px]`, content width `max-w-[1200px]`
- target had outer hero `pt-[75px]` plus child copy `pt-[55px] lg:pt-[167px]`

That pushed the mcp-gateway title/lead down relative to usage-based-llm even though the typography looked similar. Fix by moving the target to the same shell/content-section contract, removing the child top padding, aligning hero title width and hero image `mt-[80px]`, and updating mirrored source tests to forbid the removed offsets.

## Test guidance

For these small layout-parity fixes, add/update the mirrored source test for the target route so it pins:

- the shared page shell/content section primitive
- the reference-matched hero padding and width tokens
- the absence of the stale extra padding offsets
- the route's authored copy staying in `page.tsx`

Prefer narrow source tests plus CI/preview over starting a local dev server unless the user explicitly asks for local browser verification.
