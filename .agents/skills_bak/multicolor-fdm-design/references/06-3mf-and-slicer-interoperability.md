# 3MF and slicer interoperability

## Why 3MF

The 3MF specification provides defined units, meshes, objects, components, materials/properties, colors, and an extensible package. The Materials and Properties extension supports full-color and multi-material workflows. Use 3MF rather than STL when relative placement and material intent must travel together.

## Portable subset used by this skill

The included writer creates:

- millimetre model units;
- one `basematerials` group with semantic material names and display colors;
- one mesh object per color part, using object-level `pid/pindex`;
- one component assembly that references the part objects;
- one build item referencing the assembly;
- standard OPC content types and relationships;
- optional thumbnail and metadata.

The Core specification states that component relative positions must be respected. This makes an assembly safer than importing independent STLs that a slicer might auto-arrange.

## Important limitation: display color is not a machine slot

The Core specification says base-material names convey design intent and `displaycolor` is for rendering; actual printer-material mapping belongs in printer-specific data/print tickets. Therefore:

- semantic material name: portable intent;
- display color: preview aid;
- ACE/AMS/MMU slot: destination-slicer assignment.

Never claim a standard 3MF alone guarantees physical slot mapping.

## Core base materials versus full color extension

For a small number of discrete filament bodies, object-level base materials are a practical portable representation. Per-triangle gradients, texture resources, and richer color semantics belong to the Materials and Properties extension, but consumer support varies. Explicit solids are often more reliable for desktop FDM slicers.

## Slicer project 3MF versus manufacturing 3MF

Many slicers store private project settings and paint data in a `.3mf` container. The filename extension is the same, but application-specific metadata is not guaranteed to be interpreted by another slicer.

Maintain both when needed:

- `model-portable.3mf` — explicit aligned solids and portable design intent;
- `model-anycubic-project.3mf` — final slots, profiles, purge settings, supports, and paint adjustments.

## Validation gates

A 3MF handoff passes only when:

- package relationships and model XML parse;
- all referenced object/material IDs exist;
- part meshes are valid and aligned;
- destination slicer imports one assembly rather than auto-arranged objects;
- every color body is assigned to the intended physical filament;
- sliced preview matches the reference and no body is silently merged/dropped.
