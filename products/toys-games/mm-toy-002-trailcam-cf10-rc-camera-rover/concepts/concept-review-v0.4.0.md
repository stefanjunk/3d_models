# TrailCam CF10 FPV concept review — revision 0.4.0

Concept asset: `trailcam-cf10-fpv-concept-v0.4.0-r2.png`

SHA-256: `4751d6ddbc12f793b46ef4b549d31484e734404f7da111eae0ac7ab89d2adc5f`

Status: **approved** by Stefan on 2026-08-29 (response: "freigeben", concept v0.4.0-r2)

## Revision history

- `r1` (superseded): wheel/axle count consistent, but the assembled main view
  omitted the electronics bridge with the separated RX/VTX bays. Retained as
  history only.
- `r2` (current): bridge added above/behind the low battery with two separated
  module bays, independent cable and antenna paths; all other features retained.
  Self-reviewed against `EVAL-visual-concept-wheel-axle-consistency-001`: four
  wheels / two axles consistent in every full-vehicle view.

## Selected direction

Fully printed chassis route per approved requirements 0.4.0: printed frame,
suspension arms, steering links, battery tray, bridge, camera guard and RF
mounts; purchased tires/rims, motor/ESC/servo, radio, camera/VTX and metal
hardware.

| Approved 0.4.0 requirement or design intent | Visible concept correspondence |
|---|---|
| Fully printed chassis, no COTS/donor structure | Ribbed printed frame, skid plate, printed tray and bridge in all views |
| Printed suspension arms and steering links | Printed double-wishbone arms, links and coil-over shocks at all four corners |
| Two axles / four wheels, consistent views | Main and underside views each show four wheels on two axles |
| Battery in lowest designed frame position | Strapped pack low in the printed tray, below bridge level |
| Serviceable open bridge with separated RX/VTX bays | Bridge with two separated PCB bays, independent cable/antenna paths |
| RF separation | Two mushroom antennas on short rollover loops, separated routes |
| Protected FPV camera | Centered front camera inside replaceable orange guard |
| Replaceable wear parts and serviceability | Exploded view exposes arms, links, carriers, bridge, guard and screws |

## Deliberately non-authoritative details

- Tires, rims, PCBs, motor/servo and antennas are generic visual proxies.
- Suspension geometry, shock angles, link lengths and steering trim are
  illustrative; kinematics and clearances are authoritative only in CAD.
- Pixel dimensions and proportions must not be used as manufacturing dimensions.
- Orange identifies replaceable protection and service features; it is not a
  required production color.
- Printed layer texture is illustrative of FDM, not a surface specification.

Concept approval authorizes the coarse 0.4.0 assembly and decomposition
direction, followed by production CAD. It does not validate strength, fatigue,
supplier fit, cooling, radio range, legal RF settings, slicing or physical
safety; printed arms/links remain coupon-gated per AC-STRUCT-001.
