# External-model exclusion

## Binding rule

Every asset inside a directory named `external`, `external_models`, or equivalent external subtree is a download of unknown source for this review. It is **excluded from the product portfolio**, cannot be used as a product, derivative, reference master, render, fit body, or bundled file, and cannot be used to claim that a product exists.

This is a stronger rule than “license review pending.” Re-entry requires a separate, documented source acquisition and explicit business decision; the current copies remain excluded.

## Excluded product-source directories

- `art/external_models`
- `blasters/external`
- `boats/external`
- `bowls/external`
- `camera_mount/external`
- `clips/external`
- `dough_cutter/external`
- `fidgets/external`
- `gravity_knife/external`
- `music/external`
- `organizer/external`
- `puzzles/external`
- `shoes/external`
- `stamps/external`
- `walls/external`

Directories named `external` inside installed Python dependencies are not product assets and are ignored by the product inventory.

## Enforcement

- The workbook contains these paths only on the `External Exclusions` sheet, never as portfolio candidates.
- Future inventory scripts must prune all external-named subtrees before classifying models.
- Shop ingestion must accept only files referenced by an approved release manifest; it must never crawl the workspace.
- Provenance review of a non-external folder is still required. For example, a folder named `FROM_ORIGINAL_MODEL` is blocked until the original source and commercial rights are documented even though it is not under `external`.

