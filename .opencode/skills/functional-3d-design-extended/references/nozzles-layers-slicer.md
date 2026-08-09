# Nozzle, layer height, orientation, and slicing

Run:

```bash
python scripts/recommend_print_profile.py --help
```

## Nozzle selection

| Nozzle | Role | Typical layer range | Strengths | Trade-offs |
|---|---|---:|---|---|
| 0.4 mm | balanced/default | 0.10–0.28 mm | detail, small text, common profiles | slower large parts, more clog risk with fills |
| 0.6 mm | functional default | 0.18–0.42 mm | faster, thicker roads, filled materials, robust walls | reduced fine detail |
| 0.8 mm | large/coarse | 0.28–0.60 mm | fast large structures, thick single features | coarse corners/text, high flow demand |

These are starting ranges. Keep a normal default at or below 75% of nozzle diameter. Treat 80% as a verified upper edge, not the normal target.

## Layer height

- Fine cosmetic: roughly 25–40% of nozzle.
- Balanced: roughly 45–55%.
- Fast/functional: roughly 55–70%.
- Very tall layers can reduce interlayer fusion if flow/temperature/cooling are not tuned.
- Adaptive layers are useful for curved cosmetic surfaces but should not hide mechanical section changes.

## Line width and walls

- Start around 105–120% of nozzle diameter, using the slicer's tested profile.
- Model important thin walls as integer multiples of the intended extrusion width.
- Two lines may be adequate for cosmetic skins; use three or more for functional shells and more where loads or insert stresses require it.
- Increase walls before extreme infill when shell bending, impacts, and fastener loads dominate.
- Avoid fake zero-thickness knife edges and details smaller than a stable extrusion path.

## Orientation

Optimize in this order:

1. layer direction relative to primary load and crack path;
2. support access and internal cleanup;
3. dimensional accuracy of interfaces and holes;
4. bed adhesion and warp;
5. surface finish and seam visibility;
6. print time.

A visually convenient orientation can be mechanically wrong. Split a part if each half gains a much stronger orientation and the joint can be made reliable.

## Holes, fits, and first-layer effects

- Horizontal holes, vertical holes, slots, and pins have different errors.
- Calibrate holes and mating parts rather than applying one global clearance.
- Add elephant-foot relief to press/sliding interfaces near the bed.
- Use teardrop/diamond horizontal holes or support where circularity matters.
- Use `scripts/fit_clearance.py` only as a starting point.

## Overhangs and bridges

- 45 degrees is a conservative geometric starting guideline, not a universal machine limit.
- Short bridges may print well; long internal bridges and TPU bridges are less reliable.
- Chamfer lower faces, use arches/teardrops, split the model, or add removable sacrificial features before accepting inaccessible support.
- Run a coupon for the actual material/nozzle/cooling configuration.

## Infill

Select infill for the load case:

- low-density gyroid/cubic for general distributed support;
- local solid regions/modifiers around fasteners and bearings;
- aligned ribs for known bending paths;
- avoid assuming a high percentage compensates for poor layer orientation.

## Cooling and enclosure

- PLA usually benefits from cooling, especially bridges and small features.
- PETG often needs moderated cooling to preserve bonding.
- ABS/ASA/PC/PA commonly need controlled ambient temperature and reduced drafts.
- TPU profiles require slower motion and tuned cooling.
- Exact settings come from the filament/printer profile and tests.

## Volumetric flow

Approximate requested flow:

```text
flow_mm3_s = line_width_mm × layer_height_mm × print_speed_mm_s
```

A 0.8 mm nozzle at a tall layer can exceed the hotend's melt capacity quickly. Limit by measured maximum volumetric speed, not only nominal travel speed.

## Slicer preflight

Before releasing G-code:

- use an exact printer/material/nozzle profile;
- inspect first layer, bridges, support interfaces, thin-wall handling, seams, and every internal feature;
- verify build-volume and motion clearance;
- record slicer name/version and profile hash;
- save the 3MF project where possible;
- never let an agent upload/start the print without separate human approval.
