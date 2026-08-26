# Implemented mechanism extension and qualification roadmap

This roadmap was derived from integrating the library into an articulated,
motorized and water-resistant toy submarine. Families 31–39 and samples
121–156 are now implemented and have passed the library's digital mesh and
package checks. They are not physically qualified parts: the evidence listed
for each family remains mandatory before product-specific release.

## P0: high-value gaps

### Family 31 — Radial O-ring shaft gland

Seal a rotating model shaft through a printed wall while making the O-ring,
lead-in, grease reservoir and axial retainer explicit.

Implemented samples 121-124: shaft diameters 2, 3, 4 and 5 mm. Parameters:
`shaft_d`, `oring_id`, `oring_cs`, `radial_squeeze`, `clearance`, `land_l`,
`lead_in`, `grease_reservoir`, `wall`.

Required evidence: leakage at 0.2/1.0 m, running torque, 30/120 minute
temperature, 1k/10k revolutions, shaft wear and grease compatibility.

### Family 32 — O-ring-preloaded ramped bayonet

Extend family 20 with axial compression ramp, hard stop, lead-in channel and
O-ring gland. This is a sealing mechanism, not a scaled 077-080 STL.

Implemented samples 125-128: 10, 15, 20 and 25% nominal O-ring compression.
Parameters: `core_d`, `running_clearance`, `lug_w`, `ramp_h`, `turn_deg`,
`oring_id`, `oring_cs`, `radial_squeeze`, `hard_stop`.

Required evidence: closing torque, stop stress, leak test before/after 100
cycles, vibration release, O-ring extrusion and wear.

### Family 33 — Compact asymmetric micro-shaft coupler

Join unlike small shafts without the 32 x 24 mm, two-M3 envelope of family 28.
Keep both bores independently parameterized.

Implemented samples 129-132: 2-to-3, 3-to-3, 3-to-4 and 3-to-5 mm. The samples use an M2
split collar or dual clamp slit with axial stop and optional D-flat. Parameters:
`input_d`, `output_d`, `input_clearance`, `output_clearance`, `length`,
`outer_d`, `fastener`, `axial_stop`.

Required evidence: slip torque, runout, clamp-cycle wear, crack inspection,
temperature and 1k/10k revolutions. Explicitly low-speed only.

### Family 34 — Crank-pin to slotted-rocker oscillator

Convert continuous rotation into an oscillating fin, pump, automaton or linkage
output with a retained mushroom pin and replaceable slot.

Implemented samples 133-136: crank radii 3, 4, 6 and 8 mm. Parameters: `crank_r`,
`pivot_offset`, `slot_w`, `pin_d`, `rocker_r`, `plate_t`.

Required evidence: actual sweep vs CAD, binding, torque, slot wear, 1k/10k
cycles, lubrication and pin-head retention.

## P1: sealing and service interfaces

### Family 35 — Dual O-ring friction piston

Adjust sealed displacement/volume for trim bladders, dispensers, dampers and
low-pressure pumps.

Implemented samples 137-140: bores 12, 16, 20 and 24 mm. Parameters: `bore_d`,
`travel`, `oring_id`, `oring_cs`, `groove_depth`, `groove_spacing`, `lead_in`,
`anti_loss_stop`.

Required evidence: wet/dry force, static leakage, seven-day creep, immersion,
100/1k cycles and O-ring insertion damage.

### Family 36 — Captive serviceable hinge pin

Retain a removable pin without heat-peening, using one repeatable snap-collar
or quarter-turn head principle.

Implemented samples 141-144: pin diameters 2, 3, 4 and 5 mm. Parameters: `pin_d`,
`bearing_clearance`, `head_d`, `retainer_clearance`, `grip_l`.

Required evidence: insertion/removal force, axial pull-out, wear, 1k cycles,
wet contamination and accidental release.

### Family 37 — Compression cable gland / potted pass-through

Seal flexible wires or sensor leads through an enclosure wall, separating
strain relief from the seal.

Implemented samples 145-148: cable diameters 2, 3, 4 and 6 mm. Parameters:
`cable_d`, `seal_clearance`, `compression_l`, `thread_d`, `pitch`,
`strain_relief`, `wall`.

Required evidence: leakage, pull-out force, bend cycling, jacket damage,
potting compatibility and thermal cycling.

## P2: component fixtures

### Family 38 — Parametric cylindrical-cell cradle

Implemented samples 149-152: AAA x1, AAA x2, AA x1 and 18650 x1. Electrical
contacts remain purchased and supplier-specific. Parameters: `cell_d`,
`cell_l`, `count`, `cell_gap`, `clearance`, `strap_w`, `contact_keepout`.

Required evidence: insertion force, shock retention, wrapper damage,
temperature clearance and checks against actual cells.

### Family 39 — Sealed magnetic actuator pocket

Guide an external magnet or key while a reed/Hall switch remains behind an
unpenetrated wall.

Implemented samples 153-156: wall thickness 1, 2, 3 and 4 mm. Parameters:
`wall_t`, `magnet_d`, `magnet_l`, `switch_keepout`, `travel`, `retention`,
`clearance`.

Required evidence: activation distance/orientation, false triggers, retention,
water exposure and supplier-specific magnet/switch records.

## Implementation status

1. Families 31-32: implemented as enclosure, vessel and outdoor-electronics sealing samples.
2. Families 33-34: implemented as compact model-drive primitives in category 08.
3. Families 35-37: implemented as serviceable sealing and retention interfaces.
4. Families 38-39: implemented as supplier-dependent component fixtures.

Every family uses the four-variant package layout and passed automated mesh and
package validation. Calibration prints and the listed force, leakage,
100/1k/10k-cycle, wear, and supplier-specific checks remain open. Geometry
checks alone must never promote a sample to physically qualified.
