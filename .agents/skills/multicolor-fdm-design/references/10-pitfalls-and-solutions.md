# Pitfalls and solutions

| Pitfall | Symptom | Solution |
|---|---|---|
| Texture has thousands of colors | impossible four-filament mapping | quantize to actual palette; preserve critical masks; report Delta-E |
| Dithering enabled | huge change count and speckled toolpaths | disable; use printable halftone cells only after a coupon |
| Tiny color islands | regions vanish or become one-line blobs | morphological cleanup in physical units; enlarge semantic details |
| Painted slicer project treated as CAD | cannot export colored parts; migration loses paint | preserve project file and create explicit solids for reusable work |
| Independent STLs lose alignment | slicer auto-arranges parts | assemble as one 3MF component object or import all as parts of one object |
| Coplanar overlapping bodies | material assignment flickers or one color wins | Boolean-cut disjoint volumes; validate overlaps |
| Color name equals slot number | wrong colors after reload/reorder | semantic IDs plus separate slot map |
| Multiple/procedural GLB materials | texture conversion imports incorrectly | bake one base-color atlas; apply transforms; remove unsupported compression |
| UV seam becomes visible color seam | stripe/discontinuity | move seam to hidden surface, bake padding, inspect sampled seam |
| Photographic shadows become black filament | false dark regions | remove lighting/AO/shadows before quantization |
| Dark purge in light infill | gray shadow through walls | disable flush into affected infill; add perimeters; increase purge |
| One purge value for all transitions | light colors contaminated or excess waste | directed transition matrix |
| Mixed polymers in permanent body | delamination or tower failure | same-family filaments or mechanical insert/support-interface strategy |
| Too-shallow inlay | color disappears after slicing/finishing | increase to at least 2–3 proven layers |
| Sloped boundary | staircase of tiny islands and many changes | simplify, orient, or convert to insert/panel seam |
| Voxel pitch chosen from texture pixels | excessive memory or false precision | choose from nozzle, line width, surface error, and memory budget |
| 3MF display color assumed physical | wrong ACE/AMS/MMU slot | explicit destination mapping and screenshot acceptance gate |
| Purge tower omitted/unstable | under-extrusion or contamination after changes | enable, size, brace/brim, and inspect its material compatibility |
| Support colors ignored | surprise transitions and waste | assign support body/interface tools explicitly |
