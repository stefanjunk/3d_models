# Product Technical File — MM-DEC-003 v0.2.0 digital candidate

Status: **BLOCKED FOR COMMERCIAL RELEASE AND SERIES PRODUCTION**

Prepared: 2026-09-05 by Codex as AI-assisted engineering work

Manufacturer/responsible operator: unassigned

Market: EU, channel unassigned

This is a draft technical record, not a declaration of conformity or product certificate.

## Product definition

One-piece sunflower-shaped decorative catchall tray for adult indoor use with lightweight, dry, non-food objects such as keys or jewellery. It is not foodware, a plant pot, a liquid container, a toy, a load-bearing item, an outdoor product or a safety component.

The digital candidate is `07-release/artifacts/MM-DEC-003-v0.2.0-step1x-run-004-footed-digital-candidate.stl`, SHA-256 `32c33f96c503dc104d881db8ac7194fafbfe7d169bd4abba1904c5899089c04e`. Nominal units are millimetres. Measured bounds are approximately 200.000 × 195.775 × 59.157 mm.

## Design and generation chain

- Fresh prompt-bound input image with OpenAI C2PA credentials; exact source hash in the source register.
- Selected local geometry-only Step1X-3D run `eafd0cc3-9604-4840-8aed-512cf7203124`, guidance 7.5, 50 steps, 400,000 requested faces, X symmetry and smooth edge mode.
- Raw GLB preserved as immutable generation evidence.
- Uniform metric registration to a 200.0 mm maximum XY extent.
- No flower-body repair, simplification or parametric reconstruction.
- Owner-confirmed parametric disc foot: 80 mm diameter × 6 mm thickness; 5.9 mm nominal Boolean overlap and 0.1 mm pre-registration protrusion.
- No legacy mesh vertex or face reused. The old Anycubic 3MF supplied only the factual disc dimensions and owner-confirmed intent.

The selected STL has 396,316 triangles, one connected component, zero boundary/non-manifold/degenerate/duplicate faces, consistent winding and positive volume. The planar foot face spans 80 × 80 mm with approximately 5,026.044 mm² area. A 1,000-point ray-thickness sample measured 4.637 mm minimum against the 0.8 mm sampled threshold; this is not a complete global proof. A 30,000-sample exact triangle-distance comparison passed outside the foot ROI, with maximum approximately 0.100 mm matching the rigid Z registration. Read-only x=0 and y=0 sections each yield one closed contour and pass the central-depression screen; two planes do not prove the absence of every possible off-axis pocket.

## Manufacturing baseline

Digital slice baseline only; not an approved production process:

- printer: Anycubic Kobra 3 Max;
- nozzle: 0.4 mm hardened steel;
- material profile: SUNLU PETG Black, batch unresolved;
- layer height: 0.20 mm;
- orientation: 80 mm circular foot on the bed;
- support: automatic tree support, build plate only, 80 mm/s;
- slicer: Anycubic Slicer Next 1.3.9.4;
- exact machine/process/filament profile hashes retained in the selected slice report.

The selected exact-profile run reports native success without warning, one non-empty G-code, 296 executable/declared layers, zero tool changes and no parser warnings. Estimated time is 42,092 seconds, positive extrusion is 75,912.181 mm of 1.75 mm filament, calculated extruded volume is 182,590.194 mm³ and conservative peak-flow analysis is 12.507 mm³/s against a 13.3 mm³/s limit. No printer upload or print start occurred.

The support-free control run was rejected due to a native floating-regions warning. The first support run at 100 mm/s was rejected because its conservative 14.431 mm³/s peak exceeded the analysis limit. Both exact artifacts remain archived.

## Risk controls and evidence

| Risk or requirement | Current control/evidence | Status |
|---|---|---|
| Legacy Hunyuan-era licence chain | all legacy geometry excluded by hash | PASS for exclusion; old files BLOCKED |
| Unauthorized body modification | foot-only authority plus 30k protected-region comparison | PASS digital |
| Hidden/disconnected generated solids | one-body Manifold union and deterministic topology audit | PASS digital |
| Height and bed placement | 59.157 mm height; min Z 0; 80 mm circular foot | PASS digital; owner size confirmation open |
| Rocking/tipping | planar disc only; physical flatness and 10° loaded tilt not tested | BLOCK |
| Sharp or snagging petals | render and sampled thickness review only; physical tests not run | BLOCK |
| Floating regions/support burden | warning-free exact slice with build-plate-only tree support; human preview not signed | REVIEW REQUIRED |
| Exact self-intersection | no certified backend available; topology/Boolean/slicer are supporting evidence | REVIEW REQUIRED |
| Material/process repeatability | PETG profile selected; lot, drying and printer capability not qualified | BLOCK |
| Food/liquid misuse | prohibited-use scope and future warning required | BLOCK until labelling approved |
| Commercial IP/design similarity | no searches or competent review | BLOCK |
| Traceability mark | metriMade mark not yet placed or approved | BLOCK |

## Required physical qualification

Before any print-candidate or commercial status:

1. inspect and sign the final slicer layers, tree supports, seam, first layer, overhangs and seed-detail continuity;
2. print at least one full prototype with recorded machine, firmware, material lot, drying, plate and environment;
3. record support placement/removal and any surface damage;
4. measure XY/Z dimensions and base flatness on a defined instrument/surface;
5. test rocking, 10° quasistatic tilt with declared dry load, manual emptying and edge/fabric snagging;
6. inspect cracks, stringing, weak tips and cleaning accessibility;
7. select the final yellow filament and re-slice/requalify if it differs from the black PETG baseline.

## Regulatory, label and release gaps

The exact EU product classification and GPSR obligations have not been completed. Manufacturer identity, postal/electronic address, product/batch identifier, warnings, language set, online-offer information, incident contact, consumer digital terms, tax/EPR and export screening are missing. CE applicability has not been decided and no conformity mark is authorized.

Required future user information must at least state the intended dry non-food use, prohibited food/liquid/toy/outdoor/structural uses, material and temperature/cleaning limits, version/units/orientation, validated printer/process scope, and that machine-specific G-code must not be used on another configuration.

## Final decision

Engineering geometry and headless slice evidence support continued prototyping only. Commercial manufacture, publication, shipment and sale remain prohibited until the rights, physical, market, marking and signed approval gates in `05-clearance/RIGHTS-CLEARANCE.md` and `08-approvals/release-approval.json` pass.
