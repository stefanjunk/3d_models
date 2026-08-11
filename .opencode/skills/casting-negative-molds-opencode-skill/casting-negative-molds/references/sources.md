# Research sources

Accessed 2026-08-09 unless otherwise noted. Product data, software manuals, laws, and standards change; verify the current version before production.

## OpenCode and Agent Skills

1. **OpenCode — Agent Skills documentation.** Skill discovery paths, `SKILL.md` frontmatter, and activation behavior.  
   https://opencode.ai/docs/skills/

2. **Agent Skills specification.** Standard directory layout with `SKILL.md`, `scripts/`, `references/`, and `assets/`; progressive disclosure; relative file references; validation.  
   https://agentskills.io/specification

3. **Agent Skills best practices.** Concise main instructions and focused supporting references.  
   https://agentskills.io/best-practices

## Ceramic slip casting and plaster molds

4. **Digitalfire — Slip Casting.** Describes deflocculated ceramic slurry in absorbent plaster molds, wall buildup by water extraction, draining, and shrink-assisted release.  
   https://digitalfire.com/glossary/slip+casting

5. **Schunk Technical Ceramics — Slip Casting.** Industrial overview of casting into porous, absorbent plaster molds.  
   https://www.schunk-technical-ceramics.com/en/know-how/manufacturing-processes/shaping/slip-casting

6. **Digitalfire — 3D-printed coffee mug slip-casting mold/case workflow.** Practical examples of printed tooling used to make plaster mold components.  
   https://digitalfire.com/project/60

7. **Digitalfire — Mold pour spout.** Removable spouts/reservoirs and maintaining slip at the rim during casting.  
   https://digitalfire.com/glossary/pour+spout

8. **Ceramic Arts Network — “Mold Making 101.”** Multipart plaster mold sections, registration keys, separator, drying, seam cleanup, and undercut checks.  
   https://ceramicartsnetwork.org/ceramics-monthly/ceramics-monthly-article/Monthly-Methods-Mold-Making-101

9. **Digitalfire — Drying shrinkage.** Background on body shrinkage and release; values are body/process specific.  
   https://digitalfire.com/glossary/drying+shrinkage

10. **Digitalfire — Slip viscosity / specific gravity resources.** Process control context for casting slip; supplier-specific procedures remain controlling.  
    https://digitalfire.com/glossary/specific+gravity

11. **USG — Pottery Plaster Submittal Sheet, IG1365.** Product-specific consistency, mixing/pouring guidance, absorbency, drying to constant weight, storage, and safe drying-temperature guidance. Use the sheet for the exact USG product in hand rather than transferring its numbers to another plaster.  
    https://assemblies-tools.usg.com/content/dam/USG_Marketing_Communications/united_states/product_promotional_materials/finished_assets/usg-pottery-plaster-submittal-en-IG1365.pdf

## Experimental porous printed molds

12. **Research on porous flexible SLS molds for ceramic slip casting (2025).** Demonstrates that direct printed porous tooling is a specialized research path, not equivalent to ordinary dense FDM/SLA. Verify the paper, material, and permeability method before replication.  
    Search record: https://scholar.google.com/scholar?q=2025+porous+flexible+SLS+TPU+molds+ceramic+slip+casting

13. **Patent literature on porous resin molds for slip casting.** Useful only as prior art/R&D context; a patent is not proof of workshop suitability.  
    https://patents.google.com/?q=porous+resin+mold+ceramic+slip+casting

## Food-contact ceramics — EU/Germany

14. **European Commission — Food-contact-material legislation.** Lists the EU ceramics-specific Directive 84/500/EEC under current food-contact legislation.  
    https://food.ec.europa.eu/food-safety/chemical-safety/food-contact-materials/legislation_en

15. **European Commission — Revision of EU food-contact-material rules.** Current work to revise ceramic/vitreous rules, lower lead/cadmium limits, and consider additional metals.  
    https://food.ec.europa.eu/food-safety/chemical-safety/food-contact-materials/revision-eu-rules_en

16. **EUR-Lex — Regulation (EC) No 1935/2004.** General EU framework for materials and articles intended to contact food.  
    https://eur-lex.europa.eu/eli/reg/2004/1935/oj

17. **EUR-Lex — Council Directive 84/500/EEC.** Ceramic articles intended to come into contact with foodstuffs.  
    https://eur-lex.europa.eu/eli/dir/1984/500/oj

18. **German Bedarfsgegenständeverordnung.** National consumer-goods requirements, including references relevant to ceramic migration testing. Always consult the current consolidated text.  
    https://www.gesetze-im-internet.de/bedggstv/

19. **BfR — Cadmium in food, Q&A, updated 2026-06-08.** Notes that glazes and decorations on ceramic ware can contain/release metals such as lead, cadmium, and cobalt.  
    https://www.bfr.bund.de/fragen-und-antworten/thema/cadmium-in-lebensmitteln-was-ist-ueber-die-aufnahme-und-gesundheitliche-risiken-bekannt/

20. **BfR — Heavy metals from ceramic glazes.** Explains that release depends on glaze quality/firing, food, temperature, and contact duration.  
    https://www.bfr.bund.de/presseinformation/schwermetalle-aus-keramikglasuren-koennen-die-gesundheit-gefaehrden/

21. **ISO 6486-1:2019.** Ceramic ware, glass-ceramic ware and glass dinnerware in contact with food — release of lead and cadmium — test method. Purchase/current-status verification via ISO.  
    https://www.iso.org/standard/70456.html

22. **ISO 6486-2.** Permissible limits; status/revision must be checked because the standards program can change.  
    https://www.iso.org/search.html?q=ISO%206486-2

## OpenSCAD

23. **OpenSCAD Cheat Sheet.** `import`, `surface`, `scale`, `offset`, `minkowski`, `difference`, and `intersection`.  
    https://openscad.org/cheatsheet/

24. **OpenSCAD User Manual.** Current syntax and command-line behavior.  
    https://en.wikibooks.org/wiki/OpenSCAD_User_Manual

## CadQuery

25. **CadQuery — Importing and Exporting Files.** Official list of import/export formats; STEP is supported for import and STL/STEP/3MF for export, while STL is not listed as a normal import format.  
    https://cadquery.readthedocs.io/en/latest/importexport.html

26. **CadQuery Class Reference.** Boolean, shell, transform, and solid-construction APIs.  
    https://cadquery.readthedocs.io/en/latest/classreference.html

27. **CadQuery introduction.** Python/OpenCascade parametric modeling overview.  
    https://cadquery.readthedocs.io/en/latest/intro.html

## FreeCAD

28. **FreeCAD Wiki — Part Cut.** CSG subtraction.  
    https://wiki.freecad.org/Part_Cut

29. **FreeCAD Wiki — Part ShapeFromMesh.** Mesh-to-shape conversion and its role in later Part operations.  
    https://wiki.freecad.org/Part_ShapeFromMesh

30. **FreeCAD Wiki — Part MakeSolid.** Creating solids from closed shape shells.  
    https://wiki.freecad.org/Part_MakeSolid

31. **FreeCAD Wiki — Part Thickness.** Constant-thickness/hollowing tool and limitations.  
    https://wiki.freecad.org/Part_Thickness

32. **FreeCAD Wiki — Part Boolean.** Fuse, Cut, Common, and Section operations.  
    https://wiki.freecad.org/Part_Boolean

## Blender

33. **Blender Manual — Remeshing.** Voxel remesher uses a virtual 3D grid and rebuilds topology.  
    https://docs.blender.org/manual/en/latest/modeling/meshes/retopology.html

34. **Blender Manual — Solidify Modifier.** Adds thickness to surfaces.  
    https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/solidify.html

35. **Blender Manual — Boolean Modifier.** Difference, union, and intersection operations.  
    https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/booleans.html

36. **Blender Manual — Mesh cleanup.** Cleanup operations for messy geometry.  
    https://docs.blender.org/manual/en/latest/modeling/meshes/editing/mesh/cleanup.html

## FDM resolution and printable detail

37. **Prusa Knowledge Base — Layers and perimeters.** Layer height controls Z resolution; XY detail depends on nozzle/line behavior; notes diminishing benefit below 0.10 mm with a typical 0.4 mm setup and maximum-layer-height relationship.  
    https://help.prusa3d.com/article/layers-and-perimeters_1748

38. **UltiMaker — Layer height guidance.** General nozzle/layer-height relationship.  
    https://support.ultimaker.com/s/article/1667337576725

39. **Prusa — Model design for 3D printing.** Nozzle size and modeling-detail context.  
    https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135

## Draft, vents, and material-saving mold design

40. **Formlabs — 3D printed molds.** Design-for-mold guidance on draft, vents, backing out molds, and minimum negative features. Its numerical recommendations are for its stated processes and are used in this skill only as analogous prototype heuristics, not ceramic-specific requirements.  
    https://formlabs.com/eu/blog/3d-printed-injection-molds-faq/

41. **Protolabs — Draft-angle guidance.** General rigid-mold heuristic and texture/depth relationship. Not a ceramic standard.  
    https://www.protolabs.com/resources/design-tips/improving-part-moldability-with-draft/

## Release and printed-tool finishing

42. **Smooth-On — Release-agent guide.** Interface-specific release selection for mold materials. Follow the exact product technical bulletin.  
    https://www.smooth-on.com/page/sealers-releases/

43. **Smooth-On — XTC-3D.** Example of a coating designed to fill/smooth 3D-print layer lines. It is referenced only as tooling finish, not as evidence of food-contact suitability.  
    https://www.smooth-on.com/product-line/xtc-3d/

## How the sources are used

- Numerical printer-detail values in the skill are deliberately labeled **starting points** and require coupons.
- Draft values are rigid-mold heuristics and must be increased or replaced by multipart/flexible tooling when the actual article locks.
- Plaster mix ratios and drying limits are always product-specific.
- Ceramic shrinkage is always body/process-specific and should be measured.
- Food-contact and dishwasher claims apply to the finished fired product and require current-market validation.
