# Example 3 — Food-serving bowl with fine ornament

## Goal

Create a porcelain or stoneware bowl for fruit or snacks, with fine decorative engraving. The desired final article is food-contact capable and intended to tolerate dishwasher cleaning after formal qualification.

## Recommended geometry

Example final target:

- outer diameter: 180–240 mm;
- height: 60–100 mm;
- flared/open rim with no reverse undercut;
- smooth interior transition radius;
- stable foot ring with dishwasher-drain interruptions;
- fine relief primarily on the exterior;
- broad shallow optional motif inside, only after glaze/cleanability tests.

Avoid a rim that curls inward past the maximum body diameter. It locks a rigid mold section and makes greenware removal fragile.

## Process route

Use conventional ceramic slip-casting tooling:

```text
compensated positive bowl master or printed negative case
→ multipart absorbent pottery-plaster working mold
→ conditioned porcelain/stoneware slip
→ fill and top-up reservoir
→ dwell until target wall thickness
→ drain fully on cradle
→ stiffen and shrink from mold
→ open mold in defined order
→ fettle, dry, bisque, glaze/decor, fire
→ inspect and laboratory-validate intended food contact
```

Do not directly fill an ordinary sealed FDM negative and expect conventional hollow wall build.

## Mold split

A pull-safe bowl with shallow exterior relief can often use:

- two side sections split vertically;
- one base/foot section if the foot creates a lock;
- a removable top pour-spout ring/reservoir.

Use three or four side sections when relief crosses the equator or creates lateral hooks. Place vertical seams between ornament bands or on low-visibility axes. Keep the lip out of a rough seam when possible.

## Ornament strategy

### Exterior

Exterior ornament is preferred because it does not contact food and can be deeper. Still avoid sharp fragile ridges that chip in use or the dishwasher.

Starting transfer coupon:

- line width: 0.5, 0.8, 1.2, and 2.0 mm;
- relief depth: 0.2, 0.3, 0.5, and 0.8 mm;
- include convex/concave curvature representative of the bowl;
- include a parting seam through one motif variant;
- carry the coupon through plaster, casting, glaze, firing, and repeated cleaning.

### Interior

Use broad shallow engraving only. Design the glaze as part of the geometry. Deep valleys can remain unglazed, pinhole, pool, or become difficult to clean. Prefer decoration under a stable glaze rather than exposed rough relief.

## Food-contact surface rules

- Fully mature, compatible body and glaze.
- No crazing, crawling, shivering, pinholes, sharp inclusions, or exposed absorbent body in the food-contact zone.
- Decoration and stains included in the migration validation.
- Smooth rim and inspectable interior.
- No hidden double-wall cavity or foot ring that retains dishwasher water.
- Final legal and laboratory validation for the intended market and use.

“Food-safe glaze” on a supplier page is not sufficient evidence for the final article.

## Dishwasher design

Dishwasher durability needs its own qualification:

- water must drain from the interior and foot;
- relief must not create fragile tips;
- the glaze/body fit must survive repeated thermal and alkaline cycles;
- decoration must resist fading/attack;
- post-cycle inspection must check delayed crazing, cutlery marks, chips, and retained soil;
- migration validation may need repeating after wear or process changes.

## Fill/spout/drain design

Use a removable spout at the open top:

- broad reservoir above the rim to remain full during wall build;
- tapered transition so the cast rim can be trimmed cleanly;
- no nonabsorbent collar covering the entire rim-building surface unless deliberately accounted for;
- vent any high pocket in foot or exterior ornament;
- cradle supports the inverted mold during complete drain;
- drip path avoids running slip over plaster mating surfaces.

Track fill mass, slip specific gravity/viscosity according to the body supplier, dwell time, drain time, mold moisture, and wall thickness. Use these process variables, not CAD alone, to stabilize results.

## Shrinkage and wall thickness

Measure the exact body's dry and fired shrinkage in relevant orientations. A bowl can distort non-uniformly due gravity, wall thickness, mold moisture, and kiln support. Include:

- diameter rings at rim/mid/foot;
- vertical height gauge;
- wall-thickness sections;
- roundness measurement after firing;
- body/glaze test tiles from the same batch.

Scale the master with measured anisotropic compensation, then iterate from fired measurements.

## Mold architecture

For repeated production, use printed **cases** to make replaceable plaster sections. Recommended printed-case construction:

- thin detailed cavity shell or high-resolution insert;
- external open ribs;
- broad flat flange;
- asymmetric keys;
- clamp bosses;
- plaster pour gate and air vents outside the future casting face;
- removable case sections with draft relative to the plaster part.

The case is sealed/released. The resulting plaster bowl-working surface remains porous.

## Memory/resolution plan

Do not subdivide the whole bowl uniformly to match a tiny ornament. Use:

- clean parametric/revolved bowl base mesh;
- localized subdivided ornament band with continuous cylindrical/UV mapping;
- low-poly external case structure;
- final boolean only on each mold sector;
- separate exports for side and foot sections.

For an ornament band 200 mm in circumference with 0.2 mm sampling pitch, roughly 1000 samples around the band are sufficient to represent 0.6 mm features at about three samples per feature. Vertical sampling depends on the band height.

## Acceptance criteria

Geometry/process:

- wall thickness within defined range around the bowl;
- no locked mold section or greenware tearing;
- rim roundness and foot stability within tolerance;
- no trapped slip in ornament or foot;
- seam can be fettled without thinning the bowl;
- full drain within defined time.

Food/durability:

- glaze/body/decor system passes visual defect inspection;
- completed representative articles pass applicable migration testing;
- dishwasher test plan passes the stated cycle count without crazing, chipping, staining, trapped water, or unacceptable decoration change;
- user claims match the evidence and intended food/contact conditions.

## Suggested commands

```bash
python scripts/common/mold_planner.py assets/examples/food-bowl.json \
  --output build/food-bowl-plan.md

python scripts/common/shrinkage_calculator.py \
  --final 220 220 80 --shrink 12.0 12.0 13.0 --json build/bowl-scale.json

python scripts/cadquery/detail_coupon.py --curved --output-dir build/bowl-coupon
```
