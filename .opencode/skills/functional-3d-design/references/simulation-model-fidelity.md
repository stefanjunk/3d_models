# Simulation and model fidelity

Ask which decision a simulation will change. If none, use a calculation or
physical coupon instead.

Use the lowest sufficient rung:

1. geometry, clearance, travel, and collision;
2. hand calculations for beams, pressure, torque, ratio, or heat balance;
3. comparative linear FEM;
4. nonlinear contact or large deformation;
5. transient thermal, CFD, impact, or dynamics;
6. physical calibration and validation.

Printed properties depend on material formulation and conditioning, raster
direction, perimeter strategy, line width, temperature, speed, cooling,
defects, seams, moisture, creep, fatigue, UV, chemicals, and wear. Supplier
data is a starting bound, not a printed-part material model.

A useful FEM report identifies geometry revision, simplifications, material
source/calibration, element and mesh study, contacts, constraints, load cases,
nonlinear settings, displacement, stress/strain, reactions, failure criterion,
sensitivity, and a physical validation plan.
