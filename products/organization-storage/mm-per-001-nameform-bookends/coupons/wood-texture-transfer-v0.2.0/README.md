# NameForm wood-texture direct-transfer coupon v0.2.0

Status: candidate C physically preferred for the next NameForm design; exact
print context and the revised textured-glyph/connector review remain open.

This revision corrects the failed v0.1 coupon. The successful Honeycomb shelf
does not first shrink the wood image to a low-resolution build raster. Its mesh
generator samples the original image bilinearly at every 0.45 mm mesh vertex.
The failed coupon inserted a Lanczos resize before that step. On an equivalent
45 x 45 mm wall patch, that prefilter reduced the normalized P95-P5 image span
from 0.5763 to 0.3760, a 34.8% loss before slicing or printing.

The v0.2 geometry therefore keeps the full 1254 x 1254 16-bit master and limits
cost only through the physical 0.45 mm geometry grid. The repeating NameForm
patch is 120 x 45 mm; only a 24-pixel edge band is blended to hide repetition
seams. The image itself is never downsampled.

## What to print first

Print this one-piece coupon:

`exports/DRAFT-nameform-wood-direct-transfer-coupon-v0.2.0.stl`

Read the four upright fields from left to right:

| Field | Mapping | Depth | Decision purpose |
| --- | --- | ---: | --- |
| A | exact Honeycomb vertical-wall mapping, raw master | 0.6 mm | control against the successful shelf pipeline |
| B | direct 120 x 45 mm repeating patch, raw master | 0.6 mm | patch scale without seam treatment |
| C | direct 120 x 45 mm repeating patch, 24 px seam blend | 0.6 mm | intended NameForm transfer |
| D | same as C | 0.9 mm | visibility reserve for upright perimeter printing |

The raised `E` is identical in every field and defines both front direction and
the protected no-texture zone. Do not use the render to approve appearance; its
grazing light is intentionally diagnostic.

## Print contract

- Keep the supplied upright orientation and `z=0` base. Do not lay the panels
  flat.
- 0.4 mm nozzle, 0.12 mm layer height, nominal 0.45 mm line width.
- Supports off. Do not scale the STL.
- Use the same filament product, color, drying/conditioning and relevant flow
  settings as the successful Honeycomb shelf when possible. The repository
  currently proves only PETG family, not the exact successful spool.

The retained Anycubic Slicer Next run uses the bundled Kobra 3 Max 0.4 mm,
0.12 mm Standard, and Anycubic PETG profiles as an explicit provisional set.
It exports locally only; no printer upload or print start occurs.

The exact coupon slice passes with 416 layers, no support or brim, 29.64 g
slicer-reported filament and a 2 h 18 min normal-mode estimate. The integrated
left/right drafts also pass at 1,333 layers each; the profile adds a brim but no
support and estimates 108.10/108.31 g and 7 h 43 min/7 h 42 min respectively.

## Selection rule

- If A is visible but B/C are not, keep the exact Honeycomb wall mapping and
  reject the 120 x 45 mm patch mapping.
- If B and C are similarly visible and the C seam is unobtrusive, select C for
  NameForm.
- If only D is convincing, rebuild NameForm at 0.9 mm depth before printing a
  full pair.
- If none is convincing, stop engraving the upright perimeter. The next route
  is a separately flat-printed textured skin or faceplate, because its relief
  is then resolved in Z rather than primarily by XY perimeter placement.

The user selected C on 2026-08-31 as already looking quite good. That selection
authorizes C as the 0.4.0 glyph-front design input. It does not promote the old
broad-wing pair to a print candidate and does not validate textured glyph
flanks or the new recessed connector.

## Integrated NameForm draft

Candidate C is already applied to the existing v0.3.0 `STE | FAN` pair so the
transfer can be inspected without another expensive modeling iteration:

- `exports/nameform/DRAFT-nameform-STE-FAN-left-wood-direct-v0.3.0-tx0.2.0.stl`
- `exports/nameform/DRAFT-nameform-STE-FAN-right-wood-direct-v0.3.0-tx0.2.0.stl`

Only the broad front wings are engraved. Raised text and its bond, the rounded
wing edge, bed datum, side-blade junction, foot, ribs, gussets, book-contact
face and watermark remain protected. These pair files remain DRAFT until the
coupon establishes whether C or D is physically correct.

## Digital evidence

- Coupon: 84,194 triangles, one watertight body, 0 degenerate faces.
- Left: 111,962 triangles, one watertight body, 0 degenerate faces.
- Right: 107,018 triangles, one watertight body, 0 degenerate faces.
- Robust active relief span: A 0.349 mm, B 0.311 mm, C 0.307 mm, D 0.461 mm;
  integrated left/right 0.329/0.321 mm.
- The deterministic reference-pipeline comparison reproduces the 34.76%
  prefilter span loss and confirms that the registered master is numerically
  equivalent to the original Honeycomb image.
- Geometry generation and exact-artifact reproducibility: PASS.
- Exact slicer and G-code reports are under `reports/`; manufacturing artifacts
  are retained under `slicer-runs/`.

## Rebuild

The committed generated paths are write-once. Rebuild into a new empty root:

```bash
python source/generate_transfer.py --output-root /new/empty/output-root
```

Check exact reproducibility against the committed artifacts:

```bash
python source/check_reproducibility.py --json-out /new/report.json
```

Render the meshes with fixed grazing light:

```bash
blender --background --python source/render_transfer.py -- \
  --coupon exports/DRAFT-nameform-wood-direct-transfer-coupon-v0.2.0.stl \
  --left exports/nameform/DRAFT-nameform-STE-FAN-left-wood-direct-v0.3.0-tx0.2.0.stl \
  --right exports/nameform/DRAFT-nameform-STE-FAN-right-wood-direct-v0.3.0-tx0.2.0.stl \
  --output-dir renders
```
