# Recommended future FDM mechanical-library families

Derived from the submarine reuse audit against library v1.0.0 (120 samples,
30 families). These are proposed reusable principles, not qualified parts.

## P0: high-value gaps

### 31 — Radial O-ring shaft gland

Purpose: seal a rotating model shaft through a printed wall while keeping the
O-ring, lead-in, grease reservoir and axial retainer explicit.

Proposed samples 121-124: shaft diameters 2, 3, 4 and 5 mm with corresponding
standard metric O-rings. Parameters: `shaft_d`, `oring_id`, `oring_cs`,
`radial_squeeze`, `land_l`, `lead_in`, `wall`.

Evidence needed: leakage at 0.2/1.0 m, running torque, 30/120 min temperature,
1k/10k revolutions, shaft wear and grease compatibility.

### 32 — O-ring-preloaded ramped bayonet

Purpose: extend family 20 with an axial compression ramp, hard stop, lead-in
channel and O-ring gland. This is a sealing mechanism, not a uniformly scaled
version of samples 077-080.

Proposed samples 125-128: 10, 15, 20 and 25% nominal O-ring compression at one
reference diameter. Parameters: `core_d`, `running_clearance`, `lug_w`,
`ramp_h`, `turn_deg`, `oring_id`, `oring_cs`, `compression`.

Evidence needed: closing torque, stop stress, leak test before/after 100 cycles,
vibration release, O-ring extrusion and wear.

### 33 — Compact asymmetric micro-shaft coupler

Purpose: join unlike small shafts without the 32 x 24 mm, two-M3 envelope of
family 28. Keep two bores independently parameterized.

Proposed samples 129-132: 2-to-3, 3-to-3, 3-to-4 and 3-to-5 mm. Prefer an M2
split collar or dual clamp slit; include axial stop and optional D-flat.
Parameters: `input_d`, `output_d`, `input_clearance`, `output_clearance`,
`length`, `outer_d`, `fastener`.

Evidence needed: slip torque, runout, clamp-cycle wear, crack inspection,
temperature and 1k/10k revolutions. Explicitly low-speed only.

### 34 — Crank-pin to slotted-rocker oscillator

Purpose: convert continuous motor rotation into an oscillating fin, pump,
automaton or linkage output with a retained mushroom pin and replaceable slot.

Proposed samples 133-136: crank radii 3, 4, 6 and 8 mm. Parameters:
`crank_r`, `pivot_offset`, `slot_w`, `pin_d`, `rocker_r`, `plate_t`.

Evidence needed: actual sweep vs CAD, binding at extremes, torque, slot wear,
1k/10k cycles, lubrication and pin-head retention.

## P1: useful interface families

### 35 — Dual O-ring friction piston

Purpose: adjustable sealed displacement/volume for trim bladders, dispensers,
dampers and low-pressure pumps.

Proposed samples 137-140: bores 12, 16, 20 and 24 mm. Parameters: `bore_d`,
`travel`, `oring_cs`, `groove_depth`, `groove_spacing`, `anti_loss_stop`.

Evidence needed: push/pull force wet and dry, static leakage, creep over 7 days,
water immersion, 100/1k cycles and O-ring damage during insertion.

### 36 — Captive serviceable hinge pin

Purpose: retain a removable pin without heat-peening. Use one repeatable
snap-collar or quarter-turn head principle across sizes.

Proposed samples 141-144: pin diameters 2, 3, 4 and 5 mm. Parameters:
`pin_d`, `bearing_clearance`, `head_d`, `retainer_clearance`, `grip_l`.

Evidence needed: insertion/removal force, axial pull-out, pin wear, 1k cycles,
wet contamination and accidental release.

### 37 — Compression cable gland / potted pass-through

Purpose: seal flexible wires or sensor leads through an enclosure wall. Provide
separate mechanical strain relief from the seal.

Proposed samples 145-148: cable diameters 2, 3, 4 and 6 mm. Parameters:
`cable_d`, `seal_clearance`, `compression_l`, `strain_relief`, `wall`.

Evidence needed: leak test, pull-out force, bend cycling, cable-jacket damage,
potting compatibility and thermal cycling.

## P2: component fixtures

### 38 — Parametric cylindrical-cell cradle

Purpose: reusable cell restraint with strap/snap options; electrical contacts
remain purchased and supplier-specific.

Proposed samples 149-152: AAA x1, AAA x2, AA x1 and 18650 x1. Parameters:
`cell_d`, `cell_l`, `count`, `cell_gap`, `strap_w`, `contact_keepout`.

Evidence needed: insertion force, shock retention, cell-wrapper damage,
temperature clearance and dimensional checks against actual cells.

### 39 — Sealed magnetic actuator pocket

Purpose: keep a reed/Hall switch behind a thin wall and guide an external
magnet or removable magnetic key without a hull penetration.

Proposed samples 153-156: wall thickness 1, 2, 3 and 4 mm. Parameters:
`wall_t`, `magnet_d`, `magnet_l`, `switch_keepout`, `travel`, `retention`.

Evidence needed: activation distance/orientation, false triggers, retention,
water exposure and supplier-specific magnet/switch records.

## Recommended implementation order

1. Families 31 and 32: highest reuse value for enclosures, vessels and outdoor
   electronics; also close an explicit limitation in current bayonet samples.
2. Families 33 and 34: compact model-drive primitives missing from category 08.
3. Families 35-37: sealing and service interfaces.
4. Families 38-39: useful but supplier-dependent component fixtures.

All proposed families should follow the existing four-variant package layout,
digital mesh validation and physical 100/1k/10k-cycle evidence rules. None
should be marked `qualified-local` from geometry checks alone.
