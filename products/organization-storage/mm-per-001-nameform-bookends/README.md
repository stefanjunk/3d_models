# NameForm Bookends

Status: revision 0.4.0 has an approved letter-only concept and digitally
validated DRAFT variants. The current requested name is `MARITA`; the fixed
122 mm cap height and 350 mm internal part-envelope gate produce the
outline-balanced split `MA | RITA`.

Each bookend keeps the approved inward foot and 160 mm functional side blade.
The visible facade consists of separate 6 mm deep glyphs. A 2.4 mm recessed,
glyph-shaped rear web and local bridges connect the letters without creating a
rectangular front panel. Candidate-C wood relief is applied only to the glyph
fronts from the registered 16-bit master.

## Personalization

Preview a split without generating CAD:

```bash
python3 products/organization-storage/mm-per-001-nameform-bookends/source/v0.4.0/nameform_letter_only.py \
  --name MARITA --plan-only
```

Generate a new immutable pair:

```bash
python3 products/organization-storage/mm-per-001-nameform-bookends/source/v0.4.0/nameform_letter_only.py \
  --target pair --name MARITA --run-id run03
```

The planner evaluates actual outline-packed widths at every character boundary,
selects the smallest maximum part width that fits, and preserves one shared cap
height, baseline, 1.8 mm outline gap, connector construction, and texture scale.
Explicit uppercase halves can be supplied with `--left-text` and `--right-text`.
Existing output paths are never overwritten.

The validated scope is uppercase single-name variants using `A-Z`, digits,
hyphen, apostrophe, and `ÄÖÜẞ`. Lowercase, spaces, missing glyphs, one-character
automatic splits, and names that cannot fit the 350 mm envelope at 122 mm cap
height fail closed. Automatic cap-height reduction for longer names is not yet
implemented.

## MARITA candidate

- Manufacturing STLs and engineering STEPs:
  `exports/v0.4.0/generated/MARITA/run02/`
- Validation, renders, exact slices, and print handoff:
  `validation/v0.4.0/generated/MARITA/run02/`
- Process: Anycubic Kobra 3 Max, 0.4 mm nozzle, 0.12 mm layers, recorded PETG
  profile, upright orientation, separate sequential prints, no generated support.

Both meshes and exact Anycubic Slicer Next exports pass digitally. `RITA`
retains a slicer warning for a floating cantilever; final layer/seam inspection,
the physical appearance/handling test, the complete-pair load/slide test,
watermark integration, and final release approval remain human gates. Nothing
in this project uploads to or starts a printer.
