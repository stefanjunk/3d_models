# DRAFT STL geometry validation — Revision 2

Overall result: **PASS**

Independent checks use binary STL topology, quantized shared edges, signed mesh volume, B-Rep volume comparison, connected components, and the configured Kobra 3 Max build envelope.

| Part | Triangles | Bodies | Boundary edges | Volume delta | Print dimensions (mm) | Result |
|---|---:|---:|---:|---:|---|---|
| DRAFT_R2_blind_port_plate.stl | 840 | 1 | 0 | 0.188% | 43.96 × 43.98 × 18.00 | PASS |
| DRAFT_R2_cascade_spout.stl | 924 | 1 | 0 | 0.002% | 140.00 × 62.00 × 78.00 | PASS |
| DRAFT_R2_hose_barb_flange_25.stl | 1848 | 1 | 0 | 0.253% | 43.96 × 43.98 × 43.00 | PASS |
| DRAFT_R2_hose_fit_coupon_25.stl | 3684 | 1 | 0 | 0.164% | 110.00 × 40.00 × 34.00 | PASS |
| DRAFT_R2_outlet_hose_adapter_25.stl | 2132 | 1 | 0 | 0.021% | 140.00 × 62.00 × 64.00 | PASS |
| DRAFT_R2_stage1_sediment_funnel.stl | 4720 | 1 | 0 | 0.064% | 280.00 × 280.00 × 73.00 | PASS |
| DRAFT_R2_stage1_vortex_body.stl | 10362 | 1 | 0 | 0.078% | 326.99 × 310.49 × 280.00 | PASS |
| DRAFT_R2_stage2_diffuser.stl | 1516 | 1 | 0 | 0.073% | 120.00 × 119.90 × 4.00 | PASS |
| DRAFT_R2_stage2_drop_tube.stl | 816 | 1 | 0 | 0.253% | 45.96 × 45.98 × 224.00 | PASS |
| DRAFT_R2_stage2_lamella_body.stl | 8652 | 1 | 0 | 0.057% | 300.02 × 310.49 × 280.00 | PASS |
| DRAFT_R2_stage2_lamella_cassette.stl | 2468 | 1 | 0 | 0.012% | 202.00 × 176.40 × 159.49 | PASS |
| DRAFT_R2_stage3_distributor.stl | 3668 | 1 | 0 | 0.041% | 260.00 × 260.00 × 4.00 | PASS |
| DRAFT_R2_stage3_media_basket.stl | 4624 | 1 | 0 | 0.135% | 287.14 × 287.17 × 52.00 | PASS |
| DRAFT_R2_stage3_media_body.stl | 9220 | 1 | 0 | 0.136% | 329.99 × 330.00 × 280.00 | PASS |

## Scope and limits

- PASS proves closed, consistently oriented, single-body meshes within the configured build volume and close agreement with their B-Rep volume.
- It does not prove slicer toolpaths, watertight FDM process, strength, hydraulic performance, or physical fit.
- Files remain DRAFT until the watermark regression and final release approval are complete.
