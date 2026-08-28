# Decomposition

- `rack`: authoritative lane pitch, rail registration and outer stability envelope; installed and print orientation are identical.
- `index-divider-*`: authoritative category label, tab offset, follower frame and three lane-retention pads; CAD is print-oriented and has a documented installed transform.
- `lane-gap-gauge`: three candidate slot widths around production.
- `divider-foot-key`: reproduces the exact 10.8 mm installed foot thickness.
- `labels.csv` → `label-batch.json`: normalized customer/batch data source.
- `gridfont.py`: sole glyph normalization/layout/geometry source for CAD and exact proof.
- `rack-kit.3mf` and `divider-set.3mf`: separate manufacturing build sets; no multipart assembly is fused into a monolithic mesh.
