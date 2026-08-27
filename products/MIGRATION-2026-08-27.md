# Product-folder migration — 2026-08-27

## Result

- Every product is contained in one product folder beneath `products/<family>/`.
- The seven family folders contain product folders and a family README only; they do not own shared source, assets, exports, or validation artifacts.
- All 58 registered portfolio products have an existing product root and model-evidence file inside that root.
- Seven concepts that do not yet have registered SKUs are retained as `unregistered-*` product folders.
- Repository-level reusable material is limited to `templates/`, `tools/`, `libraries/`, `research/`, `business/`, and `archive/`.
- Historical product revisions remain inside their product folder under `history/`; the active revision is under `current/` where revision separation is needed.

## Verification performed

- Product-layout validation: PASS — 7 families, 65 product folders, 58 registered products, 7 unregistered concepts, 0 warnings, 0 errors.
- Portfolio model audit: PASS — 58 records, 58 models, 0 missing files, 0 contradictions.
- Portfolio workbook ZIP/XML integrity: PASS.
- Flapping-submarine regression suite: PASS — 21 tests.
- Python compilation checks for the migration tools and business audit tools: PASS.
- Git whitespace/error check: PASS.
- Representative ShelfFit validation: artifact hashes, mesh checks, 3MF checks, and external reports pass. Its path-bound approval ledger no longer validates because migration edits changed evidence files and therefore their hashes. Existing approval records were intentionally not regenerated or rewritten.

## Open release gates

- Products with approval ledgers must receive fresh provenance/interface approval evidence after review of their relocated files.
- Physical test and exact-slicer gates remain review-required wherever their validation manifests say so.
- No product should be treated as newly release-ready solely because of this repository migration.

## Version-control handoff

The migration is not staged or committed. Until `git add -A` is run, Git reports old paths as deleted and the new `products/` tree as untracked instead of displaying rename detection. Local virtual environments, dependency directories, and caches remain on disk where moved but are excluded by the repository ignore rules.
