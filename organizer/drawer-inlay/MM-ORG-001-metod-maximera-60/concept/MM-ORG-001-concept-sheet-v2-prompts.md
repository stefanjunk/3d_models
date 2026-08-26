# MM-ORG-001 concept sheet v2 — image-generation record

Mode: built-in `image_gen`; reference-guided generation followed by one targeted built-in edit.  
Date: `2026-08-26`

## Reference roles

- `DRAFT-R1.6-plain-model-preview.png`: form-language reference only; tool layout and legacy connector geometry excluded.
- `MM-ORG-001-concept-sheet-v1.png`: sheet/palette reference only; superseded 3 × 3/tool/connector content excluded.

## Generation prompt

```text
Use case: stylized-concept
Asset type: Gate 0B industrial-design concept sheet for a printable drawer organizer
Primary request: Create one coherent landscape concept sheet for the approved MM-ORG-001 revision 0.2.0. Show a full-size drawer organizer formed by exactly FOUR independent closed rectangular trays arranged as a tight 2 by 2 set. The exact mixed set is: ONE completely open tray with no divider; ONE tray divided into exactly TWO compartments by one straight divider; TWO trays each divided into exactly FOUR compartments in a 2 by 2 pattern. Total: exactly four trays and eleven usable compartments.
Input images: Image 1 is form-language reference only: retain its calm rounded functional internal corners and premium utility feeling, but do not copy its tool layout, comb, long lane, seams, or connector geometry. Image 2 is graphic-sheet and palette reference only: retain its navy, teal, aqua, sand/beige and warm-canvas color direction, but do not copy its superseded 3 by 3 module grid, tool compartments, connector inset, labels, or dashed connector zones.
Scene/backdrop: warm canvas #FBFAF7, clean industrial design presentation.
Subject: four simple FDM-printable trays with high closed perimeter walls, lower internal dividers, subtly rounded inner corners, flat floors and flat undersides. There must be no mechanical linkage between trays.
Style/medium: polished 3D product-design render plus clean diagrammatic concept sheet, precise and restrained rather than photorealistic.
Composition/framing: left side a large three-quarter assembled overview of the four trays packed together in a 2 by 2 rectangle; right side a clear exploded three-quarter view with all four trays separated enough to count and inspect. Make the four distinct layouts unmistakable in both views. Include a small bottom-side inset only if it clearly shows a flat underside and slim OPTIONAL perimeter shim strips outside the set.
Color palette: deep navy #112431 for primary walls, teal #08777D for selected wall accents, restrained aqua #7FD5D3 for neutral callout lines only, sand/beige #C7AB82 for tray floors, warm canvas #FBFAF7 background.
Materials/textures: matte satin PETG appearance, plain surfaces, no decorative texture.
Text: no dimensions, no tolerances, no claims, no tiny annotations. If any headings are used, only the exact short headings "4 FREIE TRAYS" and "MIXED SET".
Constraints: exactly four independent trays; exactly the compartment mix stated; every tray has its own closed bottom and closed walls; visible narrow separation lines between trays; all undersides flat; no connectors of any kind; no tabs; no clips; no pegs; no holes; no dovetails; no jigsaw shapes; no interlocking lips; no bridge across seams; no shared outer frame; no tool-specific shapes; no screwdriver comb; no dedicated tool lane; no handles; no lids; no products inside; no logo; no watermark.
Avoid: nine modules, three-by-three manufacturing grid, 18-bin layout, puzzle connectors, dashed seam connectors, aqua connector blocks, floating or fused trays, perspective that hides the divider count, technical dimension labels, illegible text.
```

## Targeted edit prompt

```text
Use case: precise-object-edit
Input images: Image 1: current MM-ORG-001 concept sheet edit target
Primary request: Change ONLY the small bottom-side inset at the lower right. Remove the two teal rails/strips that appear attached to the underside of the second upside-down tray. Both upside-down tray undersides must be completely smooth, uninterrupted and flat, with no grooves, rails, feet, tabs, holes, protrusions or attached parts. Keep three slim optional teal perimeter shim strips separate and loose beside the trays, not underneath or attached to either tray.
Constraints: preserve the entire main assembled view, the exploded four-tray view, exact compartment layouts, text, colors, lighting, composition, palette swatches and inset border unchanged. The four trays must remain exactly: one open, one split into two, two split into four. No connectors of any kind. Do not add dimensions, labels, logos, watermarks, handles, lids or products.
```
