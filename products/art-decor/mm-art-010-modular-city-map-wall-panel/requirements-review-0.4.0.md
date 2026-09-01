# Requirements review 0.4.0 — MM-ART-010 Berlin display modes

Status: **approved by Stefan on 2026-09-01; concept v03 awaiting approval; production CAD blocked**.

## User-stated correction

- The previous rectangular Berlin example has too much visually unused area.
- The product parameter set must support two deliberate map-display modes.
- `boundary_crop`: retain only the Berlin administrative area, remove all surrounding geometry and let the printed perimeter follow the irregular Berlin boundary.
- `context_outline`: keep a rectangular relief with surrounding map context and mark the Berlin administrative boundary clearly.
- Create one Berlin example of each mode.
- The reported right-hand 3MF must contain importable geometry in Anycubic Slicer Next.

## Normalized parameters

The authoritative concept parameters are stored in `source/v0.4.0/berlin/display-mode-parameters.json`.

- `display_mode` is an enum with `boundary_crop` and `context_outline`; the recommended default is `boundary_crop` because it directly removes the unwanted printed free area.
- Both modes use at most four semantic filament colors, no dithering, two permanent main prints, no rear grid and no replaceable section.
- `boundary_crop` uses the Berlin administrative polygon as the printed outer perimeter. The 600 × 400 mm value is a maximum assembled envelope, not a rectangular material requirement.
- `context_outline` retains the full 600 × 400 mm rectangular field. Its default context margin is 12% of the Berlin boundary width and height per side, adjustable from 5–30%.
- In `context_outline`, the Berlin boundary is an Orange relief band 2.4 mm wide and nominally 0.4 mm above the Black network band.
- Rear halo preparation and selected front-through paths remain mechanical preparation only; lighting is not supplied.

## Consequential controls

- The existing frozen Berlin PBF almost coincides with the Berlin state extent and is not large enough for a credible production Umland field. `context_outline` therefore fails closed until a larger immutable Berlin/Brandenburg source snapshot covers the selected context bounds.
- Perimeter clipping occurs only after every semantic layer, rear interface and protected light keep-out uses one global frame. The two halves must never be fitted or normalized independently.
- The irregular `boundary_crop` perimeter changes rear support lands, halo continuity, edge ligaments and possibly connector/hanger locations. The revision 0.3.0 decomposition cannot authorize revision 0.4.0 production geometry without a mode-aware update.
- The repaired revision 0.3.0 target-slicer project 3MFs remain the interoperability reference; every new 0.4.0 3MF must pass the same native Anycubic import-and-slice gate before handoff.

Stefan's message explicitly requested and defined both alternatives, so it is recorded as requirements approval for revision 0.4.0. Under the guided project policy, the stored visual comparison still requires a separate human concept approval before source-data expansion, production CAD, meshes or 3MF examples are generated.
