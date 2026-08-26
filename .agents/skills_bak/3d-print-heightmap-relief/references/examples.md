# Aspect-preserving examples

## Unicorn on cylindrical gift box

Treat the unicorn as a single motif. Preserve its physical aspect and map it to a front cylindrical patch. Convert desired horizontal width in mm into angular span with `theta=W/R`. Do not repeat or stretch the unicorn to fill 360 degrees.

## Carbon texture on rounded organizer

Treat the carbon image as a physical seamless tile. Repeat it around a continuous perimeter-distance coordinate. If the organizer perimeter does not contain an integer number of tiles, prefer a partial crop or small explicit texture-scale adjustment over independent X/Y stretch.

## Wood on honeycomb shelf

Preserve a declared wood-grain physical scale. Use coordinated mappings per surface family so grain direction is deliberate. Do not infer the scale from each face's bounding-box pixel ratio.

## Person on sphere/ellipsoid

Use a bounded front patch. Preserve the face's physical aspect locally and keep critical features away from poles/high-distortion zones. Validate with a circle marker before committing to a large portrait relief.

## Writing on rounded box

Prefer vector text on a front/side patch. If writing must wrap around a rounded corner, lay it out along physical perimeter arc length. Do not independently rescale letters per face.
