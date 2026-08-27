# MM-ORG-016 final digital model result

Revision `0.1.0-draft.1` is a fully parametric, regenerated and slicer-preflighted draft print candidate. The user-deferred physical gate remains open, so this is not a validated production release.

## Deliverables

| Artifact | Bounds (mm) | Topology | SHA-256 |
| --- | --- | --- | --- |
| Layout-5 STL | 40 × 142 × 0.8 | 1 watertight positive-volume component; 17,344 triangles | `e0be087ff467c68daf6f8c3b57ec53e3ce8d092752eecd2848cc9055df76301c` |
| Layout-4 STL | 40 × 142 × 0.8 | 1 watertight positive-volume component; 21,216 triangles | `5391dc762fbab61adb6ec39114d3005078e8fe56cdcf4707e43ac45a5c5b6776` |
| Signal-12 STL | 40 × 142 × 0.8 | 1 watertight positive-volume component; 14,784 triangles | `9aaa1b628d46846d813a0f55403246d94a036bffcc0412e52ca9f589c8fe323e` |
| Feature-coupon STL | 90 × 32 × 0.8 | 1 watertight positive-volume component; 4,824 triangles | `661059e53d6b850b18406cf76a7a5396357bc61d192dafc017422c24e395407b` |
| Four-object 3MF | three plates plus coupon | 4 watertight objects; millimetre units | `278185766fe7d59007870f0eca601de2863996be650fbd10dbf8992a76b702aa` |

Editable STEP masters for every component and the virtual set are in `exports/master/`. The authoritative parameters are in `config/model-parameters.json`; `cad/build.py` regenerates geometry and evidence.

## Functional result

- Independent native 5 mm and 4 mm registration systems cover 120 mm without scaling one layout into the other.
- Proportional boxes, rule slots, column guides and one/two-hole identity codes use no text or font dependency.
- Twelve named `Signal-12` apertures are project-owned analytic paths with no third-party vector or mesh assets.
- Production holes/slots are at least 1.2 mm by design contract, adjacent rule-slot ligaments are at least 1.2 mm and the tightest paper-edge boundary is 2.7 mm.
- The coupon exposes 0.8, 1.0, 1.2, 1.4 and 1.6 mm slot/round variants; 0.8 and 1.0 mm are explicitly coupon-only.
- Useful production apertures reduce three-plate CAD volume by 9.902% versus solid envelope plates.

## Digital evidence

- Twelve parameter and analytic-profile tests: PASS.
- Parametric-source, mesh-generation and interface reports: PASS.
- Four independent mesh audits: watertight, positive volume, consistent winding, one component, zero boundary/nonmanifold edges and within bed/triangle/file budgets.
- 3MF structure: PASS with four build objects and millimetre units.
- Exact Anycubic Slicer Next 1.3.9.4 preflight using Kobra 3 Max / 0.4 mm / 0.20 mm Standard / Anycubic PLA: PASS, four layers, 3,262 s estimate, 16,939.98 mm3 extruded volume, 7,042.83 mm positive extrusion, 13.741 mm3/s peak flow, one tool and no native object warnings.
- Hash-bound approvals through print-candidate and aggregate draft project validation: PASS.

## Deferred gate

The coupon and plates still require physical dimension, aperture, edge, paper, pen, ink, flatness, heat-storage and 250-cycle checks. Final watermarking cannot fit the current 0.8 mm host-wall contract and remains blocked with safety/commercial release. No G-code was retained and no printer action was performed.
