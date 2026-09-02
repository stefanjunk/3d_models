# Concept review 0.4.1 — MM-ART-010 Berlin physical palette

Status: **informational product-variant preview; no design approval required**.

Review artifact: `concepts/berlin-display-modes-concept-v04.png`

Artifact SHA-256: `09e5941ac5918acc0fb2d85f65ca83424dbbbe7e400baaa562cf732d1237cd77`

Parameter source: `source/v0.4.1/berlin/display-mode-parameters.json`

Parameter SHA-256: `b15e259db9cadcc3b18b1d2f1a477ca31a027b0dfa0ea283a9070338b6472c88`

The sheet reuses the approved revision 0.4.0 display-mode geometry and changes only the visible physical-filament mapping. It is an optional customer/operator preview, not a new design, an approval gate, a manufacturing drawing or a calibrated color measurement.

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
- The production color bodies remain unchanged. The variant is realized by assigning their existing tools 1–4 to Oak, Mint Green, Midnight and Sky Blue in Anycubic Slicer Next or by loading the ACE slots in that order.

## Gate interpretation corrected 2026-09-02

The user explicitly clarified that a pure filament-color selection must not cause redesign. Concept v03 therefore remains the approved design authority. This v04 image simply illustrates the product colorway **Oak base → Mint Green middle plane → Midnight streets → Sky Blue boundary/accents**. Only a change to semantic color-region geometry, function, interfaces or another actual design requirement would reopen the design/concept gate.
