# Test reports

`self-test-report.json` is produced by `scripts/self_test.py`. It exercises image-depth preservation, mapping transforms, every implemented surface type, arbitrary sampled grids, and available optional CadQuery/OpenSCAD backends.

`validation-summary.json` records:

- JSON Schema validation for all example configs;
- static Python/macro compilation;
- full draft base → cutter → OpenSCAD Boolean validation for all three examples;
- print-quality cutter topology at the detailed mesh pitches;
- which optional applications were executed versus only statically checked.

The full generated STLs are not retained in the package because they are reproducible and substantially larger than the source/configuration files.
