# metriMade product watermark

Status: `DIGITAL_PRODUCTION_CANDIDATE_PHYSICAL_TEST_PENDING`  
Asset revision: `MM-WM-001-R2`

R2 provides three purpose-built, unscaled layout tiers. Every tier shows the owned logo, exact product ID and exact version:

| Tier | Visible identity | Example envelope |
|---|---|---:|
| `full` | `metriMade.com` and `<PRODUCT_ID> · v<VERSION>` | `63.789 × 12.8 mm` |
| `compact` | stacked `metriMade.com`, `<PRODUCT_ID>`, `v<VERSION>` | `40.179 × 11.2 mm` |
| `micro` | stacked `<PRODUCT_ID>`, `v<VERSION>`; domain omitted | `36.089 × 9.6 mm` |

The dimensions above use `MM-ORG-001` / `v0.1.0`; width varies with identity length. The domain remains fixed in generator metadata even when the `micro` geometry omits it. Product ID and Semantic Versioning version are required arguments; generation fails if either is missing or malformed.

![Approved R2 layout concept](validation/concept-r2-watermark-tiers.png)

## Generate an exact product mark

```bash
python3 tools/generate_watermark.py \
  --product-id MM-ORG-001 \
  --version 1.0.0 \
  --layout all
```

`--layout full` remains the default for backward-compatible single-layout generation. `--layout all` generates Full, Compact and Micro packages for automatic safe-region selection.

The generated directory contains:

- an outlined SVG manufacturing profile with no live text;
- a DXF profile in millimetres;
- a mirrored STL Boolean cutter that reads normally from the finished underside;
- a recessed test-coupon STL;
- an OpenSCAD wrapper, visual PNG, metadata JSON and SHA-256 manifest.

The checked-in R1 and R2 example files are geometry and coupon candidates only. They do not approve that SKU or version for sale.

Verify the checked-in package before use:

```bash
sha256sum -c manifest.sha256
```

## Integration rules

1. Generate all R2 tiers from the exact immutable product ID and release version; never type the trace lines manually.
2. Put it on a flat, nonfunctional, low-stress surface, normally the underside.
3. Use the skill selector to try Full, Compact and Micro in that order at 0° and 90°, always at scale 1.0. Micro is permitted only when Full and Compact do not fit the measured safe region.
4. Subtract the selected cutter with 0.01 mm overlap. The supplied cutter is mirrored in X so the finished underside reads normally.
5. Keep the host wall at least 1.20 mm thick and at least 0.80 mm after engraving.
6. Start with 0.40 mm depth for a 0.40 mm nozzle and 0.20 mm layers. Never scale a generated tier down.
7. Slice and print the coupon for the selected tier with the intended printer, nozzle, material, first-layer settings and bed surface before product release.
8. Confirm the selected visible identity is readable and that the printed product, package/file name, release manifest and catalog all show the same product ID and version. For Micro, verify the controlled domain in 3MF metadata and/or the provenance sidecar.

For source integration, use `source/metrimade-watermark.scad` or import the generated SVG/DXF directly into the authoritative CAD model. A recessed geometry mark supports identification and traceability; it does not replace legal product markings, release records or IP/safety review.

## Migration rule

Do not overwrite or silently rebuild historical product releases carrying the JuSt Innovation mark or `MM-WM-001-R1`. Apply `MM-WM-001-R2` only to a new product revision, record the selected tier and changed geometry/hash, rerun the affected print and product checks, and retain the previous immutable release.
