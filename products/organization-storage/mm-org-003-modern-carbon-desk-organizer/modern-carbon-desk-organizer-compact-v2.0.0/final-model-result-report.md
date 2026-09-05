# Final model result — corrective digital draft

## Outcome

MM-ORG-003 revision `2.0.0-draft.2` corrects the reproducible geometry defects in draft.1. The housing rear corners and all sorter containment corners are now closed, both drawer fascias use an 8 mm rounded XZ silhouette, the finger scoop is a real opening, the fascia no longer intersects the housing, and the coarse crossed-groove presentation has been replaced by a denser directional carbon-look cue plus a representative vertical-wall coupon.

The result is a verified **digital DRAFT**, not a print-ready or commercially released product. Mesh, corner, motion, stack and 3MF checks pass. Exact-process sliding fit, slicer paths, physical texture appearance, cycling, anti-tip behavior and final marking remain open.

## Geometry and functions

- housing: 210 × 190 × 108 mm, two drawer bays, three perimeter-frame decks, matched rounded rear cavity transitions and four top registration pegs
- drawers: one 203.1 × 181.9 × 46.5 mm body design printed twice; 205.6 × 49 × 3.2 mm fascia proud of the housing at y=-3.2..0
- drawer fascia: 8 mm front-plane radius with a functional 36 × 10 mm scoop
- sorter: 210 × 190 × 65 mm, six cells, 10 mm outside / 7.6 mm inside corner radii and four socket bosses
- true assembled envelope: 210 × 193.2 × 173 mm, including the proud fascia
- carbon cue: 3.2 mm pitch, 0.8 mm wide × 0.24 mm recessed 45-degree tow lines on named badge surfaces; opposite side faces mirror direction
- coupons: 0.30/0.45/0.60 mm fit ladder and a vertical-wall 2.4/3.2/4.0 mm texture comparison

## Interface result

The corrected nominal CAD contract is:

- drawer side clearance: 0.45 mm per side
- drawer top clearance: 3.0 mm
- drawer rear clearance: 5.7 mm
- sorter peg/socket lateral clearance: 0.35 mm per side
- stack bottoming reserve: 0.2 mm

Exact B-Rep intersections pass at nine positions over the full 181.9 mm drawer travel; every measured housing/drawer volume is 0.0 mm³. The seated sorter/housing intersection is also 0.0 mm³.

These are digital nominal values. The local calibration registry has no matching printer/material/nozzle/profile identity, so 0.45 mm must not be called proven physical play. Print and measure the fit coupon first.

## Corrective evidence

`validation/quality-audit-draft.1-to-draft.2.json` reproduces the defects from immutable STEP masters:

- draft.1 housing rear-corner probes: 0/4 material; draft.2: 4/4
- draft.1 sorter corner probes: 0/4 material; draft.2: 4/4
- draft.1 drawer/housing intersection: 2.572 mm³ at y=0 and 23.421 mm³ at the old y=0.6 preview placement
- draft.2 full-travel maximum intersection: 0.0 mm³
- draft.1 scoop probe: material; draft.2: void
- draft.1 texture coupon: 78 × 34 × 3 mm flat plate; draft.2: 78 × 12 × 34 mm vertical-wall coupon

All three production meshes pass the release-profile mesh audit:

| Part | Triangles | Watertight | Boundary/nonmanifold edges | Build-volume result |
|---|---:|---|---|---|
| Housing | 1,064 | yes | 0 / 0 | pass |
| Drawer | 2,080 | yes | 0 / 0 | pass |
| Sorter | 1,516 | yes | 0 / 0 | pass |

The 3MF passes structural validation with millimetre units, three mesh objects and four build items `[housing, drawer, drawer, sorter]`.

Both calibration meshes also pass: the six-body fit ladder is watertight and the representative texture coupon is a single watertight 78 × 12 × 34 mm vertical-wall solid.

The selected job contains 6,740 production triangles and 846,301 mm³ modeled solid volume. Those are CAD/mesh measures, not deposited material or print time. Exact slicer metrics remain `NOT_RUN`.

## Print readiness

Use `PRINT-GUIDE.md` and qualify in this order:

1. exact printer/material/nozzle/profile fit coupon;
2. vertical-wall texture coupon under three fixed light angles;
3. exact slicer run and manual layer/support/seam/path review;
4. housing + one drawer + sorter fit trial;
5. second drawer, 500-cycle test and loaded anti-tip/flatness checks.

If the 0.45 mm coupon does not give free movement without objectionable rattle, update the parameter source and rebuild every draft.2 artifact; do not hand-scale only the STL.

The Anycubic Slicer Next executable is available, but this project has no complete explicit machine/process/filament JSON profile set. The required `fdm_ci.py slice-anycubic-next` run therefore remains fail-closed rather than guessing profiles.

## Deliverables

- editable parameters and source: `model-parameters.json`, `cad/build_compact_organizer.py`
- deterministic rebuild and audit: `cad/build.py`, `cad/check_interfaces.py`, `cad/audit_quality.py`
- STEP masters: `exports/master/*2.0.0-draft.2.step`
- manufacturing meshes: `exports/manufacturing/*2.0.0-draft.2.stl`
- print set: `exports/3mf/DRAFT-MM-ORG-003-modern-carbon-compact-2.0.0-draft.2.3mf`
- evidence: `reports/build-manifest.json`, `validation/parametric-source-report.json`, `validation/interface-report.json`, `validation/*draft.2.json`
- review views: `renders/*draft.2.png`

## Kennzeichnung

The mandatory metriMade.com mark is intentionally not inserted into this corrective DRAFT. It remains a blocked final-release gate and must be added only after the production geometry, exact slice, physical fit and appearance are accepted.

## Readiness

The poor-quality draft.1 should not be printed. Draft.2 is suitable for coupon-led physical qualification and a fresh exact-profile slicer review; it is not yet a print-candidate or release artifact.
