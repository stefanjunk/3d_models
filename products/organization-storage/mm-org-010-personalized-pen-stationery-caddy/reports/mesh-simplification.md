# Mesh simplification decision

Decision: `not-beneficial`.

The analytic chassis manufacturing mesh contains 2,546 triangles and the nameplate 2,876; both are far below the 120,000-face and 8 MiB per-part stop limits. The extra nameplate triangles encode the protected recessed glyphs. Lossy decimation would add dimensional uncertainty to those pixels and to the slide-channel guides without a measured slicer or storage benefit.
