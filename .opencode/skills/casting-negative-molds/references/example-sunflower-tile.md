# Example 2 — Marble-look floor tile with sunflower engraving

## Goal

Create a shallow tile or decorative floor insert with a sunflower engraving and marble appearance. The manufacturing route may be stoneware/porcelain or a decorative gypsum/plaster cast.

## Process choice

### Ceramic floor/decorative tile

Recommended chain:

```text
parametric tile + sunflower positive/negative relief
→ printed high-quality master or detail insert
→ one-sided absorbent plaster working mold / press mold
→ conditioned clay body or casting body
→ controlled drying and flat firing support
→ glaze/decor qualification
```

A one-sided open mold is usually more efficient than a closed mold. No funnel is needed for a slab/press route. For a liquid cast, use an open top and a screed/overflow rim.

### Decorative plaster tile

A sealed printed one-sided negative can be the direct working mold. Use a rigid reusable frame, release system, and back-screed rails.

Do not call a decorative plaster tile a qualified load-bearing floor product without mechanical, abrasion, slip, moisture, and regulatory testing.

## Geometry

Example nominal final size:

- 200 × 200 mm face;
- ceramic fired thickness: project-specific, initially 8–12 mm for prototype discussion;
- perimeter edge draft: begin around 2–4° depending depth/process;
- rear ribs/keys only when compatible with drying and firing;
- corner radii to reduce chipping and stress.

Keep the casting face on a flat datum. Use a surrounding sacrificial trim band so edge defects can be cut away or so excess material can be screeded consistently.

## Sunflower engraving

Decide whether the final flower is recessed or raised:

- recessed final engraving → positive ridges in the negative working mold;
- raised final relief → recessed flower in the mold.

Use broad hierarchy:

- primary petal outlines;
- secondary petal veins;
- center-seed texture;
- low-frequency marble veins beneath or around the motif.

Avoid equal-depth high-frequency detail over the entire face. It muddies the flower and increases bubble/release risk.

Starting 0.4 mm FDM master/case coupon:

| Feature | Width | Relief depth/height |
|---|---:|---:|
| Main petal boundary | 0.8–1.5 mm | 0.3–0.7 mm |
| Petal vein | 0.5–0.8 mm | 0.2–0.4 mm |
| Center seed cell | 0.6–1.2 mm | 0.2–0.6 mm |
| Marble vein | 0.5–1.5 mm | 0.15–0.4 mm |

Print a small 60–80 mm motif coupon and carry it through the actual plaster, body, glaze, and firing sequence.

## Mold architecture

Preferred:

- thin high-resolution cavity insert;
- reusable rectangular frame/cottle and flat backing plate;
- gasket or sealed perimeter outside the article;
- replaceable sunflower cartridge if multiple motifs are planned;
- external stiffening ribs or frame, not a thick printed block.

For a tile larger than the printer or memory budget, split the insert into keyed quadrants along natural sunflower/marble lines. Support every quadrant on one flat backing datum; do not rely on four independently warped panels.

## Open-face fill/press details

For direct plaster pour:

- make the top edge level;
- add a 5–15 mm overflow/screed zone outside the final tile perimeter;
- pour a face coat into the engraved detail;
- tap/vibrate carefully;
- fill to above final thickness;
- screed against rails;
- demold with broad ejector access or by flexing/removing the insert/frame in sequence.

For ceramic slab/press molding:

- provide air escape from the center outward;
- avoid a fully sealed flat rear contact that traps air;
- use release appropriate to the clay/plaster method;
- keep thickness uniform;
- dry between absorbent boards or according to the body process to control curl.

## Marble appearance

The mold can transfer subtle vein relief, but realistic marble appearance normally also requires color variation. For ceramic:

- colored slips/engobes;
- underglaze or stains;
- glaze effects qualified for floor/food/contact use as applicable;
- body marbling through colored clay where process permits.

Keep relief low in walking/contact zones because deep grooves collect soil and concentrate wear. For a real floor installation, surface texture also affects slip resistance and cleanability; test the finished tile, not only the CAD.

## Warpage and shrinkage

Tiles are sensitive to:

- nonuniform thickness;
- directional rolling/extrusion texture;
- uneven moisture extraction from plaster;
- differential drying between engraved and flat regions;
- glaze/body mismatch;
- kiln support and temperature gradients.

Use X/Y shrinkage coupons in both body directions. Measure diagonals, bow, twist, and thickness after drying and firing. Compensation alone cannot fix unstable processing.

## Memory plan

A 200 mm tile with 0.2 mm sample pitch needs about 1000 × 1000 relief samples, roughly two million triangles for a direct grid before structural geometry. This is usually enough for 0.6 mm-class motifs. Do not retain a 4K image as a 33-million-triangle displacement unless tests prove the physical benefit.

Use the height-map tool:

```bash
python ../3d-print-heightmap-relief/scripts/prepare_heightmap.py \
  sunflower.png build/sunflower.png \
  --physical-width-mm 200 --physical-height-mm 200 \
  --sample-pitch-mm 0.20 --fit contain --invert --gamma 0.9 \
  --blur-mm 0.6 --report build/sunflower-heightmap.json
```

## Acceptance criteria

- fired/plaster dimensions and flatness meet project tolerance;
- all petal boundaries remain distinct after final finishing;
- no air bubbles in central seed texture above agreed size/count;
- back is level enough for intended mounting;
- no sharp positive needles in the mold or cast;
- quadrants/inserts leave no unacceptable step;
- realistic marble direction remains continuous across the face;
- for real flooring, separate tests cover strength, abrasion, water absorption, freeze/thaw where relevant, cleanability, and slip performance.
