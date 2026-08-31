# metriMade watermark validation report

Asset revision: `MM-WM-001-R2`

Example identity: `MM-ORG-001` / `v0.1.0`

Digital validation date: 2026-08-28

Overall status: `DIGITAL_PASS_PHYSICAL_TEST_PENDING`

## Result

The R2 generator produces three independent, unscaled manufacturing profiles from one validated product ID/version source. Full and Compact visibly include `metriMade.com`; Micro visibly contains the owned logo, exact product ID and exact version and records `domain_visible=false`. All SVG manufacturing profiles contain outlined geometry with no live text.

| Tier | Visible identity | Authoritative envelope | Cutter digital result | Coupon digital result | Envelope area vs Full |
|---|---|---:|---|---|---:|
| Full | domain + `MM-ORG-001 · v0.1.0` | `63.789 × 12.800 × 0.400 mm` | `PASS`; 34 bodies; `62.27330 × 11.20001 × 0.40000 mm`; `99.96746 mm³` | `PASS`; one body; `69.789 × 18.800 × 2.400 mm`; `3046.41304 mm³` | `100%` |
| Compact | stacked domain, product ID, version | `40.179 × 11.200 × 0.400 mm` | `PASS`; 33 bodies; `38.79920 × 9.60041 × 0.40000 mm`; `59.55145 mm³` | `PASS`; one body; `46.179 × 17.200 × 2.400 mm`; `1845.22888 mm³` | `55.11%` |
| Micro | logo + stacked product ID/version | `36.089 × 9.600 × 0.400 mm` | `PASS`; 19 bodies; `34.72219 × 8.00000 × 0.40000 mm`; `38.58052 mm³` | `PASS`; one body; `42.089 × 15.600 × 2.400 mm`; `1536.26712 mm³` | `42.43%` |

The Full R2 manufacturing geometry is backward-compatible with R1 for the same identity: both the generated SVG and cutter STL have identical SHA-256 hashes (`9d9d138e...` and `ff6d52df...`). R2 changes the generator contract and metadata while preserving the Full profile geometry.

The disconnected cutter bodies are intentional logo planes and glyph islands. Each body is closed; all six cutter/coupon meshes pass the shared `audit-mesh` command for load, watertight topology, consistent winding and positive volume. Exact report files are stored beside this report as `r2-*-audit.json`.

## Selector regression

The R2 selector was executed against all three generated metadata packages with the default 2.0 mm edge clearance:

| Candidate surface | Safe rectangle | Expected/actual result |
|---:|---:|---|
| `80 × 30 mm` | `76 × 26 mm` | `PASS`, Full |
| `48 × 20 mm` | `44 × 16 mm` | `PASS`, Compact |
| `42 × 16 mm` | `38 × 12 mm` | `PASS`, Micro, `domain_visible=false` |
| `38 × 16 mm` | `34 × 12 mm` | `BLOCK`, no tier fits |

Every selected result uses rotation 0° or 90° and `uniform_scale=1.0`. The selector rejects mixed identities/revisions, duplicate tiers, incomplete artifact packages, insufficient host wall, invalid depth and a region smaller than Micro. Boundary reports are retained as `r2-selector-*.json`.

## Skill and learning integration

- Functional skill unit tests: `15 PASS`, including R1 compatibility and R2 Full/Compact/Micro/Block selection.
- Commercialization skill unit tests: `4 PASS`.
- Skill Creator validation: both updated skills valid.
- Shared printable-project skill validation: both updated skills `PASS`; the functional skill retains a pre-existing optional dependency-declaration `REVIEW_REQUIRED` note for PyYAML/numpy/trimesh, which does not change the required-check result.
- Learning-system schema validation and audit cover correction candidate `EXP-00023` and targeted eval `EVAL-regression-watermark-layout-tier-selection-001`.

## Remaining release gate

Digital geometry and skill integration do not prove first-layer legibility. Before any tier is approved for a product, slice and print that tier's generated coupon with the exact intended printer, 0.40 mm nozzle, layer profile, material/color, first-layer settings and bed surface. Record the selected tier, confirm every required visible field without guessing, and archive the relevant slicer layers. Micro must additionally retain the controlled domain in the product's 3MF metadata and/or provenance sidecar.

Until those product/process-specific checks pass, R2 remains a digital production candidate rather than a physically qualified production watermark.
