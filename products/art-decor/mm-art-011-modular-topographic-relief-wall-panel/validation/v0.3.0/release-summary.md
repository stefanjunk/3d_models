# MM-ART-011 digital pilot summary — revision 0.3.0

Status: **DIGITAL PASS / HUMAN AND PHYSICAL REVIEW REQUIRED**

## Deliverables

- Harz: two 299.875 × 400 mm composite STL halves, eight named color STL bodies, two portable four-material 3MF packages and one full-resolution reference solid.
- Rheinisches Braunkohlerevier: the same deliverable set with its own immutable source and transform.
- Shared family hardware and the 0.15/0.25/0.35/0.45 mm clearance coupon remain owned by MM-ART-010 `exports/v0.3.0/interfaces/` and `coupons/v0.3.0/`.
- Every main half contains three rear-open seam-connector pockets plus one local upper-hanger or lower-standoff socket as applicable. No rear grid, magnet, adhesive interface or replaceable section exists.
- Optional customer lighting is not included. The panels only provide an 18 mm wall gap and selected protected front-through paths.

## Pilot evidence

| Pilot | Palette low → high | Global color planes | Light paths | Composite triangles left/right | 3MF |
|---|---|---:|---:|---:|---|
| Harz | Dark Green / Chocolate Brown / Caramel / Bone White | 4.2 / 4.8 / 6.0 mm | 6 | 438,586 / 439,392 | PASS ×2 |
| Rheinisch | Black / Chocolate Brown / Desert Tan / Orange | 7.6 / 7.8 / 8.2 mm | 7 | 437,952 / 439,730 | PASS ×2 |

Both 1201 × 801 UInt16 masters preserve the complete 600 × 400 mm physical aspect at 0.5 mm generation pitch. Manufacturing uses one global 801 × 535 field at approximately 0.75 mm pitch, then performs the center split. Round-trip height correlations are 0.999862 (Harz) and 0.999527 (Rheinisch). The complete manufacturing meshes reduce reference triangles by 54.56% and 54.57% while retaining the protected seam, outer perimeter, light apertures and rear interfaces.

The deliberate through-open area is 0.48% per Harz half and 0.47–0.63% per Rhenish half, well below the 12% stop. Every finished panel half is one connected, watertight, positive-volume body. Open light contours are required; any contour buffer with an interior ring is rejected to prevent a loose terrain island.

## Exact Anycubic geometry preflight

Anycubic Slicer Next 1.3.9.4 used the exact Kobra 3 Max 0.4 mm machine profile, 0.20 mm Standard process profile and Anycubic PLA Matte filament profile. These runs slice the composite geometry as one tool to establish fit, layers, path and material baseline. They do not simulate the final four ACE slots or purge tower.

| Pilot half | Result | Layers | Filament | Slicer estimate | Exact G-code SHA-256 |
|---|---|---:|---:|---:|---|
| Harz left | PASS | 50 | 127.506 m | 16 h 27 min 13 s | `1a0615121d132e581bb245a36c5b872f28bd1691e38efa2a8745fe07cdf3d427` |
| Harz right | PASS with footer review note | 43 executable | 117.114 m | 14 h 23 min 56 s | `4444c8c4e48d9817e995455b84cd46ebed4aa9825e4bb298187fa6bd95a299b4` |
| Rheinisch left | PASS | 50 | 129.310 m | 15 h 20 min 43 s | `a4286a15b6a0b7a0bfac309680572d38497ecdc00d2e48cf7e41dc5c94574765` |
| Rheinisch right | PASS | 45 | 126.694 m | 14 h 52 min 30 s | `fa69a26793ce7c9cd6dcfcc09c80b54a6b60ad865c8b760c0e59d2a608c65f1a` |

The Harz-right G-code header and executable markers both report 43 layers while the Anycubic footer reports 44. The adapter records this as `REVIEW_REQUIRED`; the required parse and layer-marker checks pass. Exact G-code is preserved and was not normalized, uploaded or started.

## Remaining gates

- Print the shared clearance coupon in the exact final connector/standoff filament, batch, nozzle, orientation and process; select 0.15/0.25/0.35/0.45 mm from measured fit.
- Load the four actual spools, verify physical swatches and opacity, map the four named 3MF bodies to ACE slots and review the final color/purge-tower preview.
- Verify first layer, peak survival, seam edge, light apertures and no unsupported islands in the destination slicer.
- Perform one-time seam assembly, installed mass proof, flatness/flushness, sharp-edge, unlit appearance and optional-light appearance tests.
- Approve and integrate the product watermark before any release.
- Electrical parts and wall fasteners are customer/installer supplied and remain outside the product claim.
