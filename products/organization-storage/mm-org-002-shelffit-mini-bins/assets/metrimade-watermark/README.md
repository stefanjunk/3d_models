# metriMade product watermark

Status: `DIGITAL_PRODUCTION_CANDIDATE_PHYSICAL_TEST_PENDING`  
Asset revision: `MM-WM-001-R1`

Every newly generated metriMade production mark contains two mandatory visible lines:

```text
metriMade.com
<PRODUCT_ID> · v<VERSION>
```

Example: `metriMade.com` and `MM-ORG-001 · v0.1.0`. The domain is fixed in the generator. Product ID and Semantic Versioning version are required arguments; generation fails if either is missing or malformed.

![Example metriMade engraving profile](exports/examples/MM-ORG-001_v0.1.0/metrimade-watermark-MM-ORG-001-v0.1.0.png)

## Generate an exact product mark

```bash
python3 tools/generate_watermark.py \
  --product-id MM-ORG-001 \
  --version 1.0.0
```

The generated directory contains:

- an outlined SVG manufacturing profile with no live text;
- a DXF profile in millimetres;
- a mirrored STL Boolean cutter that reads normally from the finished underside;
- a recessed test-coupon STL;
- an OpenSCAD wrapper, visual PNG, metadata JSON and SHA-256 manifest.

The checked-in `MM-ORG-001_v0.1.0` files are a geometry example and coupon candidate only. They do not approve that SKU or version for sale.

Verify the checked-in package before use:

```bash
sha256sum -c manifest.sha256
```

## Integration rules

1. Generate the mark from the exact immutable product ID and release version; never type the trace line manually.
2. Put it on a flat, nonfunctional, low-stress surface, normally the underside.
3. Subtract the cutter with 0.01 mm overlap. The supplied cutter is mirrored in X so the finished underside reads normally.
4. Keep the host wall at least 1.20 mm thick and at least 0.80 mm after engraving.
5. Start with 0.40 mm depth for a 0.40 mm nozzle and 0.20 mm layers. Do not scale the profile down.
6. Slice and print the generated coupon with the intended printer, nozzle, material, first-layer settings and bed surface before product release.
7. Confirm the physical mark is readable and that the printed product, package/file name, release manifest and catalog all show the same product ID and version.

For source integration, use `source/metrimade-watermark.scad` or import the generated SVG/DXF directly into the authoritative CAD model. A recessed geometry mark supports identification and traceability; it does not replace legal product markings, release records or IP/safety review.

## Migration rule

Do not overwrite or silently rebuild historical product releases carrying the JuSt Innovation mark. Apply `MM-WM-001-R1` only to a new product revision, record the changed geometry/hash, rerun the affected print and product checks, and retain the previous immutable release.
