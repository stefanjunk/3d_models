# Draft final model result — MM-ORG-033 / 0.1.0-draft.1

## Outcome

GemStage 6 is complete as a **DRAFT digital print candidate**. The parametric CAD, STEP masters, manufacturing STLs, two-object 3MF, exact Anycubic G-code run, topology audits, interface checks, optimization evidence and current approval chain pass. The user-owned physical and release gates remain open.

## Product geometry

- Six independent rearward-sloped tray stations.
- Maximum declared generic tray: 86 x 145 x 12 mm.
- Functional envelope: 96 x 154 x 128 mm; print-orientation rack envelope: 128 x 154 x 96 mm.
- Rearward fall: 6 mm over 145 mm (2.37 degrees).
- Nominal clearance: 1.8 mm per side and 6.6 mm vertically.
- Split front retention leaves a 46 mm central finger, label and pour-spout opening.
- Rack and mouth coupon are each one watertight positive-volume component with zero boundary, non-manifold, degenerate and duplicate faces.
- Open scaffold CAD volume is 335,034 mm3, 82.30% below the solid-envelope proxy.

Preview: `renders/MM-ORG-033-digital-candidate.png`.

## Exact slicer evidence

- Anycubic Slicer Next 1.3.9.4.
- Anycubic Kobra 3 Max 0.4 mm machine profile, 0.20 mm Standard process profile and Anycubic PLA filament profile, all hash-bound in the report.
- Supports disabled by the exact process profile.
- 480 consistent layer markers, one tool, zero tool changes and no G-code/native warnings.
- Slicer estimate: 33,370 s (9 h 16 min 10 s).
- Analyzed extrusion: 252,285 mm3; density-converted PLA estimate: 312.8 g.
- Exact G-code SHA-256: `f79e2ea70d38e1a2942718ce53d8751dae12e0187c1d787682bec167b92d653b`.
- No printer upload or print start occurred.

## Deliverables

- Editable source: `cad/build.py`, `cad/finalize_candidate.py`, `config/model-parameters.json`.
- Neutral masters: `exports/master/`.
- Rack STL: `exports/manufacturing/DRAFT-MM-ORG-033-rack-0.1.0-draft.1.stl`.
- First-print coupon: `exports/coupons/DRAFT-MM-ORG-033-mouth-coupon-0.1.0-draft.1.stl`.
- Print set: `exports/3mf/DRAFT-MM-ORG-033-gemstage-six-0.1.0-draft.1.3mf`.
- Exact retained run: `slicer-runs/anycubic-next-1.3.9.4-kobra3max-pla-0p20-run-003/`.
- Aggregate evidence: `validation/validation-summary.json` (PASS; only optional human reviews remain).

## User print sequence

1. Measure the actual tray; do not exceed 86 x 145 x 12 mm and do not scale the STL.
2. Print the mouth coupon first and check the pour-spout/label opening and one-hand removal.
3. Preview the retained G-code for final layers, seams and bed placement, or regenerate with the same exact profiles.
4. Print the unchanged rack and complete `tests/physical-test-plan.md`.

## Remaining limits

Real-tray fit, loaded spill resistance, one-hand retrieval, 100-cycle durability, surface/edge quality, safety and commercial release are not digitally provable. Adult stationary dry craft use only; no child, transport or spill-proof claim.

`MM-WM-001-R1` is not integrated. Exact placement, marked-part coverage, slicer-layer visibility and a physical watermark coupon remain a commercial-release blocker, not a print-candidate blocker.
