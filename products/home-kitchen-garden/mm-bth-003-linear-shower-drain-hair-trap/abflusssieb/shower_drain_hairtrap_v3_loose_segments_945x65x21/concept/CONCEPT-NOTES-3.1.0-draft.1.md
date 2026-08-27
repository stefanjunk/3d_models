# Concept review — revision 3.1.0-draft.1

Review asset: `DRAFT-concept-sheet-3.1.0-draft.1.png`

Editable schematic source: `DRAFT-concept-sheet-3.1.0-draft.1.svg`

PNG SHA-256: `2c9abde283845c5ff5789918984b69f830b44b4d2adb9247de6b54f0f88984af`

SVG SHA-256: `9b6e64cc4cc6d9acc847e830a37181cd747c882a9be5c73705a8e77b9f1b1048`

Generation route: precise programmatic SVG schematic rendered to PNG with ImageMagick. This route was selected because the product is interface- and dimension-led.

## Requirement-to-feature correspondence

- Panel A represents exactly sixteen 52.5 mm single segments and one highlighted 105.0 mm double segment. Its eighteen circles represent the preserved eighteen catcher fields. The nominal equation is `16 × 52.5 + 1 × 105.0 = 945.0 mm`.
- Panel B represents the double segment as the same open-bottom inverted-U section extended to 105.0 mm, with two unchanged funnel-and-swirl catcher modules centered at 26.25 and 78.75 mm from its start.
- The pale-blue field in panel B represents the intended `metriMade.com` / `MM-BTH-003 · v3.1.0-draft.1` placement on one inner side wall. It does not redraw or substitute the canonical `MM-WM-001-R1` profile.
- Panel C represents the approved 3.0 mm side wall, a future 0.4 mm recess and the resulting 2.6 mm residual wall. The 4.2 mm top and 65 × 21 mm U-profile envelope remain unchanged.
- Panel D represents the retained print intent: rotate the assembly-orientation part +90 degrees about global Y, translate Z minimum to zero, and place one complete U-profile end cross-section on the build plate.
- No connector, key, snap, tongue, rail, magnet, overlap, separate fastener, or separate watermark insert is intended or shown.

## Deliberate simplifications and limits

- The diagram is a concept-gate image, not CAD, dimensional evidence, a slicer preview, or proof of printability, flow, hair retention, cleaning performance, strength, or fit.
- Funnel slopes, sieve-hole count and pitch, rib curvature, radii, wall perspective and the illustrative mark strokes are schematic. Production CAD must use `design-spec.yaml` and preserve the previously validated catcher parameters.
- The inner-side-wall callout communicates placement intent. The exact generated profile, its rotation and coordinates remain subject to the canonical generator and selector after concept approval.
- The print-orientation panel communicates the axis and bed-contact intent only. Anycubic Slicer Next review and a process-matched physical coupon remain required.

## Approval requested

Approve this concept only if the 16 + 1 decomposition, two-funnel double segment, inner-side watermark placement, U-profile wall relationship, and on-end print intent match the desired revision. Production CAD and watermark integration remain blocked until that approval is recorded.
