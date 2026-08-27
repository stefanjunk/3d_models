# Anycubic Slicer Next profile snapshots

These three project-local JSON files snapshot the user's selected local presets for the MM-BTH-003 draft slicer check:

- `Anycubic Kobra 3 Max 0.4 hardened steel nozzle`
- `0.20mm PETG Tool @AC K3 Max`
- `SUNLU PETG Black new @Anycubic Kobra 3 Max 0.4 nozzle`

The source files were read from the user's Anycubic Slicer Next profile directory on 2026-08-27. Their source SHA-256 values were:

- machine: `6999467dfc8f7562da667297c2e0ef44a3c1e8cebaaa2628ed6b46037d30219b`
- process: `11a5302ebd121dcfa6fad957d39d437aa797ca6d23f44e32295654d923221289`
- filament: `cedaf384ee5cabf16163009beb86f2e96b663a83640f3fda2b3978719a3ec345`

The GUI-authored source files omit the schema discriminator. Each snapshot adds only the corresponding `type` field (`machine`, `process`, or `filament`) required by the deterministic CLI adapter; all slicer settings, names, IDs, versions, and inheritance values are unchanged.

These files document a local draft-validation scope. They do not identify the physical printer unit, firmware, nozzle serial identity, or filament batch and do not qualify print quality without a physical test.
