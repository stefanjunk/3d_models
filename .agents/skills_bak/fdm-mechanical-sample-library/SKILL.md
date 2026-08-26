---
name: fdm-mechanical-sample-library
description: Select, compare, adapt, rebuild, and validate a local library of 120 parametric FDM mechanical samples covering one-axis hinges, two-axis joints, ball joints, permanent plug/slide joints, screw interfaces, reusable snaps/latches/bayonets, linear rails, gears, detents, shaft couplers, cable clips, and pulley blocks. Use when a product needs a printable mechanical connection or motion primitive, when FDM clearance variants must be compared, or when a proven sample should be integrated into a larger CAD or OpenSCAD project.
license: MIT for code and CC0-1.0 for generated geometry
compatibility: OpenCode with project file access, Python 3.10+, and OpenSCAD for regeneration. NumPy, Trimesh, Pillow, and xvfb-run are optional for validation and headless previews.
metadata:
  version: "1.0.0"
  domain: "fdm mechanical joints connections closures and motion components"
  manufacturing: "fdm-fff-first"
  sample_count: "120"
  family_count: "30"
  outputs: "OpenSCAD source STL print plates separated part STLs PNG previews metadata validation reports"
  complements: "functional-3d-design parametric-freeform-surfacing organic-mesh-functionalization"
---

# FDM Mechanical Sample Library

Use this skill to choose and adapt a **mechanical principle**, not merely a visually similar STL.

The package root contains `catalog/catalog.json`, `samples/`, `library/fdm_mechanisms.scad`, and `tools/`. When the skill is installed without the full package, set:

```bash
export FDM_MECH_LIBRARY_ROOT=/absolute/path/to/fdm-mechanics-library-v1.0.0
```

## Companion routing

Load `functional-3d-design` as well when the task includes real loads, safety factors, fastener selection, bearings, motor torque, material qualification, tolerances beyond calibration coupons, assembly planning, or physical verification.

Load `parametric-freeform-surfacing` when a functional mechanism must be embedded in a smooth shoe, vehicle, vessel, enclosure, or other aesthetic envelope. Preserve joint axes and keep-out volumes as hardpoints.

Load `organic-mesh-functionalization` when the destination is an existing dense STL/OBJ/GLB whose source surface must remain authoritative.

Read `references/00-routing.md` before a composite workflow.

## Required selection contract

Before selecting a sample, establish or explicitly assume:

- required degrees of freedom and travel or rotation range;
- whether the connection is permanent, serviceable, cyclic, captive, or print-in-place;
- expected load direction, magnitude class, shock, vibration, and cycle count;
- available envelope, protected datums, assembly direction, and tool access;
- printer, nozzle, layer height, material, orientation, and acceptable support;
- desired play, friction, insertion force, retention force, and environmental contamination;
- permitted foreign hardware such as screws, nuts, inserts, metal pins, shafts, or magnets;
- whether failure is merely inconvenient or safety relevant.

Do not use these samples for safety-critical release without a companion engineering analysis and physical test plan.

## Search the catalog

```bash
python3 tools/query_catalog.py kugel leichtgängig
python3 tools/query_catalog.py --category linear --material PETG
python3 tools/query_catalog.py schraube --hardware-free
```

From the skill directory itself:

```bash
python3 scripts/find_samples.py kugel leichtgängig
```

Search broadly first, then compare all four variants of the chosen family. Read both `metadata.json` and the sample `README.md`.

## Method selection

Default mapping:

- one controlled rotation, removable pin → offset pin hinge;
- one controlled rotation without play, small angle → flexure or serpentine hinge;
- two angular axes → universal joint or pinned gimbal;
- small planar XY motion without bearings → XY flexure stage;
- arbitrary angular adjustment → snap ball joint or screw-clamped ball joint;
- permanent alignment → press-fit dowel, keyed plug, barb, dovetail, or wedge lock;
- repeated opening → cantilever snap, hook latch, bayonet, or slide bolt;
- repeated linear motion → dovetail rail, T/mushroom rail, or compliant preload slider;
- rotation-to-translation → rack and pinion;
- speed/torque ratio → spur gears;
- tactile angular positions → rotary detent;
- slow coaxial shaft joining → split clamp coupler;
- routing → cable clip or pulley block.

Read `references/01-selection-matrix.md` for trade-offs.

## Adaptation workflow

1. Print the existing `print_plate.stl` before modifying geometry.
2. Record the best-performing variant and actual material/slicer profile.
3. Copy the entire sample folder into the product project.
4. Modify only named semantic parameters in `model.scad` first.
5. Keep joint axes, clearances, spring roots, thread pitch, gear module, and mating profiles coupled.
6. Rebuild the sample:

```bash
python3 tools/build_library.py --ids 030 --workers 1
```

7. Re-run validation and inspect `components.json`.
8. Integrate the appropriate `parts/part_XX.stl` or call the shared OpenSCAD module directly.
9. Rebuild exact bores, planar seats, screw interfaces, and hardpoints after any non-rigid styling step.
10. Slice and physically cycle-test the integrated part.

Read `references/02-print-and-integration.md`.

## Print-in-place rule

Samples 005–008 must be printed from their common `print_plate.stl`. Their separated `parts/` files are provided only for inspection and redesign; independently arranging them destroys the calibrated relative gap.

## Validation contract

A valid library sample must have:

- source, print plate, preview, README, metadata, component report, and separated part files;
- watertight and winding-consistent components with positive volume;
- no degenerate triangles;
- all printable geometry at or above Z=0;
- component count matching the documented mechanism;
- dimensions within the declared printer envelope;
- explicit material, clearance, assembly, and limitation notes.

Run:

```bash
python3 tools/validate_library.py
```

Digital validation does not prove fatigue life, retention force, load capacity, temperature resistance, or safe failure. Read `references/03-safety-and-physical-validation.md`.

## Non-negotiable rules

- Do not uniformly scale a finished STL when clearance, thread pitch, gear module, spring thickness, bore size, or hardware dimensions matter.
- Do not select the tightest variant by default.
- Do not place snap or flexure roots across weak layer adhesion without an explicit reason.
- Do not use PLA as the default for high-cycle living hinges.
- Do not smooth, remesh, or deform mating faces and then assume the original tolerance survived.
- Do not treat printed threads or simplified gears as standards-compliant metal equivalents.
- Do not use printed pulley blocks, hooks, hinges, or couplers for people, lifting, steering, braking, guards, medical devices, or other safety functions without full engineering validation.
- Do not claim a sample is physically proven merely because all mesh checks pass.

## Delivery when adapting a sample

Deliver at minimum:

```text
mechanism/
├── README.md
├── selected-source.md
├── parameters.json
├── model.scad or native CAD source
├── print_plate.stl
├── parts/
├── preview.png
├── slicing-notes.md
└── validation/
    ├── mesh-report.json
    └── physical-test-plan.md
```
