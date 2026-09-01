# Hybrid design recipes

Load only when deciding how much of a design Step1X should generate.

## 1. Whole appearance-led product

Use for a figurine, decorative desk object, low-risk toy shell or artistic planter whose visible form dominates and whose product requirements can be engineered afterward.

```text
approved requirements/concept
→ isolated whole-object plate with a deliberately simple base/back
→ several Step1X geometry candidates
→ select clay geometry, not texture
→ register to target height/envelope
→ repair/hollow/add base/drainage or other exact features
→ topology and thickness checks
→ slicer and physical prototype
```

Do not use the raw whole object when a hidden mechanism, seal, load-bearing mount, child-safety feature or tight interface controls the design. Split or rebuild those regions.

## 2. Step1X component inside a parametric product

Use for an organic grip, ornament, decorative cap, animal/leaf form, ergonomic skin or free-form handle region.

```text
CAD-owned master envelope and interface skeleton
→ component brief with target bounds/keep-outs/sacrificial root
→ imagegen component plate
→ Step1X raw geometry and textured appearance GLBs
→ landmark registration and seam check
→ trim root against CAD-owned seat/backer
→ separate keyed insert or validated mesh union
→ preservation, fit coupon and slicer checks
```

This is usually the best functional-design route because Step1X owns only appearance while CAD owns assembly and loads.

## 3. Sacrificial preform plus Boolean/CAD engineering

Use when the outer form is hard to model but the desired modification is exact: channels, holes, mounting eyes, ventilation, a compartment, a sole, a cable path, a threaded attachment or a flat/keyed base.

```text
prompt thick closed stock and protect the visible exterior
→ Step1X geometry master
→ explicit physical registration
→ proxy and protected/edit/transition regions
→ parametric cutters/inserts/backers/threads
→ mesh Boolean or local SDF fallback
→ compare exterior outside ROI
→ export final mesh plus exact STEP sources for functional bodies
```

Prefer a purchased insert, heat-set insert, captive nut or tap drill over a generated thread. Keep load transfer in a parametric core/backer rather than trusting decorative triangle geometry.

## 4. Textured GLB to multicolor print

```text
Step1X textured GLB as appearance evidence
→ normalize/bake albedo
→ measured filament palette quantization
→ remove sub-process color islands
→ explicit aligned color solids or tested slicer paint
→ portable 3MF plus destination project 3MF
→ layer-by-layer tool/color verification
```

Do not interpret image highlights, AO or painted shadows as additional materials or relief. Keep the raw textured GLB even if the final print uses one color.

## 5. When another route is better

| Design signal | Better route |
|---|---|
| prismatic/revolved/dimensioned body | direct CadQuery, FreeCAD or OpenSCAD |
| shallow motif on known substrate | height map/relief skill |
| real object with many calibrated photographs | photogrammetry then hybrid repair |
| simple exact handle or duct | parametric loft/sweep |
| safety-critical or tight mating component | measured CAD or purchased part |
| Step1X repeatedly fills a required opening | generate solid sacrificial stock and cut the opening parametrically, or abandon Step1X |

## Candidate experiment record

For each candidate, keep a one-line decision:

```text
run-001 REJECT — correct front silhouette, fused handle opening, insufficient seam stock
run-002 ACCEPT-AS-PREFORM — massing and protected exterior pass; back/holes explicitly replaced in CAD
run-003 REJECT — attractive texture, wrong handedness and excessive thin sheets
```

Rejected runs remain part of the authorship and engineering history; do not delete them from a commercial candidate's internal evidence set.
