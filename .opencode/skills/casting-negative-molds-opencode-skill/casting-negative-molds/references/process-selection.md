# Process selection

The geometry of a mold is inseparable from the way the casting material sets. Select the process before selecting the CAD operation.

## Decision table

| Desired cast | Normal tool chain | Why | Typical fill mode |
|---|---|---|---|
| Gypsum/plaster final object | Sealed printed negative, silicone mold, or conventional mold | Gypsum sets by hydration; the working cavity does not need to absorb water | Open pour or closed pour with vents |
| Hollow porcelain/stoneware slip cast | Printed positive master or printed case → absorbent pottery-plaster working mold → ceramic cast | Porous plaster removes water from deflocculated slip and builds a wall | Fill, dwell, drain, dry, demold |
| Solid ceramic cast | Absorbent plaster mold or process-specific porous tool | Water extraction and drying still control release and defects | Fill and hold; sometimes feed reservoir |
| Ceramic press/slump mold | Printed master/case → plaster mold, or qualified refractory/porous tool | Geometry and moisture transfer differ from drain casting | Press slab/body or slump sheet |
| Flexible undercut object in plaster | Silicone skin + rigid mother mold | Flexible skin releases undercuts; shell controls shape | Open/closed pour |
| One-off sacrificial cast | Thin breakaway printed mold or soluble core when compatible | Eliminates complex segmentation | Fill, cure/set, destroy tool |
| Experimental direct ceramic casting into printed porous tool | Special porous print process only | Requires controlled permeability and release, unlike ordinary dense FDM/SLA | R&D-specific |

## Route A — Direct printed negative for a gypsum/plaster final cast

Use when the final object is gypsum-based and the print material, coating, and release system are compatible with the selected plaster.

1. Create a rigid mold with adequate draft or multiple separable parts.
2. Seal layer lines and pinholes if the mold must not absorb water.
3. Apply a product-specific release system. Test that it does not stain, inhibit setting, or soften the print.
4. Clamp and leak-test the assembled mold with water before mixing plaster.
5. Mix by the plaster manufacturer's stated water-to-powder procedure; minimize entrained air.
6. Pour at the lowest practical turbulence, tap/vibrate carefully, and top up a reservoir as needed.
7. Demold after adequate set and strength; avoid levering against delicate relief.
8. Clean and dry the tool without exceeding the print material's temperature limits.

A full solid printed block is rarely necessary. A ribbed shell or insert in a reusable frame usually reduces print time and warping.

## Route B — Conventional hollow ceramic slip casting

The working mold must normally be absorbent. Dense plastic does not pull water from slip, so a direct dense printed negative will not build the usual cast wall.

Recommended chain:

```text
finished-object geometry
        ↓ compensate body shrinkage
positive master or reusable negative case
        ↓ seal/release only at the master/case interface
pottery plaster working-mold sections
        ↓ dry to stable working condition
fill with conditioned slip
        ↓ dwell to build wall
pour out excess slip
        ↓ drain and stiffen
open plaster mold and remove greenware
        ↓ dry, finish seams, bisque, glaze, fire
```

Two common printed-tool strategies:

### Printed positive master

Print the positive article shape at compensated size. Finish its surface. Build cottles and parting dams around it, then cast plaster mold sections around it. This is intuitive for one-off or low-volume mold making.

### Printed negative case

Print a reusable case that represents the exterior of one plaster mold section. Fill it with pottery plaster to reproduce identical working-mold sections. This is more efficient when making several plaster molds or replacing worn sections.

Do not coat the ceramic slip-contact face of the plaster working mold. Sealers and release films reduce the absorption needed for casting.

## Route C — Press, slump, and open-face ceramic molds

For tiles, trays, slabs, and shallow reliefs, a one-sided open plaster mold is often simpler than a closed casting mold.

- A **negative relief mold** receives a clay slab or liquid body and creates raised detail.
- A **positive hump mold** supports a slab and creates a concave article.
- A **negative slump mold** receives the slab and forms a convex outside.

Design broad draft around the perimeter, radiused transitions, drainage/air escape under slabs, and handling space. Test warpage because clay thickness, directional shrinkage, and firing support often dominate dimensional error.

## Route D — Silicone skin and mother mold

Use a flexible skin for deep texture, re-entrant detail, handles, figurative ornament, and other undercuts. Back the thin silicone with a segmented rigid mother mold.

Advantages:

- fewer rigid mold sections;
- high surface reproduction;
- easier demolding of undercuts;
- replaceable flexible skin.

Tradeoffs:

- silicone cost and mixing accuracy;
- possible inhibition or compatibility issues;
- dimensional compliance under hydrostatic pressure;
- not an absorbent slip-casting surface unless the silicone is only an intermediate tooling step.

## Route E — Sacrificial or soluble tooling

A sacrificial mold can be efficient for one-off parts that cannot be segmented. The cast must tolerate mold-removal chemistry and mechanical destruction.

Examples include:

- thin breakaway PLA/PETG shell for a plaster final cast;
- water-soluble cores only where water exposure will not damage the cast;
- low-melting or dissolvable cores qualified against the casting material;
- sand or granular cores retained by a printed skin.

Never assume a soluble support is safe for a ceramic body, glaze, wastewater stream, or food-contact product. Test contamination and disposal requirements.

## Process questions the skill must answer

Before generating geometry, state:

1. What physically causes the cast to solidify or build a wall?
2. Must the working mold absorb water, conduct heat, flex, or remain chemically inert?
3. Is the printed piece the working mold, a master, a case, a core, an insert, or a mother mold?
4. Where does air leave and excess material drain?
5. What changes dimension: tool finishing, plaster expansion, green shrinkage, drying shrinkage, firing shrinkage, glaze, or coating?
6. How many cycles must the tooling survive?
7. Which surfaces may show seams, witness marks, or post-processing?

## Default recommendation hierarchy

For ordinary workshop equipment:

- **Plaster final cast:** ribbed printed negative or silicone skin/mother mold.
- **Porcelain/stoneware hollow ware:** finished printed master or case, then pottery-plaster working mold.
- **Shallow ceramic relief/tile:** one-sided plaster mold generated from a printed master.
- **Severe undercuts:** silicone intermediate or sacrificial core, not an excessively fragmented rigid mold.
- **Production repeats:** reusable printed cases and replaceable plaster working-mold sections.
