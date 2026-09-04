# metriCreate logo

Status: `SELECTED_VECTOR_REDRAW_CLEARANCE_PENDING`

Asset revision: `MC-BRAND-001-R3`

Selected by: Stefan Junk on 2026-09-04

The production direction is concept `01` from the [v3 sister-brand concept sheet](../../logo-concepts/metricreate-metrimade-sibling-concepts-v3.png), reconfirmed through the [isolated user selection](source/reference/metricreate-v3-concept-01-user-selection.png): a compact spatial enclosure with a rounded midnight-navy left plane, a precise teal right plane, a fitted off-white floor and one signal-orange upper cut. The SVG redraw uses flat colors and explicit geometry so it remains crisp, editable and reproducible without the raster reference's gradients, glow or artifacts.

![Selected metriCreate logo](exports/metricreate-lockup-stacked-color-dark.png)

## Binding assets

| Use | Preferred file |
|---|---|
| Primary stacked logo with fixed dark field | `exports/metricreate-lockup-stacked-color-dark.svg` |
| Website/header lockup with fixed dark field | `exports/metricreate-lockup-horizontal-color-dark.svg` |
| Compact app icon/favicon with fixed dark field | `exports/metricreate-mark-color.svg` |
| One-color or light-background production | corresponding `*-mono.svg` file |
| Raster preview only | corresponding PNG file |

Use SVG for web, print and packaging masters. PNG files are previews, not source artwork. Do not reconstruct the logo from the AI-generated concept sheet.

## Binding palette

| Role | Value |
|---|---|
| Anthracite canvas | `#0B0F12` |
| Shared midnight navy | `#112431` |
| Shared brand teal | `#08777D` |
| Shared light aqua | `#7FD5D3` |
| High-contrast off-white | `#F2F6F5` |
| Signal orange | `#F05A28` |

The wordmark is outlined from Inter Variable at weight 650. No live font remains in the SVG files. The font used for the deterministic build is licensed under the SIL Open Font License 1.1; see [the rights record](THIRD-PARTY-NOTICES.md) and `provenance.json`.

The intended rights owner is `Stefan Junk Holding UG (haftungsbeschränkt)`. That ownership and the public-use risk decision remain subject to the signed `BRD-001` record; the asset package does not itself establish trademark availability.

## Background and light-ground study

The historical, non-binding [`MC-BRAND-001-R2` candidate study](candidates/r2-background-light-ground/README.md)
tested permanent carriers and light-ground recoloring on the now-superseded R1
voxel geometry. The selected R3 route instead adopts v3 concept `01` and embeds
the dark field directly in every binding full-color asset.

## Minimum-use rules

- Preserve the spelling and capitalization `metriCreate`.
- Keep clear space of at least one quarter of the mark width around the complete logo.
- Keep the fixed anthracite field in every full-color use. Use the monochrome navy version on light backgrounds or when color reproduction is unreliable.
- Do not recolor individual planes, remove the background field, add gradients/shadows, rotate the mark or place text inside the spatial opening.
- Preserve the complete four-part construction: navy left plane, teal right plane, off-white fitted floor and orange upper cut.
- Use the compact mark at no less than 24 CSS pixels for ordinary UI. At 16 pixels, use it only as the tested favicon treatment on its dark square field.
- This selection does not close `BRD-001`: trademark/name searches, visual similarity review and the signed risk decision remain open.

## Rebuild

```bash
python3 source/build_brand_assets.py
sha256sum -c manifest.sha256
```

The build requires FontTools, ImageMagick and a local Inter Variable font. The build source, concept-sheet hash, isolated selection-reference hash, font hash and generated asset hashes are retained in this directory. The superseded production package is retained unchanged in [`archive/MC-BRAND-001-R1`](archive/MC-BRAND-001-R1/README.md).

## Website integration

Repository consumers that reference the stable export paths receive the new R3 geometry automatically. Separate storefront-native copies such as `src/components/logo.tsx`, `public/metricreate-icon.svg` or `public/metricreate-apple-icon.svg` must be synchronized from this package before deployment. No deployment was performed as part of this selection.
