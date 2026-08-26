# FDM design patterns and conventional-part substitutions

## Integrate when the printer adds value

Useful integrated features include:

- bosses, spacers, ribs, gussets, cable routes, ducts, labels, alignment keys, handles;
- captive nut pockets, heat-set insert bosses, magnet captures, O-ring grooves;
- low-cycle snaps, flexures, print-in-place joints, compliant clamps;
- custom bearing seats around purchased bearings and shafts;
- multi-function walls that locate, protect, guide, and stiffen at once.

Integration is beneficial only when it preserves print orientation, support access, maintenance, replacement, and failure isolation.

## Replace conventional assembly selectively

| Conventional element | Printable replacement | Use printed replacement when | Keep purchased/conventional when |
|---|---|---|---|
| screw + bracket | snap-fit or slide lock | low load/cycles, calibrated material | preload, repeated cycles, safety |
| hinge + pin | living hinge or print-in-place hinge | suitable polymer, low/moderate cycles | precise/high-cycle/load-bearing |
| coil spring | flexure/compliant mechanism | space permits long low-strain beam | compact force, high cycles, stored energy |
| spacer stack | integrated bosses | geometry/orientation are robust | replaceable precision stack needed |
| machined manifold | integrated printed ducts | pressure/temp/material allow | certified pressure or smooth critical flow |
| plain bearing | printed bushing | low speed, replaceable, tested tribology | speed, life, runout, heat |
| gasket | printed TPU lip/static gasket | low pressure, broad sealing surface | dynamic/chemical/pressure/certification |

## Load-path patterns

- Align primary tensile/compressive load with continuous extrusions where possible.
- Add generous radii at ribs, snaps, and bosses; a sharp root is a crack initiator.
- Use triangular gussets rather than thick unsupported blocks.
- Spread fastener loads into multiple perimeters and local pads.
- Avoid thin towers loaded by screw leverage.
- Design sacrificial/replaceable wear pieces when the body is expensive.

## Fasteners

- Repeated service: metal screw plus heat-set insert or captive nut.
- One-time light assembly: thread-forming screw in a tested boss may be reasonable.
- Large low-cycle adjustment: printed coarse threads can work after coupon testing.
- Small preload-critical threads: buy metal hardware.
- Add tool access, insertion access, and anti-rotation geometry.

## Hinges and pins

- Durable default: printed knuckles plus metal dowel/screw.
- Print-in-place: calibrate radial/axial clearance and bridge behavior.
- Living hinge: use a compatible ductile polymer, controlled thickness/orientation, and cycle coupon; do not assume PLA behaves like molded PP.

## Gears

- Generate true involute geometry with a library.
- Define module/DP, pressure angle, tooth count, face width, center distance, backlash, bore/hub, torque, speed, life, lubrication, and material.
- Printed gears are strongest for larger module, lower speed, replaceable prototypes, and noncritical drives.
- Buy small high-speed or high-load gears and use printed housings/guards.

## Snap-fits and flexures

- Length is highly effective because strain falls approximately with the square of cantilever length for a simple baseline.
- Use tapered arms and a large root radius to distribute strain.
- Add a hard stop to prevent accidental over-deflection.
- Use measured printed properties and cycle coupons in final orientation.

## Wall mounting

- Print the custom shelf/bracket, not an unqualified universal anchor.
- Select purchased anchors and screws for the actual substrate, installation, edge distance, and load.
- Provide a screw-head/keyhole coupon and a guarded proof-load plan.
