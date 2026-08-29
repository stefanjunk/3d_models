# TrailCam CF10 FPV concept review — revision 0.3.0

Concept asset: `trailcam-cf10-fpv-concept-v0.3.0-r3.png`

SHA-256: `498770857824577a76a0ce651a8a00a815f16876b17a1d8990ba83a9fadd46de`

Status: **approved** by Stefan on 2026-08-29 (response: "freigegeben", concept r3)

## Revision history

- `r2` (superseded): user reported that the main view showed only one axle / two
  wheels while the underside view showed four. Confirmed as a generation artifact
  and internal inconsistency. Retained as history only.
- `r3` (current): regenerated with r2 as style/layout reference and an explicit
  constraint of two axles / four wheels, visible and consistent in every view.
  The main view now includes the far-side wheels; the underside view shows both
  axles with differentials; the exploded payload view is unchanged. See
  `../docs/user-correction-concept-wheels-2026-08-29.md`.

## Selected direction

The second concept iteration replaces the broad upper deck with a lower, open
electronics bridge. It preserves the low battery position, exposes service
access and separates the receiver, video transmitter and antenna routes.

| Approved requirement or design intent | Visible concept correspondence |
|---|---|
| Low center of gravity | Traction battery remains low in the purchased chassis |
| Measured structural load path | Two longitudinal rails and clamped adapter nodes carry the payload |
| Lightweight upper structure | Open bridge with edge beams, radiused windows and local ribs |
| Protected FPV camera | Centered front camera inside a replaceable orange guard |
| Serviceable electronics | Separate, exposed receiver and video-transmitter positions |
| RF separation | Two distinct antenna paths and short rollover loops |
| Inspectable assembly | Exploded and underside views show clamps, fasteners and access zones |

## Deliberately non-authoritative details

- The chassis, printed fasteners, PCBs and antennas are generic visual proxies.
- Antenna lengths, bends and active-element clearances are illustrative.
- Rail spacing, hardpoints, cover vents and cable paths must be based on measured
  hardware before production CAD.
- Exposed electronics communicate serviceability; the final design may add a
  minimal splash shield after thermal and antenna-clearance review.
- Pixel dimensions and proportions must not be used as manufacturing dimensions.
- Orange identifies replaceable protection and service features; it is not a
  required production color.

Concept approval authorizes the coarse assembly and the approved decomposition
direction, followed by production CAD. It does not validate strength, supplier
fit, cooling, radio range, legal RF settings, slicing or physical safety.
