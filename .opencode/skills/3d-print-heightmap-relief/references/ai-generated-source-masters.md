# AI-generated source masters

## Request physical size, PPI, and pixels together

Do not ask an image generator for "300 DPI" alone. Define:
- physical authoring width and height;
- isotropic square-pixel authoring PPI;
- calculated native pixel width and height;
- whether the image is seamless/repeating;
- whether it is a single recognizable subject;
- continuous grayscale / no posterization intent.

Example for a 75×55 mm unicorn at 450 PPI:

`width_px = ceil(75/25.4*450)`

`height_px = ceil(55/25.4*450)`

The requested pixel aspect should closely match `75/55`. If the generator returns a different raster aspect, do **not** silently stretch the result into the requested rectangle.

## Registration after generation

Inspect the returned raster and persist:
- raw pixel dimensions and raster aspect;
- raw bit-depth estimate;
- embedded DPI if any;
- requested physical authoring size and PPI;
- effective raw PPI on each axis at that intended size;
- requested-versus-actual aspect mismatch;
- exact generation prompt;
- hash/provenance.

Register the raw image into a canonical 16-bit master using aspect-preserving `contain` or `cover/crop` depending on image class.

A square 1024×1024 portrait returned for a requested 60×40 mm canvas must not become a physically stretched 3:2 face. Use contain/crop and flag the generator mismatch.

## Source master versus build raster

The source master normally has square physical pixels at authoring PPI. The final surface build raster may have different X/Y physical pixel pitch because the printer/surface directions differ. Preserve physical aspect during this conversion.
