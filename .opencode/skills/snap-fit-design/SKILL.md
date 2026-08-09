---
name: snap-fit-design
description: Use when a commercial FDM design contains a snap-fit, cantilever clip, compliant latch, repeated deflection, retention force, creep, or cycle-life requirement.
---

# Snap-Fit Design

## Scope

Use the calculator for transparent first-pass cantilever screening. It does not
predict anisotropic printed strength, fatigue life, creep, retention force, or
customer-printer performance.

## Workflow

1. Define material, deflection, beam length, root/tip thickness, width, root
   radius, assembly direction, service load, temperature, and cycle target.
2. Prefer a tapered beam and root radius at least half the root thickness.
3. Orient the beam so normal use does not peel layers apart.
4. Run `scripts/snapfit_calculator.py` to report nominal root strain using
   `1.5 * deflection * root_thickness / length^2`.
   Supply `--allowable-strain` from an authoritative material/process basis;
   do not invent it from the material name.
5. Generate a coupon with the real beam geometry and engagement path.
6. Measure assembly force, retention, permanent set, creep, and target cycles.

PLA is not a default repeated-flexure material. PETG is the first economical
candidate but still requires creep and cycle testing. Activate TPU, ABS/ASA, or
PA only when the functional requirements justify their process cost.

## Completion Gate

Every result is `COUPON_REQUIRED` or `REDESIGN_REQUIRED`; the formula alone can
never produce commercial release approval.
