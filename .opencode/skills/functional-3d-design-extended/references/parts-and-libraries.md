# Standard-part and geometry libraries

## CadQuery/build123d ecosystem

### cq_warehouse

Use for parametric fasteners, nuts, washers, bearings, inserts, and matching holes in CadQuery assemblies. Prefer the library's standards and manufacturer-specific data over retyping dimensions.

### bd_warehouse

Use with build123d for similar standard-component workflows and STEP/STL export.

### cq_gears

Use for spur, helical, herringbone, ring, planetary, bevel gears, and racks where supported. Treat version/API stability as a project dependency and pin it.

### build123d

A Python/OpenCascade alternative to CadQuery with a different builder/object style. Use when its ecosystem or assembly model fits the project; do not mix style casually inside one source file.

## OpenSCAD ecosystem

### BOSL2

Useful for:

- gears and racks;
- screws/threads;
- hinges and joiners;
- attachments/orienting parts;
- shapes, masks, rounding, and textures.

Pin a known release/commit because behavior can change.

### NopSCADlib

Use its "vitamins" concept for purchased components such as bearings, motors, belts, inserts, and extrusion profiles. This is a strong model for a local design system: purchased parts are explicit assembly objects rather than redrawn approximations.

## Off-the-shelf STEP libraries

### step.parts

Search before modeling commodity hardware. Record:

- source URL and revision;
- supplier/standard/part number;
- license;
- whether dimensions were verified against the supplier drawing;
- whether the model is visual/reference or authoritative for interface generation.

A third-party STEP model does not replace the supplier datasheet.

## Gear references

Use a recognized involute generator plus gear calculations. Record at least:

- module or diametral pitch;
- tooth count;
- pressure angle;
- profile shift if any;
- center distance;
- backlash;
- face width;
- speed/torque/lubrication.

## Local parts library rules

Each reusable part entry should contain:

```json
{
  "part_id": "unique-kebab-id",
  "revision": "1.0.0",
  "status": "experimental",
  "source_type": "printed|purchased|hybrid",
  "category": "fastener-interface",
  "parameters": {},
  "interfaces": [],
  "material_process": {},
  "geometry": {},
  "provenance": {},
  "validation": [],
  "test_evidence": []
}
```

Never store only an STL. Preserve parameter source and interface metadata.
