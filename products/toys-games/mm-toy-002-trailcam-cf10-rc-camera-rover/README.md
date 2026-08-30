# MM-TOY-002 — TrailCam CF10 FPV Camera Rover

Portfolio record: `PORT-096`

Current revision: `0.4.0-draft.3` — the double-wishbone kinematics and isolated chassis-side pivot-host coupon scope pass; printable arm routing, full chassis and purchased-interface integration remain BLOCKED

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
- `concepts/trailcam-cf10-fpv-concept-v0.4.0-r2.png` — approved 0.4.0 concept reference (fully printed chassis)
- `concepts/concept-review-v0.4.0.md` — 0.4.0 requirement correspondence and interpretation limits
- `architecture/hybrid-design-plan-v0.4.0.json` — approved machine-readable 0.4.0 decomposition
- `architecture/double-wishbone-v2-interface-contract-v0.4.0.json` — confirmed joint graph, datums, deterministic motion matrix and fail-closed gates
- `architecture/architecture-report-v0.4.0.md` — 0.4.0 architecture report with decision and gate log
- `reports/design-review-v0.1.0.md` — evidence-based audit of the imported design
- `reports/cad-phase-2-corner-stack-review-v0.4.0.md` — rejected suspension/carrier integration, measured blockers and permitted continuation route
- `reports/cots-drivetrain-study-v0.4.0.md` — official-source geared-motor, right-angle transfer, locked-spool and halfshaft envelope study
- `reports/cad-phase-4-pivot-host-coupon-v0.4.0.md` — isolated front/rear x-axis pivot-host result, limits and next gate
- `validation/source-inventory.json` — exact imported-report hash and missing-artifact inventory
- `validation/corner-stack-v1-integration-2026-08-30-r4.json` — current fail-closed STEP collision, interface and kinematic evidence with exact source/export hashes
- `validation/corner-stack-v1-mesh-audit-2026-08-30/` — isolated topology reports for the six rejected DRAFT meshes; topology pass does not imply assembly pass
- `validation/double-wishbone-v2-kinematics-2026-08-30.json` — full ±10 mm / ±20 degree sweep, linkage-closure metrics and explicit current-chassis/COTS blockers
- `validation/double-wishbone-v2-pivot-host-coupon-2026-08-30.json` — B-Rep/mesh, nominal-clearance, attachment, eye-pocket, tire-sweep and arm-neck findings
- `validation/dwv2-pivot-host-mesh-audit-2026-08-30/` — independent functional-workflow mesh audits for both coupon STLs
- `validation/design-spec-validation-2026-08-30-cad-phase-4.json` — current specification schema/gate validation
- `cad/validate_corner_stack.py` — deterministic read-only integration audit; refuses evidence overwrite
- `cad/double_wishbone_v2_kinematics.py` — import-safe v2 point/axis solver and non-manufacturing STEP/preview exporter
- `cad/validate_double_wishbone_v2.py` — fail-closed fine-grid sweep and artifact validator; refuses evidence overwrite
- `cad/double_wishbone_v2_pivot_host_coupon.py` — import-safe front/rear pivot-host coupon generator
- `cad/validate_double_wishbone_v2_pivot_host_coupon.py` — fail-closed coupon geometry, mesh and sweep validator; refuses evidence overwrite
- `cad/exports/v0.4.0-draft.2-double-wishbone/` — versioned skeleton STEP, neutral preview and hashed manifest; intentionally no STL
- `cad/exports/v0.4.0-draft.3-pivot-host-coupon/` — DRAFT front/rear STEP/STL coupons, preview and hashed manifest; not vehicle parts
- `autonomy-policy.json` — guided workflow; requirements and concept remain human gates
- `docs/legacy/TrailCam_CF10_Entwurfsbericht_v0.1.0.pdf` — unchanged imported report

Concept and decomposition gates are approved, and `cad/chassis.py` provides the
first reproducible chassis DRAFT. The rejected lower-arm/carrier work remains
failure evidence. The new v2 skeleton restores two wishbones, spherical outer
joints, independent front steering, rear toe closure and a shock used only for
spring/damping. It is deliberately not printable: the current chassis has the
wrong pivot-axis topology, and wheel/hub, shock, halfshaft and joint samples are
not measured. Phase 4 therefore adds separate chassis-side x-axis pivot-host
coupons without modifying chassis v1. Their isolated scope passes, including
924 conservative tire-envelope Boolean checks, but straight arm-neck proxies
still overlap the hosts by up to 46.276 mm3. The coupon STEP/STL files are
process evidence, not vehicle parts. Exact slicing remains fail-closed until a
complete Anycubic machine/process/filament JSON profile set exists.
