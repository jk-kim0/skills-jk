# Migrated memory and user context for querypie-docs

These entries were moved out of global Hermes memory/user profile because they are repository- or platform-specific. Keep them here or split them into narrower workflow skills as they evolve.


## From MEMORY.md


### MEMORY entry 1

In querypie-docs, confluence-mdx is a Python-based bidirectional Confluence↔MDX pipeline. Main forward flow: bin/fetch_cli.py (Confluence API/local cache -> var/) -> bin/convert_all.py (batch over var/pages.<sync_code>.yaml) -> bin/converter/cli.py (single-page XHTML -> MDX, generates mapping.yaml and _meta.ts).


### MEMORY entry 2

In querypie-docs confluence-mdx, important data directories are var/ and cache/. var/ is the active working dataset with one directory per Confluence page_id plus pages.qm.yaml catalog and reverse-sync artifacts; each page directory commonly contains page.v1.yaml, page.v2.yaml, children.v2.yaml, attachments.v1.yaml, page.xhtml/html/adf, and mapping.yaml. cache/ mirrors page-level source data for reuse when fetching attachments/content.


### MEMORY entry 3

In querypie-docs confluence-mdx, reverse sync is centered on bin/reverse_sync_cli.py plus bin/reverse_sync/*. It diffs original vs edited MDX, maps changes back to XHTML using sidecar mapping.yaml, writes reverse-sync.* artifacts under var/<page_id>/, forward-converts patched XHTML to verify.mdx, and validates round-trip before optional Confluence push. docs/architecture.md and docs/analysis-reverse-sync-refactoring.md document this as a major, actively evolving subsystem.


### MEMORY entry 4

In querypie-docs confluence-mdx, container usage is standardized through compose.yml and scripts/entrypoint.sh. The container exposes fetch_cli.py, convert_all.py, converter/cli.py, full, full-all, and status commands; it mounts ../src/content/{ko,en,ja} and ../public onto target/ symlink destinations, and uses ATLASSIAN_USERNAME plus ATLASSIAN_TOKEN from .env/environment for API access.


### MEMORY entry 5

In querypie-docs confluence-mdx reverse_sync, build_patches in bin/reverse_sync/patch_builder.py is the main decision engine: it classifies each MDX block change into direct/containing/list/table/skip, relies on sidecar lookup plus roundtrip sidecar v3 identity fallback, and produces modify/delete/insert/replace_fragment patches while collecting skipped_changes reasons like no_mapping, missing_roundtrip_sidecar, preserved_anchor_table, and unsafe_html_table_edit.


### MEMORY entry 6

In querypie-docs confluence-mdx reverse-sync planning, the user considers current table support sufficient for now; prioritize verifier-side handling so whitespace differences or column-width-only differences are treated as matches rather than mismatches.


### MEMORY entry 7

In querypie-docs confluence-mdx reverse-sync planning, the user supports using planner / strategy / proof as the main axis for codebase cleanup and architectural reorganization.


### MEMORY entry 8

In querypie-docs confluence-mdx reverse-sync planning, treat `tests/reverse-sync/pages.yaml` as straightforward and non-core: in real-data usage it is just a reference metadata catalog for reverse-sync, and extra fields exist only for testcase implementation; do not overcomplicate its role.


### MEMORY entry 9

In querypie-docs confluence-mdx reverse-sync planning, the user prefers verifier taxonomy to be classified in more detail.


## From USER.md


### USER entry 1

For confluence-mdx reverse-sync work, the user prefers two separate PRs in sequence: first update docs to reflect the current implementation state, then open a separate Draft PR for a new replacement plan document and refine that plan through review.


### USER entry 2

For querypie-docs reverse-sync discussions, the user values checking whether design concepts are actually reflected in current implementation and whether terminology is used consistently across code and docs.
