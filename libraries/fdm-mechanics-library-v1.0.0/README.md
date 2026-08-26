# FDM Mechanical Sample Library

A reproducible collection of **156 parametric, FDM-oriented mechanical samples across 39 families**. Every sample includes an OpenSCAD source, a digitally mesh-checked but physically unqualified DRAFT STL plate, separated component STLs, preview image, metadata, and German integration notes.

**Status: `1.1.0-draft.1`, experimental DRAFT.** Digital checks pass; physical qualification, exact-slicer evidence, watermark integration, and final release approval remain open.

Families 31–39 add sealing, compact-drive, service-interface, and component-fixture mechanisms. Their implementation scope and outstanding physical qualification are documented in [ROADMAP_RECOMMENDATIONS.md](ROADMAP_RECOMMENDATIONS.md).

Start with `README_DE.md` and `CATALOG.html`. Build with OpenSCAD and Python; query with `python3 tools/query_catalog.py`.

Digital validation: 156/156 plates passed watertightness, positive-volume, orientation, build-plane, component-count, and 220-mm-bed checks. Physical strength, sealing, wear, and fatigue tests remain printer-, material-, and process-specific.

Code: MIT. Generated geometry and previews: CC0-1.0.
