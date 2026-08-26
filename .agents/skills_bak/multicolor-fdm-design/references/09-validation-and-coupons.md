# Validation and coupons

## Geometry validation

For each color part report:

- bounds and common transform;
- vertices/faces and connected bodies;
- watertightness and winding consistency;
- positive volume;
- degenerate/duplicate faces where detectable;
- minimum feature and wall checks where available.

For the assembly report:

- pairwise overlap volume or collision warning;
- union-envelope agreement with the intended product;
- gaps at interfaces larger than the job tolerance;
- parts entirely internal or missing from the exterior.

## Texture conversion validation

Persist:

- UV/material/texture inspection;
- quantization error statistics;
- original and quantized previews;
- number/area of removed islands;
- voxel pitch, shell depth, and estimated memory;
- deviation from source mesh after remeshing;
- seam and sharp-edge review.

## 3MF validation

Run:

```bash
python3 scripts/validate_multicolor_3mf.py model.3mf --json-out report.json
```

Check package members, XML namespaces, IDs, material references, component references, triangle indices, part count, and optional extracted mesh metrics.

## Final slicer review

Mandatory screenshots or notes:

- object/part list and assigned filaments;
- color/tool preview from bottom, middle, and top;
- layers where a new color begins or ends;
- wipe tower and support tool assignment;
- purge matrix and flush destinations;
- estimated changes, time, purge volume, and material waste;
- thin-detail warnings and dropped regions.

## Physical coupons

### Color-boundary coupon

Include straight, curved, diagonal, and one-line/two-line boundaries. Measure bleed, gaps, bulges, and repeatability.

### Purge matrix coupon

Print directed transitions for every important pair. Evaluate visible contamination over a fixed light-colored length/thickness.

### Inlay coupon

Test several widths and depths with the same top-surface settings as the product.

### Opacity coupon

Print 1–5 wall-thickness steps over light and dark backings.

### Texture-resolution coupon

Print representative islands and line patterns at increasing physical size. Use it to set the cleanup threshold.

Record results in a project-local evidence registry; do not promote a heuristic to a global rule after one print.
