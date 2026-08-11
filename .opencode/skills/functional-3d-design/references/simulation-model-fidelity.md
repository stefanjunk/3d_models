# Simulation and model-fidelity guide

## First question

Ask which decision the simulation will change. If the answer is unclear, use a simpler calculation or physical coupon instead.

## Fidelity ladder

1. **Geometry and interference** — dimensions, clearances, travel, collision.
2. **Hand model** — beam, pressure, torque, gear ratio, heat balance, buoyancy.
3. **Comparative linear FEM** — relative stiffness/stress pattern under controlled assumptions.
4. **Nonlinear/contact/large deformation** — snaps, TPU, contact, buckling.
5. **Transient/thermal/CFD/dynamics** — only where heat, flow, impact, or time dependence controls function.
6. **Physical calibration/validation** — ties the model to the printed process.

## Printed-material uncertainty

Printed properties depend on:

- exact filament formulation and conditioning;
- raster direction, perimeter/infill strategy, line width, temperature, speed, and cooling;
- defects, seams, warping, moisture, and post-processing;
- temperature, time, creep, fatigue, UV, chemicals, and wear.

Use supplier data only as a starting bound. For meaningful structural prediction, test specimens printed in relevant orientations and profiles.

## Minimum FEM report

- geometry revision and simplifications;
- material model and source/calibration;
- element type and mesh-size study;
- contacts and friction;
- constraints and why they represent the real fixture;
- all load cases and combinations;
- nonlinear settings where applicable;
- displacement, stress/strain, reaction forces, and failure criterion;
- sensitivity to uncertain inputs;
- physical validation plan.

## Practical examples

### Wall shelf

A simple beam/back-panel model can compare wall thickness and ribs. It cannot validate the real wall anchor without substrate/installation data. The decisive test is the complete mounted system under proof and sustained load.

### Drawer organizer

Kinematic clearance, interference, center-of-mass/anti-tip geometry, and a fit coupon are more useful than a high-fidelity stress model.

### Dice tower

A path envelope or repeated physical dice-drop test is more useful than structural FEM. Simulate only if impact noise/wear or a complex jam mechanism needs investigation.

### TPU sole

Use nonlinear contact/hyperelastic analysis only with measured material curves and geometry. Otherwise compare variants under identical simplified compression and validate with pressure/bend/cycle tests.
