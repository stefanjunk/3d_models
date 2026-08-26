# Scope and routing in the 3D-design skill family

## Ownership

`multicolor-fdm-design` owns:

- semantic decomposition of one product into printable filament regions;
- color architecture: layer bands, inlays, shells, inserts, named solids, and slicer painting;
- actual-filament palette capture, measurement, and texture quantization;
- textured OBJ/glTF/GLB conversion into multicolor painting or true color solids;
- standard multi-part 3MF packaging and destination-slicer handoff;
- purge-transition planning, change-count reduction, and color-contamination coupons;
- multicolor-specific geometry, slicer, and physical validation.

It does not own:

- general function, loads, fits, tolerances, standard parts, or material selection outside the color-specific constraints;
- preservation and modification of an authoritative dense organic source mesh;
- construction of a new premium freeform envelope;
- conversion of imagery into depth/relief;
- printer firmware modification or automatic printer control.

## MECE routing

| Specialist | Owns | Hand-off to this skill |
|---|---|---|
| `functional-3d-design` | function, mechanical architecture, interfaces, tolerances, materials, orientation, test plan | stable bodies and design contract needing color architecture |
| `organic-mesh-functionalization` | immutable source, ROI/protected/transition/keep-out regions, mesh repair and functional edits | stable textured or vertex-colored mesh plus transforms and validation baseline |
| `parametric-freeform-surfacing` | fair curves, lofts, NURBS/SubD/FFD envelope, exact hardpoints | stable envelope and tessellation suitable for color-region construction |
| `3d-print-heightmap-relief` | image-to-depth, physical raster sampling, emboss/engrave mapping | use only if the same artwork also needs filament color assignment |
| `multicolor-fdm-design` | filament regions, palettes, 3MF, purge/change optimization | final slicer and physical validation |

## Composite sequences

### New parametric product

```text
functional contract and hardpoints
→ exact or freeform geometry
→ print split and orientation
→ semantic color map
→ disjoint named color solids
→ standard multi-part 3MF
→ slot mapping and purge planning
→ coupon and final print
```

### Existing textured AI/scan mesh

```text
archive source and hash
→ inspect/repair under organic-mesh preservation contract
→ bake transforms and preferably one texture atlas
→ actual-filament palette
→ texture quantization and island cleanup
→ fast paint handoff OR solid voxel partition
→ standard 3MF/slicer project
→ preview and coupon
```

### Image should become both relief and color

```text
stable mapping surface
→ height-map relief at physical print resolution
→ freeze resulting geometry
→ color-region design using the same semantic source mask
→ validate relief depth and color boundary independently
```

## Routing decision

Use color as **geometry** when the project is reusable, parametric, mechanically meaningful, or must survive slicer migration. Use **slicer painting** when the edit is one-off and visual. Use **layer changes** whenever all boundaries can be horizontal. Use **texture conversion** only after fixing the physical palette and filtering details below print resolution.
