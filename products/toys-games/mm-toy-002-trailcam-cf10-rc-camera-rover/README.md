# MM-TOY-002 — TrailCam CF10 FPV Camera Rover

Portfolio record: `PORT-096`

Current revision: `0.4.0` — requirements, concept and decomposition approved; chassis v1 is a reproducible DRAFT, suspension/drivetrain integration is BLOCKED

Lifecycle: `P0 Idea` — partial reproducible CAD exists, but no collision-free or manufacturing-authoritative vehicle assembly exists

This folder integrates the previously loose TrailCam CF10 design report into the
controlled product structure. The imported report describes a modular low-speed
1:10 RC camera rover and claims a Node.js CSG generator plus ten validated STL
files. Those claimed source and mesh deliverables were not present in the
workspace or embedded in the PDF, so the report is retained as legacy evidence,
not treated as a digital model candidate. Revision 0.3.0 defines the rover as an
FPV vehicle and aligns its analog camera/VTX and ExpressLRS ecosystem with
OpenQuad while retaining a surface-specific receiver and transmitter layout.

## Controlled files

- `design-spec.yaml` — current requirements contract and approval state
- `decision-log.md` — identity, migration and redesign decisions
- `concepts/trailcam-cf10-fpv-concept-v0.4.0-r2.png` — selected 0.4.0 concept candidate for human review (fully printed chassis)
- `concepts/concept-review-v0.4.0.md` — 0.4.0 requirement correspondence and interpretation limits
- `architecture/hybrid-design-plan-v0.4.0.json` — machine-readable 0.4.0 decomposition draft (validated, pending human approval)
- `architecture/architecture-report-v0.4.0.md` — 0.4.0 architecture report with decision and gate log
- `reports/design-review-v0.1.0.md` — evidence-based audit of the imported design
- `reports/cad-phase-2-corner-stack-review-v0.4.0.md` — rejected suspension/carrier integration, measured blockers and permitted continuation route
- `validation/source-inventory.json` — exact imported-report hash and missing-artifact inventory
- `validation/corner-stack-v1-integration-2026-08-30-r4.json` — current fail-closed STEP collision, interface and kinematic evidence with exact source/export hashes
- `validation/corner-stack-v1-mesh-audit-2026-08-30/` — isolated topology reports for the six rejected DRAFT meshes; topology pass does not imply assembly pass
- `validation/design-spec-validation-2026-08-30-cad-phase-2-r2.json` — current specification schema/gate validation (PASS with expected draft warnings)
- `cad/validate_corner_stack.py` — deterministic read-only integration audit; refuses evidence overwrite
- `autonomy-policy.json` — guided workflow; requirements and concept remain human gates
- `docs/legacy/TrailCam_CF10_Entwurfsbericht_v0.1.0.pdf` — unchanged imported report

Concept and decomposition gates are approved, and `cad/chassis.py` provides the
first reproducible DRAFT. The experimental lower-arm/carrier work does not match
the approved double-wishbone joint contract and collides with that chassis, so
it is retained only as failure evidence. No STL, STEP, 3MF or G-code may be
described as a vehicle candidate or final until a compliant suspension,
steering and drivetrain assembly passes the declared digital and physical
checks.
