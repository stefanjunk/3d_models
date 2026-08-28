# MM-ORG-019 — Parametric label-tape cartridge rack

This digital print candidate turns measured rectangular cartridge envelopes into support-free upright storage. It includes two unbranded example presets, common side joints, per-slot adhesive label/status fields and a three-clearance fit coupon.

## Authoritative outputs

- `config/model-parameters.json` — dimensions, clearances, slot counts and printer assumptions
- `cad/build.py` — deterministic CadQuery generator
- `exports/master/` — editable STEP masters and virtual set
- `exports/manufacturing/` — compact-six and extended-five STL racks
- `exports/coupons/` — 0.30/0.50/0.70 mm per-side clearance coupon
- `exports/3mf/` — three-object millimetre 3MF build package
- `validation/print-candidate-report.json` — hash-bound digital handoff status

Run `python cad/build.py` from this folder or the repository root after editing parameters. All downstream meshes, 3MF and reports must then be regenerated. The example envelopes do not claim compatibility with any named brand or cassette family.

Physical cartridge fit, 100 retrieval cycles, connector fit, label adhesion and tip resistance are deferred to the owner's print validation. G-code is not packaged and the workflow does not upload or start a print.
