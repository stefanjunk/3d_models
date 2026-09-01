# Concept review 0.4.1 — MM-ART-010 Berlin physical palette

Status: **awaiting Stefan's visual approval**.

Review artifact: `concepts/berlin-display-modes-concept-v04.png`

Artifact SHA-256: `09e5941ac5918acc0fb2d85f65ca83424dbbbe7e400baaa562cf732d1237cd77`

Parameter source: `source/v0.4.1/berlin/display-mode-parameters.json`

Parameter SHA-256: `b15e259db9cadcc3b18b1d2f1a477ca31a027b0dfa0ea283a9070338b6472c88`

The sheet reuses the approved revision 0.4.0 display-mode geometry and changes only the visible physical-filament mapping. It is appearance/gate evidence, not a manufacturing drawing or calibrated color measurement.

## Requirement-to-feature correspondence

- Oak (`FIL-0005`) fills the light base plate in both display modes.
- Mint Green (`FIL-0001`) forms the middle relief and area level.
- Midnight (`FIL-0003`) forms the darkest street-network level.
- Sky Blue (`FIL-0002`) forms the boundary and top accents; in `context_outline` it clearly traces the Berlin administrative boundary.
- `boundary_crop` still removes all printed material outside Berlin.
- `context_outline` still retains the rectangular Umland field and the approved 2.4 mm Berlin boundary relief.
- The central vertical line still indicates two permanent main prints; halo/front-through lighting remains an optional customer add-on.

## Deliberate limitations

- Display colors are visual approximations derived from the supplied spool photographs, not measured swatches.
- The concept cannot prove opacity, backlight appearance, directed purge sufficiency or contamination at dark-to-light transitions.
- Connector, hanger, rear-light and watermark geometry are intentionally not dimensionally depicted.
- Production color-body renaming and Anycubic 3MF remapping remain blocked until this concept is approved.

## Approval request

Approve concept v04 if the hierarchy reads correctly as: **Oak base → Mint Green middle plane → Midnight streets → Sky Blue boundary/accents** in both variants. Corrections to the visual hierarchy or role assignment reopen only the affected palette requirement and concept gate.
