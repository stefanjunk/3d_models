# Validation, simulation, and physical testing

## Verification ladder

| Level | Question | Tools |
|---|---|---|
| V0 source | Does code run and reject invalid parameters? | unit tests, assertions |
| V1 geometry | Is the intended solid/mesh present and dimensionally plausible? | CadQuery/OpenSCAD checks, Trimesh, Blender 3D Print Toolbox |
| V2 manufacturing | Can the exact printer/profile produce it? | slicer CLI/preview, coupons |
| V3 engineering | Does the model/calculation predict acceptable behavior? | hand calculation, FEM, kinematics, thermal/CFD |
| V4 coupon | Does the exact material/process reproduce the local feature? | fit/snap/bridge/insert/adhesive coupons |
| V5 assembly | Do parts fit, move, and assemble? | subassembly prototype |
| V6 service | Does it survive target load, cycles, temperature, UV, moisture, wear? | proof/cycle/environment test |

## Geometry checks

Use:

```bash
python scripts/validate_mesh.py model.stl --require-watertight --max-bodies 1
```

Check at minimum:

- body/component count;
- bounding box;
- watertightness and winding;
- positive volume;
- disconnected islands;
- critical dimensions and clearances in the source CAD;
- minimum wall thickness with a suitable thickness-analysis tool;
- collisions and assembly motion.

Mesh auto-repair must not silently change interfaces. Record before/after metrics.

## Slicing checks

- exact printer, nozzle, and material profile;
- first-layer contact and elephant foot;
- missing thin walls;
- unwanted gap fill or bridge paths;
- supports trapped in cavities;
- seams at sealing/sliding/cosmetic surfaces;
- toolpath around inserts and pauses;
- estimated mass/time and maximum volumetric flow;
- G-code viewer review.

## Simulation selection

### Hand calculations

Use first for beams, flexures, simple bolts, gear ratios, buoyancy, and thermal resistance. They expose assumptions and provide bounds.

### Linear static FEM

Useful for comparing stiffness and locating stress concentrations when:

- deformations are small;
- contacts and material behavior can be approximated;
- printed anisotropy is represented conservatively or calibrated.

Perform mesh-convergence checks and vary uncertain boundary conditions.

### Nonlinear/contact/hyperelastic FEM

Use for TPU, snap-through, large deflection, contact, and cellular compression only when material curves and solver expertise are available. A colorful result without calibrated material data is not evidence.

### Kinematics/collision

Use for drawers, hinges, dice paths, mechanisms, and assembly sequence. Clearance checks may be more valuable than stress simulation.

### Thermal/CFD

Use for ducts, electronics, hot environments, fans, and fluid paths. Validate with temperature/flow measurements where possible.

## Coupon strategy

Generate the smallest specimen that isolates the uncertain feature:

- hole/shaft tolerance ladder;
- insert boss variants;
- snap arms with length/thickness/root-radius matrix;
- gear pair strip;
- wall/roof/bridge test;
- adhesive peel/shear strip;
- TPU compression cell;
- textured surface resolution tile.

Print coupons in the same orientation, material condition, nozzle, layer height, line width, and cooling regime as the final feature.

## Structural proof tests

For a noncritical local design:

1. define working load and load directions;
2. choose a conservative proof load/safety margin appropriate to consequences;
3. fixture the real mounting interfaces;
4. load gradually behind a barrier;
5. measure deformation and inspect cracks/creep;
6. repeat/cycle where service is cyclic;
7. record failure mode and environmental condition.

Do not extrapolate one printer/material result to another without evidence.

## Example-specific checks

### Wall shelf

- verify real wall material and purchased anchors;
- proof test the module and mounting with nonfragile ballast in a safe area;
- inspect keyhole/fastener bearing and creep over time;
- do not display valuable art until evidence supports the load.

### Desk organizer

- drawer fit coupon and full travel check;
- anti-tip behavior with drawers open;
- edge/handle comfort;
- bottom flatness and felt/foot adhesion.

### Dice tower

- dice path across multiple dice sizes;
- no trapped dice or unreachable cavity;
- no sharp edges/small loose parts for intended age group;
- acoustic and impact wear check;
- engraving remains readable after slicing.
