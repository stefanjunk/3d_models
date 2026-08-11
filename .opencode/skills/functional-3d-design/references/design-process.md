# Design process and project structure

## Contents

- [Design objective](#design-objective)
- [Risk classes](#risk-classes)
- [Fabrication preference](#fabrication-preference)
- [Stage gates](#stage-gates)
- [Definition of done](#definition-of-done)

## Design objective

The objective is not merely to produce a mesh. It is to produce a traceable design package that can be changed, built, tested, and reused.

## Risk classes

| Class | Typical examples | Minimum evidence |
|---|---|---|
| `decorative` | figurine, visual trim, display label | valid mesh, bed fit, visual review |
| `normal-functional` | organizer, knob, low-load enclosure | dimensional checks, slicer review, interface coupon or prototype |
| `structural` | loaded shelf, bracket, moving mechanism | load assumptions, orientation/material rationale, calculation or FEM, destructive or proof test, safety factor |
| `safety-critical` | lifting, vehicle control, pressure, mains/fire/medical | professional review, applicable standards, qualified process and material; do not self-certify |

## Fabrication preference

### `integrated-print`

Prioritize fewer components and assembly operations.

Good techniques:

- integrated bosses, spacers, ducts, cable clips, handles, flexures, print-in-place hinges;
- captive purchased hardware inserted during or after printing;
- geometry that prints in one orientation without inaccessible support.

Trade-offs:

- longer/high-risk print;
- whole assembly may be discarded after one local failure;
- harder maintenance and mixed-material optimization;
- print-in-place clearances require calibration.

### `balanced-hybrid` — default

Print custom geometry and integrate proven standard parts where they add precision, wear resistance, fatigue life, sealing, or serviceability.

Typical split:

- print: housing, frame, adapter, guide, large low-speed gear, custom bushing, grip;
- buy: screws, inserts, shaft, bearing, spring, O-ring, magnet, belt, wall anchor.

### `standard-hardware`

Prioritize replaceability, known interfaces, low print risk, and conventional assembly. Use printed parts mainly as brackets, housings, and adapters around standard hardware.

## Stage gates

### Gate 0A — requirements synthesis and approval

Create `design-spec.yaml` with:

- problem and user-visible function;
- dimensions, interfaces, and coordinate convention;
- load cases and environment;
- printer/material/nozzle constraints;
- fabrication preference;
- target outputs and acceptance tests.

Present the specification as the structured review defined in `requirements-concept-approval.md`. Mark assumptions, recommendations, and open decisions; answer each consequential question with a recommended default. Stop until the user explicitly approves the current specification revision.

### Gate 0B — concept visualization and approval

Generate a concept image from the approved requirements. Provide the views needed to judge the design and map the visible features back to the specification. Stop until the user explicitly approves the concept for the same specification revision.

If requirements change, invalidate requirements, concept, and final watermark approvals and return to Gate 0A. If only the depiction changes, retain requirements approval, repeat Gate 0B, and invalidate the final watermark approval.

### Gate 1 — architecture

Produce:

- functional decomposition;
- print-vs-buy table;
- assembly sequence and maintenance path;
- tool selection and file-format plan;
- risk register.

### Gate 2 — calibration

Check whether the exact process has evidence for:

- XY hole/shaft compensation;
- Z fit and elephant-foot compensation;
- bridge and overhang limits;
- minimum wall/feature;
- snap strain and living hinge life;
- inserts, adhesives, and material conditioning.

Generate coupons before the full model if the uncertainty can change geometry.

### Gate 3 — parametric geometry

Source requirements:

- millimetres unless documented otherwise;
- centralized parameters;
- assertions for invalid combinations;
- stable named subassemblies;
- deterministic output paths;
- no hidden manual transform needed after export;
- fast preview mode separate from final export when geometry is expensive.

### Gate 4 — geometric verification

Check:

- expected body/component count;
- bounding box and critical dimensions;
- positive volume and valid solids;
- no unintended intersections or loose components;
- mesh manifold/watertight/winding state;
- fit to build volume in intended orientation;
- minimum walls/features using CAD or a dedicated thickness tool.

### Gate 5 — manufacturing verification

Check:

- load-oriented print direction;
- support generation/removal access;
- bridges and overhangs against calibrated limits;
- seam locations and first-layer contact;
- line-width-compatible walls;
- maximum volumetric flow;
- material drying, enclosure, and nozzle abrasion;
- slicer preview layer by layer.

### Gate 6 — engineering verification

Select only analyses that can influence a decision:

- kinematics and collision for mechanisms;
- hand calculation for basic beams, bolts, gears, or flexures;
- linear FEM for comparative small-deformation stiffness;
- nonlinear/contact/hyperelastic models only with suitable material data;
- thermal/CFD for heat and flow parts;
- do not mistake a generic filament datasheet for properties of the printed orientation and profile.

### Gate 7 — physical evidence

Use an escalating test ladder:

1. material/interface coupon;
2. sub-feature test;
3. subassembly;
4. full prototype;
5. proof/load/cycle/environment test;
6. limited field use;
7. qualified local revision.

### Gate 8 — watermarked candidate and final approval

Follow `watermark-release-gate.md` after the production geometry is stable:

- insert the exact `JSI-WM-001-R1` standard or compact profile into the actual model;
- prefer a recessed, process-safe mark on the print-bed-facing underside;
- rerun geometry, wall, bed-contact, and slicer checks on the marked body;
- show the finished underside, dimensions, section, and relevant slicer layers;
- obtain explicit final approval for the current specification and geometry revisions.

Do not silently omit the mark or label a package final while this gate is unapproved.

### Gate 9 — release package

Recommended tree:

```text
project/
  design-spec.yaml
  decision-log.md
  bom.yaml
  source/
  exports/
    model.step
    model.3mf
    model.stl
  profiles/
  validation/
    geometry.json
    slicer.json
    simulation/
  tests/
    plan.yaml
    results.jsonl
    photos-or-measurements/
  README.md
```

## Definition of done

A design is done only when every acceptance criterion is either:

- passed with linked evidence;
- explicitly waived by the user with risk recorded; or
- marked failed/open.

In addition, `scripts/validate_design_spec.py design-spec.yaml --require-final-approval` must pass. Unlike an ordinary acceptance criterion, the mandatory JuSt Innovation watermark and its explicit current-revision approval cannot be waived silently.
