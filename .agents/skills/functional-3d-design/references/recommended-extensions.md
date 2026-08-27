# Recommended package extensions

The package intentionally provides a strong baseline rather than pretending one generic rule set can qualify every printer and application. The following additions create the most value.

## 1. Printer/process calibration registry

Store measured values by:

```text
printer + firmware + hotend + nozzle + filament product/batch + drying + slicer/profile hash + orientation
```

Record hole compensation, fit ladders, wall/line behavior, bridges, overhangs, inserts, snaps, adhesives, shrinkage, flow, and surface resolution.

## 2. Geometric regression and visual diff

For each approved revision, store:

- critical dimensions and sampled interface points;
- body count, bounds, volume, center of mass;
- STEP/mesh checksum and tool versions;
- multi-view render.

Fail CI when a change exceeds explicit tolerances rather than merely when a render changes.

## 3. Slicer adapters

Use the sibling validation skill's tested Anycubic Slicer Next adapter for Anycubic FDM work. Add equivalent fail-closed adapters for other slicers actually present in the fleet—OrcaSlicer, PrusaSlicer, Bambu Studio CLI where available, CuraEngine, or other vendor tooling—to extract time, mass, support volume, tool changes, flow peaks, and warnings. Keep printer upload/start behind human confirmation.

## 4. Materials test database

Add tensile/bend/compression/creep/cycle coupons for the exact printed process. A generic filament family name is not enough for reliable mechanics.

## 5. Standard-interface catalog

Add locally used:

- heat-set inserts and boss coupons;
- screws/nuts/washers;
- bearings/shafts/bushings;
- magnets, O-rings, springs, motors, fans, electronics;
- preferred wall-mount and modular connector patterns.

Use supplier part number, source drawing, license, version, and measured local fit.

## 6. Failure-mode knowledge base

For each prototype, record observed failure, root cause, corrective action, and whether the rule should be generalized. Keep observations separate from universal claims.

## 7. Unit-aware parameters and schemas

Introduce unit parsing and richer JSON Schema validation so loads, temperatures, torque, and dimensions cannot be confused. Add risk-specific required fields.

## 8. Sustainability and repairability

Track material mass, support waste, print failure risk, replaceable wear parts, disassembly, mixed-material separation, and whether a standard purchased component prolongs product life.

## 9. Ergonomic and accessibility checks

For handles, drawers, toys, organizers, and wearables, add reach, pinch, edge radius, grip, labeling, handedness, and cleaning requirements.

## 10. Security and provenance

Pin external skills/MCPs/libraries, review licenses, scope filesystem/code-execution permissions, keep a dependency manifest, and never allow silent cloud upload of proprietary models.
