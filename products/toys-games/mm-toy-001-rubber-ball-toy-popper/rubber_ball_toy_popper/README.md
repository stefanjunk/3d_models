# 20 mm Rubber-Ball Toy Popper

This folder contains a parametric CadQuery model for a brightly styled,
low-energy toy popper. It launches **soft 20 mm rubber balls only** with a
spring-driven air piston. The design uses a thumb-operated sear rather than a
firearm-style trigger and includes a removable physical safety block.

The design is intentionally capped at about **0.13 J of stored spring energy**.
Do not install a stronger spring, enlarge the bore, defeat the travel stop, or
use hard projectiles.

## Files

- `cadquery_toy_popper.py`: parametric source and STL/STEP generator
- `requirements.txt`: Python dependency
- `output/toy_popper_body.stl`: main pressure chamber and barrel
- `output/toy_popper_grip.stl`: sliding grip
- `output/toy_popper_rear_cap.stl`: bolted spring and sear carrier
- `output/toy_popper_plunger.stl`: piston, rod, catch groove, and pull handle
- `output/toy_popper_sear.stl`: thumb release lever
- `output/toy_popper_safety_block.stl`: physical release blocker
- `output/toy_popper_muzzle_ring_ORANGE.stl`: ball-retention and visibility ring
- `output/toy_popper_rail_lock_pin.stl`: printed grip pin
- `output/toy_popper_ball_fit_gauge.stl`: 19.6, 20.4, and 21.0 mm test holes
- `output/toy_popper_assembly_preview_NOT_FOR_PRINT.stl`: visual assembly only
- `output/toy_popper_assembly.step`: editable assembly geometry

## Required Hardware

- 1 compression spring, **18 mm maximum OD**, **14.5 mm minimum ID**, about
  **74 mm free length**, spring rate **0.20 to 0.25 N/mm**, and solid length
  below 40 mm
- 1 O-ring, **28 x 2 mm**
- 4 M3 x 18 or M3 x 20 bolts with washers and locknuts for the rear cap
- 1 M3 x 22 bolt with washers and a locknut for the sear pivot
- 1 very weak 5 x 10 mm compression spring, such as a trimmed pen spring, for
  sear return
- Plastic-safe silicone grease for the O-ring
- Soft, deformable 20 mm rubber balls

The firing spring must not exceed 0.25 N/mm. At the designed 32 mm travel this
means a maximum spring force of 8 N and about 0.128 J stored energy.

## Generate the Models

Install CadQuery 2.8 or newer, then run:

```bash
python3 -m pip install cadquery
python3 cadquery_toy_popper.py
```

The script writes all generated files into `output/`. Important dimensions are
grouped at the top of the script. Safety assertions prevent accidental export
when the configured spring energy exceeds 0.15 J.

## Fit Check Before the Full Print

Print `toy_popper_ball_fit_gauge.stl` first. The three holes are arranged from
left to right when the 82 mm edge is horizontal:

1. 19.6 mm: the ball should pass only with gentle rubber compression.
2. 20.4 mm: the ball should pass with light friction.
3. 21.0 mm: the ball should pass freely.

If the ball does not behave this way, measure it with calipers and adjust
`BALL_DIAMETER`, `BARREL_CLEARANCE`, and `BALL_RETENTION_DIAMETER` before
printing the body. Do not force an oversized ball into the finished barrel.

## Recommended Slicer Settings: 0.4 mm Nozzle, High-Speed PLA+

- Layer height: 0.20 mm for the plunger, cap, sear, and muzzle ring
- Layer height: 0.24 mm for the body and grip
- Line width: 0.42 to 0.46 mm
- Walls: 5 perimeters; use 6 for the rear cap and plunger
- Top/bottom layers: 6
- Infill: 25% gyroid for body and grip; 50% for cap, sear, and plunger
- Seam: align to the rear or least-visible side
- Elephant-foot compensation: 0.15 to 0.20 mm
- Supports: off by default; use build-plate-only support only if your slicer
  flags the rear-cap sear shelf
- Brim: 6 to 8 mm on the tall body and plunger
- PLA+ nozzle temperature: use the filament maker's high-speed range, commonly
  215 to 230 C
- Bed: commonly 55 to 65 C
- Maximum volumetric flow: stay within the filament and hot-end rating
- Outer wall speed: 45 to 70 mm/s even when inner walls print faster
- Cooling: follow the PLA+ maker's guidance; keep full cooling on small sear
  and safety parts

The STLs are already arranged in their recommended print orientations. The
body and plunger print vertically for round bores and rods. The grip and sear
print on a broad side for layer strength.

## Assembly

1. Deburr every air path, the grip rail, the rod guide, and the three ball-fit
   surfaces. Do not sand the piston chamber aggressively.
2. Fit the 28 x 2 mm O-ring to the plunger groove and apply a very thin film of
   silicone grease.
3. Test the plunger in the body without a spring. It must move freely and seal
   without binding. Stop and correct the fit if it sticks.
4. Slide the grip onto the body rail from the rear until it reaches the front
   stop. Align the 4.2 mm holes and install the printed rail pin.
5. Place the firing spring around the plunger rod, insert the plunger, and fit
   the rear cap locating boss into the chamber.
6. Bolt the rear cap to the body using all four M3 fasteners, washers, and
   locknuts. Tighten evenly and only until secure.
7. Install the sear between the cap ears with the M3 pivot bolt. The tooth must
   face down into the rod groove. Add the weak return spring between the cap
   shelf and rear thumb pad.
8. Verify that the sear drops fully into the catch groove when the plunger is
   pulled back 32 mm. It must hold firmly through ten unloaded cock-and-release
   tests.
9. Slide the safety block under the rear thumb pad. With it installed, pressing
   the sear must not release the plunger.
10. Slide or glue the muzzle ring over the final 8 mm of the barrel. Print it in
    orange or another highly visible toy color.

## Use and Safety

- Wear eye protection during assembly and every test.
- Test outdoors against a soft backstop with no people, animals, glass, or
  fragile objects nearby.
- Keep the safety block installed until the toy is pointed at the backstop.
- Never aim at a face, person, or animal.
- Use only soft 20 mm rubber balls. Never use bearings, marbles, printed slugs,
  stones, or other hard objects.
- Do not use a spring stronger than specified and do not add elastic bands,
  pressure tanks, combustion, or other energy sources.
- Inspect the sear, cap, bolts, plunger, and body for cracks before every use.
  Retire any damaged part immediately.
- PLA+ softens in a hot car and creeps under continuous load. Store uncocked,
  unloaded, and away from heat and children.

This is a hobby design, not a certified commercial toy. The builder is
responsible for validating local toy, product-safety, and public-use rules.
