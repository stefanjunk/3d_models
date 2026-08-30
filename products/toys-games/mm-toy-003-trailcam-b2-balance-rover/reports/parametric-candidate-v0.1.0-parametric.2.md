# Parametric candidate — 0.1.0-parametric.2

## Design outcome

Option A is implemented without changing the approved requirement: the complete
assembly proxy now passes the 70–110 mm center-of-mass band. The source and
geometry stage passes; manufacturing and physical release remain blocked.

## Model result

- Exactly two 120 × 40 mm wheel proxies on one common Y axis
- Five structural chassis bodies and seven removable printed modules
- Battery center raised to 136 mm; control stack remains above it with an
  unobstructed 5 mm nominal tier gap
- Raised ribbed roof protects the electronics while retaining the approved
  TrailCam open-frame language
- Camera/guard shifted 8 mm forward to preserve the upper mounting boundary
- Envelope: 187 mm long × 245 mm wide × 250 mm ground-to-top
- Wheel/frame axial clearance: 7.5 mm nominal CAD contract; diagnostic mesh
  fallback reports at least 8.71 mm
- Landing contact: 22.88°; clearance at 12° pitch: 14.32 mm
- All 12 printed bodies remain orientable within 220 × 220 × 250 mm

## Mass properties

| Metric | Revised proxy | Acceptance | Result |
|---|---:|---:|---|
| Complete mass | 1877.15 g | ≤2200 g | PASS |
| COM X | 1.69 mm | ±12 mm centered bound | PASS |
| COM Y | approximately 0.00 mm | ±3 mm | PASS |
| COM Z above axle | 71.23 mm | 70–110 mm | PASS |
| Cradle trim travel | ±12.2 mm | at least ±12 mm | PASS |

These values use provisional COTS masses and must be repeated with weighed,
registered purchased parts before integration approval. The vertical proxy COM
has only 1.23 mm margin above the lower acceptance boundary, so the PASS is not
treated as robustness evidence.

## Control-model correlation

The revised reduced-order plant represents 1.890 kg total mass versus 1.877 kg
in the CAD ledger (0.684% error). Its gravitational first moment differs by
0.275%. At 250 Hz, both idealized ±8° cases settle below 1° in 1.22 s, translate
at most 0.187 m and command at most 8.16 N against the 33.33 N transient proxy
limit. This remains simulation evidence, not firmware or powered safety proof.

## Print and release boundary

The STEP and STL artifacts are DRAFT validation proxies. Mesh topology and bed
fit are checked, but certified self-intersection is unavailable. Clearance
measurements use a diagnostic nearest-vertex fallback and remain
`REVIEW_REQUIRED`. Exact components and complete Anycubic machine/process/
filament profiles are absent, so no 3MF, G-code, print-time or filament claim is
provided. The aggregate draft project result is consequently `NOT_RUN`, while
the required geometry and control subchecks are `PASS`.
