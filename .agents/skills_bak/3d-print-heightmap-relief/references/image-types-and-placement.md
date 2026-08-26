# Image classes and placement

## Repeating textures

Examples: carbon, wood, fabric, stone, hammered metal.

Use `design-printable-surface-textures` first to decide whether the effect belongs in vector/procedural geometry, slicer/toolpaths, material/finish, or continuous relief. Continue here only when a heightmap remains necessary for irregular local height.

For the selected heightmap portion, prefer seamless repeat/crop and a stable physical tile size. A texture can wrap across rounded corners and multiple faces. Preserve orientation and tile aspect; alter repeat count before stretching.

## Single subjects

Examples: person, animal, object, unicorn, logo, photograph, writing.

Place once on a defined surface patch. Preserve physical aspect. Prefer `contain`, then controlled `cover/crop`. Avoid tight corners, poles, and high-distortion UV islands for critical features.

## Text and logos

Vector outlines are usually best for crisp primary geometry. Raster heightmaps remain useful for bevels, sculpted edges, handwritten art, and tonal relief. Preserve letter proportions and stroke width.

## Background cleanup

For people/animals/objects, background illumination can become false geometry. Mask or simplify the background, preserve the silhouette, and use a soft relief fade if the subject should merge smoothly into the base.
