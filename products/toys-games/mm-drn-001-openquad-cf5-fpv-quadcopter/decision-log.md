# Decision log — MM-DRN-001

## 2026-08-29 — Integration and identity

- Assigned product ID `MM-DRN-001` and portfolio record `PORT-097`.
- Preserved the original zip and extracted it unchanged under `legacy-package/`.
- Retained both byte-identical loose PDF reports instead of deleting provenance.
- Retained the later loose 2026-08-14 BOM separately because it materially adds
  the RunCam Phoenix 2 SE V2, SpeedyBee TX800, antenna and goggles.
- Classified the product as `P0 Idea` under the portfolio's fail-closed artifact
  rule: controlled parametric source and analysis exist, but no neutral or
  manufacturing mesh, slicer proof or physical proof exists.

## 2026-08-29 — Shared FPV architecture

- OpenQuad is the reference for the air/ground analog-FPV component family.
- TrailCam may reuse the camera, VTX, goggles and ExpressLRS ecosystem, but not
  the serial aircraft receiver or flight-control ergonomics by default.
- Tethys may reuse ExpressLRS only on an above-water buoy; submerged control and
  video remain tethered.
- No flight geometry was generated or changed because requirements and concept
  approval remain pending.
