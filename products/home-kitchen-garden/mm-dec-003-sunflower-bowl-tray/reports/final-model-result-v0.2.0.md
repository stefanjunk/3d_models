# Final model result — MM-DEC-003 v0.2.0 digital candidate

## Outcome

The provenance-unknown legacy manufacturing geometry is blocked and excluded. The selected visible bowl body is the registered but otherwise unreconstructed geometry from Step1X-3D run `eafd0cc3-9604-4840-8aed-512cf7203124`. Only the owner-confirmed 80 × 6 mm underside disc was generated parametrically and Boolean-unioned. This is a digital candidate, not a commercial release.

Runs 001–003 are retained as rejected development evidence. Run 001 used a planar body operation later rejected by the owner. Run 002 produced multiple bodies and a rounded underside. Run 003 was watertight but had fragmented first-layer sections without a disc. None is the selected product candidate.

## Selected artifact

- path: `result/MM-DEC-003-sunflower-bowl-tray-v0.2.0-step1x-run-004-footed-digital-candidate.stl`
- SHA-256: `32c33f96c503dc104d881db8ac7194fafbfe7d169bd4abba1904c5899089c04e`
- envelope: approximately 200.000 × 195.775 × 59.157 mm
- topology: one positive watertight component, consistent winding, zero boundary/non-manifold/degenerate/duplicate faces
- mesh: 396,316 triangles; 19,815,884 bytes
- volume: approximately 720,142.228 mm³
- flat foot: 80.000 mm diameter × 6.000 mm thick
- planar bed-contact area: approximately 5,026.044 mm²

The protected Step1X body is `organic/work/run-004/01-registered-raw.stl`, SHA-256 `870761db53c81a2f9e3756b8bb502c7768f7787ce4d93c007a06d37a7aac1400`. The standalone parametric foot is `organic/work/run-004/02-parametric-foot-disc.stl`, SHA-256 `b05414897dddb81721c67ff9bc98f77038f3779013328328ff19f346c728fcc7`.

## Generation and edit boundary

The raw untextured Step1X GLB has SHA-256 `1d8648e8bf7711afa11c53c342aba896464caf747789dfa3ff02e04d6730757a`. The run, runtime snapshot and attestation bind the prompt-derived image, owned-fork commit, model snapshots, preprocessing and output hashes.

The disc dimensions were reconstructed as nominal facts from the old Anycubic 3MF metadata: 80 mm diameter and 6 mm thickness. No legacy mesh triangle was reused. The disc protrudes 0.1 mm below and overlaps 5.9 mm into the registered Step1X body before final bed registration.

The 30,000-sample bidirectional preservation check passed. Outside the authorized foot ROI, P95 and maximum displacement are approximately 0.100 mm, matching the documented rigid Z-registration; no local body reshape is evidenced. The exact triangle-distance backend was available.

## Mesh evidence

The deterministic draft mesh audit passed all declared topology, file-budget and bed-fit gates. A deterministic 1,000-point ray thickness sample measured 4.637 mm minimum, 7.224 mm P01 and 24.780 mm median against the 0.8 mm sampled threshold. This sample can miss small defects and is not a global thickness proof. No certified exact self-intersection backend was run; the watertight one-body Manifold Boolean and slicer success are supporting, not equivalent, evidence.

Read-only vertical sections at x=0 and y=0 each form one closed contour. Their centre surfaces are respectively 31.186 mm and 27.666 mm below the highest section rim, passing the declared open-depression screen. Two planes do not prove that every possible off-axis hidden pocket is absent.

## Manufacturing evidence

The selected Anycubic Slicer Next 1.3.9.4 local slice uses Kobra 3 Max / 0.4 mm hardened nozzle / 0.20 mm PETG with build-plate-only automatic tree support at 80 mm/s:

- 296 layers;
- slicer estimate 42,092 s (11 h 41 min 32 s);
- 75,912.181 mm positive filament extrusion;
- 182,590.194 mm³ calculated extrusion volume;
- conservative peak-flow estimate 12.507 mm³/s, below the declared 13.3 mm³/s analysis limit;
- zero tool changes, no parser warnings and no native slicer warning;
- exact G-code SHA-256 `95ad919c28aa02304741afb86916561cc7633f91e717e2f3e376637ef652a17c`.

The support-free control slice was rejected because Anycubic reported floating regions. The first support slice was also rejected because the 100 mm/s support setting produced a conservative 14.431 mm³/s analyzer peak. Both remain archived.

The aggregate validator is expected to remain `REVIEW_REQUIRED`: digital geometry, G-code and exact-slice gates can pass, while physical and commercial gates stay open. No printer upload or print start was performed.

An independent read-only organic-mesh review accepted the derivation as a digital prototype. It also flagged visible asymmetric, fused and wrinkled Step1X petal regions for owner aesthetic acceptance and warned that tree-support removal may damage petal surfaces. No body repair was requested or performed.

## Release boundary

The commercial audit remains `BLOCK`. A human layer/support/seam preview, supervised physical print, support-removal and edge/stability tests, final dimension/material approval, release marking, rights/IP/product-safety/export checks and signed owner approval are required before release. Food-contact, tableware, liquid-service, outdoor, child-toy and structural-use claims are outside the current scope.
