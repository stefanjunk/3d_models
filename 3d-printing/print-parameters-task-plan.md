# Task Plan: Kobra 3 Max Filament Profiles

## Goal
Create a source-linked Markdown table of speed-and-quality settings for GEEETECH TPU 95A, SUNLU TPU 95A, SUNLU PETG Black, and SUNLU PLA+ 2.0 High Speed on an Anycubic Kobra 3 Max in Anycubic Slicer Next. Cover 0.4 mm nozzle profiles at 0.12, 0.20, and 0.24 mm layers plus 0.8 mm nozzle profiles at 0.20 and 0.40 mm layers.

## Scope
- Printer: Anycubic Kobra 3 Max
- Nozzles: 0.4 mm and optional 0.8 mm replacement
- Slicer: Anycubic Slicer Next
- Layer heights: 0.12, 0.20, and 0.24 mm with 0.4 mm nozzle; 0.20 and 0.40 mm with 0.8 mm nozzle
- Priority: Best practical balance of speed, surface quality, strength, and reliability
- Evidence: Manufacturer documentation plus online owner experiences where retrievable

## Phases
- [x] Phase 1: Define scope and evidence rules
- [x] Phase 2: Validate printer and slicer capabilities
- [x] Phase 3: Research manufacturer settings for all four filaments
- [x] Phase 4: Research owner experiences and reconcile conflicts
- [x] Phase 5: Derive and sanity-check slicer profiles
- [x] Phase 6: Create and review the Markdown deliverable
- [x] Phase 7: Add and validate 0.4/0.24 and 0.8/0.20/0.40 profile variants

## Key Questions
1. Which settings are genuine material limits versus broad marketing ranges?
2. What volumetric-flow and motion limits are realistic on the Kobra 3 Max?
3. How should 0.20 mm speed profiles differ from 0.12 mm quality profiles?
4. Which Anycubic Slicer Next fields map to the recommended temperatures, cooling, retraction, speed, acceleration, and flow controls?
5. Which settings require calibration because of color, moisture, ambient temperature, or individual spool variation?

## Decisions Made
- Prefer first-party printer and filament data for safe operating bounds.
- Use owner reports to refine, not override, safe manufacturer limits without corroboration.
- Express speed limits through both feature speeds and maximum volumetric speed where possible.
- Provide starting profiles plus a short calibration sequence rather than claiming one universal optimum.
- Keep the proven 0.4 mm material MVS values as temporary safety caps after fitting the 0.8 mm nozzle; recalibrate flow ratio, PA, and MVS before raising them.

## Errors Encountered
- Several delegated research runs paused for assumptions; resumed them with a fully stock printer, current slicer, and balanced speed-quality objective.
- Anycubic's public Slicer Next profile bundle did not consistently expose Kobra 3 Max files; used a pinned Anycubic commit and the later OrcaSlicer Max profile merge as versioned references.
- Exact SUNLU TPU 95A owner evidence on the Kobra 3 Max was scarce; used Kobra-family mechanical evidence and clearly labeled comparable direct-drive reports.
- GEEETECH's older wiki contains a 95A wording error and aggressive retraction guidance that conflicts with its newer guide; prioritized the newer guide and Kobra owner reports.
- The pinned Anycubic Slicer Next bundle contains the 0.4/0.24 Max process but no Max 0.8 printer profile; used the exact Max 0.8 machine and 0.20/0.40 process profiles from pinned Orca commit `972dae2` as the secondary reference.

## Status
**Complete** - Manufacturer research, owner-experience review, five nozzle/layer variants, profile derivation, and technical/usability validation are finished.
