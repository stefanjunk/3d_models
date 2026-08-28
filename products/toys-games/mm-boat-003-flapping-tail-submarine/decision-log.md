# MM-BOAT-003 decision log

## 2026-08-28 — Fish-silhouette revision requirements

- Baseline reviewed: the existing five circular longitudinal ribs increase the
  local bounding boxes but do not create a continuous fish silhouette. The
  fourth segment narrows while the electronics capsule widens again, and the
  current tail-fin blade lies completely below the hull axis.
- Recommended direction: use shared global side/top guide curves and registered
  elliptical sections on every hull module. Keep the modules separate at the
  hinges, but match adjacent neutral-position section widths/heights.
- Replace the five circular add-on ribs with three broad shallow crests. Add one
  restrained swept dorsal fin, two swept pectoral fins, and a symmetric rounded
  caudal fin using the existing tang and pin interface.
- Protect all hinge, seal, cap, motor, trim and drive hardpoints. Appearance and
  physical water behaviour remain human-review gates.
- Requirements status: approved by Stefan in chat on 2026-08-28 for
  `1.1.0-draft.1`. The concept-image gate is open; production geometry and
  manufacturing exports remain blocked until concept approval.

## 2026-08-28 — Fish-silhouette concept candidate

- Selected concept asset:
  `previews/concept-fish-silhouette-v1.1.0-draft.1.png`.
- The selected correction shows one nose, exactly four short articulated
  modules, one long electronics capsule, one dorsal fin, one bilateral
  pectoral-fin pair on the capsule, and a symmetric caudal fin.
- The image is an appearance target only. Hinge ears, the rocker/crank, sealing
  geometry, keel details and exact clearances remain governed by the existing
  parametric source and the approved specification.
- Concept status: approved by Stefan in chat on 2026-08-28 for
  `1.1.0-draft.1`. Production CAD is authorized; watermark, physical,
  appearance and final-release gates remain separate.

## 2026-08-28 — Parametric freeform production candidate

- Implemented natural cubic side/top guide curves and seam-registered ellipse
  lofts as additive fairings outside the unchanged pressure/functional cores.
  The lofts are split at every hinge; no surface spans a moving joint.
- Exactly three broad crests at 0/±62° replace the circular rod-like ribs.
  Crest visible height is 0.55–1.00 mm over a 5.2–8.4 mm visible width.
- Added one 3.2-mm dorsal fin and a bilateral 3.2-mm pectoral pair on the
  capsule. The pectorals cant down 45° to support the side silhouette and
  reduce horizontal support-driving undersides in keel-down orientation.
- Replaced only the tail blade with a symmetric spline caudal profile. The
  tang, socket clearance and 2.5-mm pin bore are unchanged; exact projected
  blade area is 1335.826 mm², or 1.04525 of the 1278-mm² baseline.
- Initial collision regression found additive fairing material inside the
  protected keel-plug service envelope. The unchanged bore/thread and external
  plug-head keep-out are now re-cut after every aesthetic union; the exact
  plug/capsule intersection returned to zero.
- DRAFT preflight passes. New displacement is 474.67 ml, dry mass 408.55 g and
  required ballast 59.90 g, which fits completely in the keel allocation.
- Exact Anycubic slicing remains `NOT_RUN` until an approved complete
  machine/process/PETG profile set and printer model are named. Watermark,
  appearance, physical fit/water and final-release gates remain open.
- The print-oriented nose STL contains one non-zero seam triangle with area
  4.614e-10 mm². The conservative global-scale audit labels it degenerate, but
  removing it creates a real boundary hole. The nose policy therefore permits
  exactly this one watertight-closing triangle; all other parts remain at zero,
  and the generator does not move vertices or hide the exception.

## 2026-08-28 — Canonical watermark integration

- Generated and preserved all canonical R2 Full, Compact and Micro tiers for
  product `MM-BOAT-003`, revision `1.1.0-draft.1`; the selector chose Compact
  at native scale and 0° rotation for the 70 x 22 mm flat keel land.
- Engraved the exact Compact DXF 0.40 mm into the finished capsule keel while
  preserving at least 2.0 mm edge clearance, 1.60 mm residual wall and the
  original print-bed datum. Direct Boolean evidence shows that the removed
  material is exactly the 41-glyph cutter and that no material was added.
- The canonical coupon is one watertight mesh with zero degenerate faces.
  Finished-underside and readable close-up renders are hash-tracked project
  evidence. Physical coupon, exact Anycubic preview and human watermark
  approval remain `PENDING`/`NOT_RUN`, so the watermark gate stays blocked.
