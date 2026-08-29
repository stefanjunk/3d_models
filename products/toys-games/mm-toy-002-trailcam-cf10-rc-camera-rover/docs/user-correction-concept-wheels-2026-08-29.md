# User correction — concept wheel count (2026-08-29)

- Product: MM-TOY-002 TrailCam CF10 FPV Camera Rover
- Phase: concept visualization, specification revision 0.3.0
- Exact user observation (German): "auf dem concept bild hat der rover nur eine
  achse, also zwei räder. ist das richtig?"
- Classification: depiction defect in the AI-generated concept sheet. The r2 main
  view omitted the far-side wheels (two visible wheels), while the r2 underside
  view correctly showed four wheels. Internal inconsistency, not a design intent.
- Not a requirements change: approved requirements 0.3.0 state a purchased 1:10
  COTS crawler chassis with two axles and four wheels (reference candidate Tamiya
  CC-02). The requirements gate remains approved.
- Response: generated concept r3 with an explicit two-axle / four-wheel constraint
  in every view; updated `design-spec.yaml`, `concept-review-v0.3.0.md`, README and
  decision log; r2 retained as history; concept gate re-presented for explicit
  human approval.
- Learning action: eval candidate via `3d-skill-maintainer` — concept images of
  wheeled vehicles must depict a consistent, requirement-conform wheel and axle
  count in every view of the sheet.
