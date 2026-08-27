# External-model exclusion

## Binding rule

Every asset inside a directory named `external`, `external_models`, or equivalent external subtree is a download of unknown source for this review. It is **excluded from the product portfolio**, cannot be used as a product, derivative, reference master, render, fit body, or bundled file, and cannot be used to claim that a product exists.

This is a stronger rule than “license review pending.” Re-entry requires a separate, documented source acquisition and explicit business decision; the current copies remain excluded.

## Excluded product-source directories

- `research/third-party/art-models`
- `products/toys-games/mm-toy-001-rubber-ball-toy-popper/external`
- `research/third-party/boats`
- `products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/external`
- `products/printer-workshop/mm-tool-003-kobra3max-camera-arm/external`
- `research/third-party/clips/external`
- `research/third-party/dough-cutters/external`
- `research/third-party/fidgets/external`
- `research/third-party/gravity-knife-fidgets/external`
- `research/third-party/music-boxes/external`
- `research/third-party/organization-storage`
- `research/third-party/puzzles`
- `research/third-party/shoes/external`
- `research/third-party/stamps/external`
- `products/organization-storage/mm-wall-001-honeycomb-wood-wall-shelf/external`

Directories named `external` inside installed Python dependencies are not product assets and are ignored by the product inventory.

## Enforcement

- The workbook contains these paths only on the `External Exclusions` sheet, never as portfolio candidates.
- Future inventory scripts must prune all external-named subtrees before classifying models.
- Shop ingestion must accept only files referenced by an approved release manifest; it must never crawl the workspace.
- Provenance review of a non-external folder is still required. For example, a folder named `FROM_ORIGINAL_MODEL` is blocked until the original source and commercial rights are documented even though it is not under `external`.
