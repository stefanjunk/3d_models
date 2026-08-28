# MM-ORG-020 — Parametric belt and scarf shelf comb

Draft digital print candidate for SKU-125 (opportunity score 89.0). The family stores rolled dry soft goods directly on an existing shelf between rounded full-depth fins, so lint can escape and each roll remains visible.

## Parametric outputs

- `belt-four`: four 46 mm clear compartments, 204 × 105 × 58 mm including side tab.
- `scarf-three`: three 64 mm clear compartments, 209 × 105 × 58 mm including side tab.
- Textile-edge coupon: R0.6 / R1.0 / R1.4 ribs, marked by one/two/three holes.
- Connector key: isolates the shared 0.25 mm nominal planar-joint fit.

Edit `config/model-parameters.json`, then run `python cad/build.py`. STEP is authoritative; STL and 3MF are deterministic manufacturing derivatives. No external geometry or branded compatibility profile is used.

## Candidate state

All digital gates pass: parameter relations, one-solid B-Reps, independent topology audits, four-object 3MF and exact Anycubic Slicer Next preflight. Physical fabric snagging, retention, connector fit, cycling and shelf friction remain deferred. See `PRINT-GUIDE.md` and `validation/print-candidate-report.json`.
