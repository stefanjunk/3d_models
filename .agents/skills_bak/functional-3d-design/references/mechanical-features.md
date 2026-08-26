# Mechanical feature design

## Fasteners and threads

Default hierarchy:

1. through-bolt + nut/washer for the most robust serviceable joint;
2. captive nut where rear access is limited;
3. heat-set insert for repeated assembly in a sufficiently thick boss;
4. thread-forming screw for plastics when the exact screw/hole is tested;
5. tapped or printed thread for low-cycle/light-load cases;
6. printed bolt only for large, low-load, noncritical use.

Rules:

- place screw loads across strong printed sections, not thin layer peel paths;
- add boss fillets/gussets and sufficient edge distance;
- use washers or broad bearing faces to reduce crushing;
- verify insert hole from the insert supplier and a printed coupon;
- model cosmetic threads only when required; use simplified geometry for assembly planning.

## Snap-fits and compliant mechanisms

Run:

```bash
python scripts/snapfit_calculator.py --help
```

For a simple rectangular cantilever baseline:

```text
strain ≈ 1.5 × thickness × deflection / length²
force  ≈ E × width × thickness³ × deflection / (4 × length³)
```

Use measured/credible printed modulus and allowable cyclic strain for the exact material/orientation. Add a generous root fillet and taper thickness or width to distribute strain. Print the beam so layer separation is not the primary failure mode.

Always test a coupon over the intended cycle count and environment. Fiber-filled rigid materials are generally poor first choices for highly deflected snap arms.

## Hinges

- Durable default: printed knuckles with a purchased metal pin or screw.
- Print-in-place: convenient but clearance/calibration dependent and hard to repair.
- Living hinge: best with materials such as PP and some TPU formulations; requires thin-section and fatigue testing.
- Add hard stops so the hinge does not overload the flexible element.

## Gears

Run:

```bash
python scripts/gear_pair.py --help
```

Use involute gear libraries (`cq_gears`, BOSL2, FreeCAD Gears) and record module, tooth count, pressure angle, face width, center distance, backlash, material, lubrication, speed, and torque.

Printed gears are favored for:

- prototypes;
- larger module/teeth;
- low/moderate speed;
- accessible replacement;
- low noise with suitable polymer and load.

Buy gears for high speed, high torque, precise backlash/runout, long continuous duty, or safety-critical transmission. Use metal shafts and bearings in many hybrid assemblies.

## Bearings, bushings, and shafts

- Rolling bearing: purchase and model the supplier dimensions.
- Bushing: printable for low-speed/light-duty or with a suitable tribological filament; make it replaceable.
- Shaft/pin: buy steel/aluminium/carbon rod for precision and stiffness; printed pins suit toys and light-duty large diameters.
- Avoid press-fitting a rigid bearing into a thin brittle ring without split, chamfer, fillet, and strain allowance.
- Calibrate bearing-seat dimensions and account for temperature/creep.

## Springs

Use purchased metal springs for high cycle count, stored energy, compact force, and predictable rate. Replace with a printed flexure only when:

- the deformation is geometrically bounded;
- strain and fatigue are tested;
- creep at temperature is acceptable;
- failure is safe.

## Seals

- O-rings and standard lip seals are purchased components.
- Print grooves and retainers according to the seal supplier.
- TPU gaskets can work for custom low-pressure static sealing after compression and leakage tests.
- Layer lines and seams make dynamic/high-pressure sealing unreliable without a qualified process.

## Adhesives and mixed materials

Test actual surface preparation, adhesive, filament, and environment. Useful options include:

- mechanical capture plus adhesive;
- holes/mesh keys for elastomer overmolding or glued pads;
- roughened/glue-channel surfaces;
- replaceable fabric/felt liners;
- avoid relying on an adhesive joint where peel loads dominate without a coupon.
