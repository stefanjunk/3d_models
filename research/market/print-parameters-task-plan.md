# Task Plan: Kobra 3 Max Filament Profiles

## Goal
Create a source-linked Markdown table of speed-and-quality settings for GEEETECH TPU 95A, SUNLU TPU 95A, SUNLU PETG Black, ELEGOO Rapid PETG, SUNLU PLA+ 2.0 High Speed, EONO Red/Gold/Blue Silk PLA, and GRATKIT Blue/Purple/Black Silk PLA on an Anycubic Kobra 3 Max in Anycubic Slicer Next. Cover 0.4 mm profiles at 0.12, 0.20, and 0.24 mm layers plus 0.8 mm profiles at 0.20 and 0.40 mm layers. Add separate brass, stainless-steel, and conventional hardened-steel temperature/MVS commissioning values for identical standard nozzle geometry, and document safe variable-layer-height windows by material and object type.

## Scope
- Printer: Anycubic Kobra 3 Max
- Nozzles: 0.4 mm and optional 0.8 mm replacement, each in brass, stainless steel, or conventional hardened steel with identical standard Kobra geometry
- Slicer: Anycubic Slicer Next
- Fixed layer heights: 0.12, 0.20, and 0.24 mm with 0.4 mm nozzle; 0.20 and 0.40 mm with 0.8 mm nozzle
- Configured variable-layer limits: 0.08-0.28 mm with 0.4 mm; 0.16-0.56 mm with the referenced 0.8 mm machine profile; use narrower material/object windows in practice
- Priority: Best practical balance of speed, surface quality, strength, and reliability
- Evidence: Manufacturer documentation plus online owner experiences where retrievable

## Phases
- [x] Phase 1: Define scope and evidence rules
- [x] Phase 2: Validate printer and slicer capabilities
- [x] Phase 3: Research manufacturer settings for the original six filaments
- [x] Phase 4: Research owner experiences and reconcile conflicts
- [x] Phase 5: Derive and sanity-check slicer profiles
- [x] Phase 6: Create and review the Markdown deliverable
- [x] Phase 7: Add and validate 0.4/0.24 and 0.8/0.20/0.40 profile variants
- [x] Phase 8: Add and mathematically validate both requested tri-color Silk PLA profiles and prices
- [x] Phase 9: Correct GEEETECH TPU nozzle-specific MVS evidence and add variable-layer-height guidance
- [x] Phase 10: Research ELEGOO Rapid PETG, add its five process variants, and verify an exact German offer
- [x] Phase 11: Research brass/stainless/hardened thermal and applied-flow evidence, including counterexamples
- [x] Phase 12: Add and validate nozzle-material-specific temperature and MVS commissioning columns for all seven filaments

## Key Questions
1. Which settings are genuine material limits versus broad marketing ranges?
2. What volumetric-flow and motion limits are realistic on the Kobra 3 Max?
3. How should 0.20 mm speed profiles differ from 0.12 mm quality profiles?
4. Which Anycubic Slicer Next fields map to the recommended temperatures, cooling, retraction, speed, acceleration, and flow controls?
5. Which settings require calibration because of color, moisture, ambient temperature, or individual spool variation?
6. Does evidence support an automatic temperature or flow penalty for stainless or hardened steel versus brass?

## Decisions Made
- Prefer first-party printer and filament data for safe operating bounds.
- Use owner reports to refine, not override, safe manufacturer limits without corroboration.
- Express speed limits through both feature speeds and maximum volumetric speed where possible.
- Provide starting profiles plus a short calibration sequence rather than claiming one universal optimum.
- Treat 0.4 mm MVS values as current profile caps or derived starts, not automatically proven nozzle-independent limits. Recalibrate flow ratio, PA, and MVS after fitting the 0.8 mm nozzle.
- Use 3.0 mm3/s as an uncalibrated GEEETECH TPU 0.8 engineering estimate, test 2.0-5.0 mm3/s in 0.25 steps, and retain 80-90% of the first repeatable transition.
- Follow the exact Kobra machine limits for variable layers, then narrow them by material, object geometry, MVS, and required physical shell thickness.
- Treat EONO's missing TDS and GRATKIT's conflicting high-speed/gloss claims conservatively; prioritize exact Max Silk references, owner evidence, and appearance-preserving speed.
- Treat the existing filament temperatures and MVS values as the brass baseline. Start both steel types at the brass temperature; expose only a conditional +5 C fallback within each material's range.
- Use 80% of brass MVS only as an explicitly uncalibrated steel commissioning policy. Replace it after a nozzle/material MVS and layer-strength test; do not report it as a measured alloy penalty.
- Exclude high-flow bore geometries, proprietary high-conductivity alloys, inserts, and performance coatings from the nozzle-material comparison.
- Keep ELEGOO's exact 250 C/70 C cooling profile but use conservative Kobra starts of 10 mm3/s at 0.4 and 12 mm3/s at 0.8; do not convert the 600 mm/s marketing claim into a process speed.

## Errors Encountered
- Several delegated research runs paused for assumptions; resumed them with a fully stock printer, current slicer, and balanced speed-quality objective.
- Anycubic's public Slicer Next profile bundle did not consistently expose Kobra 3 Max files; used a pinned Anycubic commit and the later OrcaSlicer Max profile merge as versioned references.
- Exact SUNLU TPU 95A owner evidence on the Kobra 3 Max was scarce; used Kobra-family mechanical evidence and clearly labeled comparable direct-drive reports.
- GEEETECH's older wiki contains a 95A wording error and aggressive retraction guidance that conflicts with its newer guide; prioritized the newer guide and Kobra owner reports.
- The pinned Anycubic Slicer Next bundle contains the 0.4/0.24 Max process but no Max 0.8 printer profile; used the exact Max 0.8 machine and 0.20/0.40 process profiles from pinned Orca commit `972dae2` as the secondary reference.
- Orca's generic 0.4/0.8 layer-height table allows 80% of nozzle diameter, but the exact Kobra 3 Max profiles use lower 70% maxima: 0.28 mm and 0.56 mm.
- A 25 mm/s GEEETECH TPU comment in a Max discussion actually described a smaller Kobra 3 and omitted extrusion geometry; retained it only as weak linear-speed/feed-path evidence, not as a measured Max MVS.
- No controlled identical-geometry Kobra comparison was found for stainless or hardened steel. Controlled V6 evidence covered hardened steel and PLA only; stainless remained a material-property plus calibration-policy case.
- Published guidance conflicts on automatic steel temperature offsets: CNC Kitchen found little quality-hardened-steel difference above about 200 C, while vendor support pages suggest +5 to +10 C conditionally. Resolved by using no automatic offset and a +5 C troubleshooting fallback.

## Status
**Complete** - Manufacturer research, owner-experience review, seven materials across five fixed nozzle/layer variants, pricing, profile derivation, variable-layer guidance, separate brass/stainless/hardened commissioning columns, counterevidence review, source review, and mathematical MVS validation are documented. Physical calibration prints remain required before treating any profile, steel MVS, temperature fallback, or adaptive window as production-qualified.
