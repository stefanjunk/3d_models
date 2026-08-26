# Textured OBJ/GLB to four-color 3MF

This example generates a watertight UV-textured cylinder, a single base-color PNG, an OBJ/MTL pair, and—when supported by the local exporter—an embedded-texture GLB. The build then:

1. inspects the source;
2. quantizes its texture to the exact four-filament palette;
3. partitions a voxelized shell into explicit color volumes;
4. exports aligned STL parts;
5. writes a standard multi-part 3MF component assembly;
6. validates the package and renders a preview.

The example uses a coarse pitch so it can run quickly. Treat it as a deterministic workflow demonstration, not as the recommended resolution for a production model.
