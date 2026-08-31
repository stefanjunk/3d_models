# NameForm 0.4.1 reinforced production architecture

Status: approved concept translated to an implementation plan. The outputs remain
`DRAFT` until the representative letter/bridge coupon and the complete pair pass
their physical gates.

## Decomposition and source of truth

- CadQuery owns the exact functional core: side blade, inward foot, ribs, gussets,
  12.0 mm glyph bodies, and the 4.0 mm recessed rear connector.
- Font outlines are generated from the bundled Noto Sans ExtraCondensed ExtraBold
  file. Glyphs are packed by their real outline distance, not by font advance
  width, so the nominal visible gap is 1.8 mm.
- The rear connector repeats each glyph silhouette at `y=10..14 mm` and adds
  only 12.0 mm wide local bridges between nearest neighboring outlines and the
  side blade. It overlaps the `y=0..12 mm` glyph bodies by 2.0 mm and extends
  2.0 mm behind them. There is no rectangular facade panel.
- The engineering STEP is the untextured B-Rep master. The manufacturing STL is
  derived by subtracting a closed, masked height-field cutter from only the
  visible glyph fronts.
- The accepted candidate-C pipeline samples the registered 1254 x 1254 16-bit
  master directly at the 0.45 mm physical mesh grid. It uses a 120 x 45 mm
  repeating patch, 24-pixel periodic edge blend, and 0.60 mm maximum depth.
  Relief fades to zero over the inner 1.2 mm outline band so the bed edge,
  counters, silhouette, and 1.8 mm gaps remain unchanged.

## Coordinate and print contract

- `X`: book-row direction; left facade extends to negative X and right facade to
  positive X.
- `Y`: shelf depth; the viewer and glyph fronts are at `-Y`; glyph bodies extend
  from `y=0` to `y=12 mm`; the rear connector begins at `y=10 mm`.
- `Z`: print-bed datum. Uppercase optical overshoots outside the typographic bed
  and cap planes are clipped at `z=0` and `z=122`; the shared baseline and true
  122 mm cap height are retained while every default glyph can start on the bed.
- Each part is printed upright, without generated support, on an Anycubic Kobra 3
  Max with a 0.4 mm nozzle and 0.12 mm layers.

## Representative coupon

The first process gate is a full-height `FA` coupon. It deliberately includes:

- the sloped A outline and its open counter;
- the exact 1.8 mm nearest-outline gap;
- the same recessed local rear bridge used in the product;
- continuous candidate-C phase across both glyphs;
- the same 12.0 mm body depth, 4.0 mm connector depth, 2.0 mm overlap,
  12.0 mm bridge width, edge taper, orientation,
  nozzle, and layer height as the complete NameForm pair.

Physical acceptance requires recognizable wood appearance, an open A counter and
visible gap, no broken bridge during normal handling, and no unintended front
panel impression. The full pair can be generated and exactly sliced in parallel,
but it remains a draft print candidate until this coupon is accepted.

## Tool and artifact plan

- `nameform_letter_only.py`: deterministic source and texture integration.
- `--name NAME --plan-only`: evaluate every character-boundary split using the
  real outline-packed width and fail closed when no half fits the fixed 350 mm
  part envelope at 122 mm cap height.
- `--name NAME [--run-id ID]`: generate an immutable personalized pair under
  `exports/v0.4.1/generated/NAME/` and its matching validation directory.
- `--left-text TEXT --right-text TEXT`: explicit uppercase halves with the same
  envelope, glyph, connector, and texture checks.
- `exports/v0.4.1/engineering/`: exact untextured STEP masters.
- `exports/v0.4.1/candidate/`: textured manufacturing STLs.
- `coupons/nameform-letter-bridge-v0.4.1/`: coupon STL, report, exact slice, and
  physical evaluation record.
- `validation/v0.4.1/`: generation report, mesh audits, exact pair slice evidence,
  preview renders, and release-gate state.

## Controlled limits

- Stop above 1,000,000 triangles or 50 MiB per manufacturing STL.
- Stop if any output has more than one connected body, a closed font counter, a
  finished glyph gap below 1.2 mm, or a changed `z=0` bed datum.
- Stop if a required exact profile is absent, Anycubic Slicer Next does not return
  native success plus G-code, or slicing exceeds the 240 second budget.
- Do not generate the 0.4.1 watermark until the revised safe underside placement
  has its own approval and evidence.

## MARITA transfer proof

The requested `MARITA` variant resolves to `MA | RITA`. `MAR | ITA` would need
363.019 mm at the approved 122 mm cap height; `MA | RITA` limits the larger part
to 348.748 mm and is the only fitting split. Revision 0.4.1 preserves the exact
candidate-C texture contract and the 0.4.0 binary-STL quantization guard. Its
reinforcement contract fails closed unless the approved glyph depth, connector
front/thickness, positive overlap, rear extension, and local bridge width are
present before any expensive geometry is generated.
