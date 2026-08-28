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

## 2026-08-28 — Consolidated Anycubic print candidate

- Stefan explicitly authorized local Anycubic slicing and a consolidated 3MF;
  printer upload and print start remain outside the authorized workflow.
- Authored one Anycubic production-extension 3MF with 21 arranged build items:
  all 17 unique DRAFT STLs, with the hinge-pin input repeated to five total
  hinge pins. It embeds the selected Kobra 3 Max 0.4-mm hardened-steel machine,
  six-wall/25%-gyroid watertight process and ELEGOO Rapid PETG profiles.
- The first exact adapter run is preserved as `run-001`: a relative input path
  failed after the adapter entered its isolated work directory. The fresh
  absolute-path `run-002` passed, matching the already recorded `EXP-00003`
  candidate rather than creating a new path-handling rule.
- Anycubic Slicer Next 1.3.9.4 returned native success with 592,550 triangles,
  no native warning and one exact G-code file. The slicer footer reports 1179
  layers, 21 h 4 min 16 s normal time and 376.41 g / 291.79 cm3 PETG.
- The raw endpoint flow estimate peaks at 22.8502 mm3/s on a 0.0030-mm rounded
  segment. The hash-bound independent audit keeps the exact G-code unchanged,
  confines every value above 18.45 mm3/s below 0.05 mm, and measures 18.4172
  mm3/s as the peak for segments at least 0.05 mm long.
- The generic strict 3MF report is retained as a diagnostic failure because it
  does not traverse Anycubic's distributed production-extension resources.
  The product validator resolves all 21 external object resources, and native
  Anycubic import plus exact slicing provide the compatibility gate.
- Final GUI layer/support/seam review and physical fit, watermark, leak, trim
  and swimming tests remain human-controlled release gates.

## 2026-08-28 — Purchased-parts shopping list

- Added `SHOPPING_LIST.md` with quantities, exact fit-critical specifications,
  spares, Amazon.de search links and a receiving-inspection checklist. Dynamic
  search links are preferred over unqualified single-ASIN recommendations.
- Retained the existing N20 requirement: 3 V, 150–300 rpm, Ø3-mm smooth/D
  output shaft and at least 15 mm free shaft length. A common Amazon-listed
  GA12-N20 datasheet specifies only 3 × 9 mm, so that variant is explicitly
  rejected rather than presented as compatible.
- Specified loose AAA contacts instead of a rigid 2×AAA holder because the
  production capsule already contains two individual cell saddles.
- Sized seal purchases as NBR 70 Shore A with spares for all four exact rings.
  Supplier identity remains non-authoritative until local measurement, coupon
  fit and leak testing pass; no geometry or manufacturing artifact changed.
