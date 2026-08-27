# Final model result — digital geometry stage

## Outcome

MM-ORG-003 revision `2.0.0-draft.1` is complete as a fully parameterized, common-printer-sized digital geometry package. It includes editable CadQuery source, JSON parameters, STEP masters, manufacturing STLs, a structurally valid multi-object 3MF, two process coupons and a reproducible interface contract.

The result remains a **DRAFT digital engineering candidate**, not a physically validated or commercially released product. Exact slicer preflight was not run because no supported slicer CLI and destination profile are installed; physical validation was explicitly deferred by the user.

## Selected architecture

- one 210 × 190 × 108 mm framed two-bay housing
- one identical drawer design printed twice
- one removable 210 × 190 × 65 mm top sorter with a 2 × 3 grid
- four tapered peg/socket registrations between housing and sorter
- sparse procedural twill grooves on cosmetic badge fields only
- separate drawer-clearance and twill-scale coupons

The assembled envelope is 210 × 190 × 173 mm. Every production part fits the 220 × 220 × 250 mm target build volume in its documented orientation.

## Parametric interfaces

- drawer side clearance: 0.45 mm each side
- drawer vertical clearance: 3.0 mm
- drawer depth contract: 3.2 + 181.9 + 2.5 = 187.6 mm cavity depth
- stack peg/socket lateral clearance: 0.35 mm each side
- socket bottoming reserve: 0.2 mm
- sorter grid: six cells, nominally 101.7 × 60.53 mm each before corner effects

`validation/interface-report.json` records these checks with hashes of the current parameter and source files.

## Optimization result

The compact framed selection has 843,891 mm³ of modeled production volume versus 1,122,373 mm³ for the conservative compact untextured comparator, a 24.81% reduction. Its 4,572-job-triangle burden is 99.85% below the dense v1.1.2 manufacturing job. Procedural grooves replaced the prior dense raster-relief dependency.

The derived 1,046 g PLA-equivalent figure is CAD volume × density, not a slicer material estimate. No print-time or deposited-material claim is made.

## Evidence and limitations

Passing digital evidence:

- all five manufacturing/coupon meshes are watertight, consistently wound and positive-volume
- production and coupon meshes fit their configured build-volume policies
- the 3MF package has valid standard structure and the expected four build items
- the parametric source, assembly envelope and nominal interface checks pass
- the autonomous approval chain is valid through `interface-validation`

Open evidence:

- exact slicer preflight and G-code analysis
- process-matched fit and texture coupons
- unchanged full print
- drawer travel/cycle testing and 0.75 kg target-load checks
- loaded anti-tip, flatness, stack retention and appearance checks
- safety, rights and commercial release review

The blocked slicer and print-candidate events are retained in `validation/agent-approvals.json`; they document the intentionally open boundary instead of implying that validation occurred.

## Primary outputs

- `exports/3mf/DRAFT-MM-ORG-003-modern-carbon-compact-2.0.0-draft.1.3mf`
- `exports/manufacturing/DRAFT-MM-ORG-003-compact-housing-2.0.0-draft.1.stl`
- `exports/manufacturing/DRAFT-MM-ORG-003-compact-drawer-print-twice-2.0.0-draft.1.stl`
- `exports/manufacturing/DRAFT-MM-ORG-003-compact-top-sorter-2.0.0-draft.1.stl`
- `exports/manufacturing/DRAFT-MM-ORG-003-compact-fit-coupon-2.0.0-draft.1.stl`
- `exports/manufacturing/DRAFT-MM-ORG-003-compact-texture-coupon-2.0.0-draft.1.stl`
- `renders/MM-ORG-003-compact-digital-candidate.png`

## Handoff

Use `PRINT-GUIDE.md` for the physical sequence. If a coupon changes any fit parameter, rebuild all artifacts and rerun the digital evidence before the full assembly print. A successful physical print must be recorded against this exact revision and artifact hashes before lifecycle advancement beyond P2.
