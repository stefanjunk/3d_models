# Scope and routing

## Problem this specialist solves

Many dimension-driven models remain visually technical because their generators use only lines, extrusions, primitive Boolean operations, and constant-radius fillets. The model is parametric, but the **form language** is not. This skill adds a distinct aesthetic-geometry layer without weakening functional traceability.

## MECE ownership

| Question | Primary skill |
|---|---|
| What must the product do, carry, fit, survive, and print with? | `functional-3d-design` |
| How should a new visible envelope flow and remain editable across variants? | `parametric-freeform-surfacing` |
| How can an existing dense AI/scan mesh be cut or augmented without losing protected detail? | `organic-mesh-functionalization` |
| How does an image become printable relief? | `3d-print-heightmap-relief` |
| How is a negative mold or casting workflow designed? | casting/mold skill |

A project may load multiple skills, but each decision has one owner.

## Route here when

- a shoe, bowl, vehicle, enclosure, furniture part, lamp, or consumer product looks boxy;
- silhouette and highlight flow matter as much as nominal dimensions;
- size or style variants must share a stable design language;
- a sculpted or AI reference should become an editable parametric family;
- functional hardpoints must stay fixed while the shell changes;
- a local junction needs a smooth implicit blend, but the whole model must not be remeshed.

## Do not route here when

- ordinary fillets, chamfers, or one simple loft are sufficient;
- the task is only material selection, fit clearance, gears, fasteners, or slicer configuration;
- the main requirement is preserving an existing dense source mesh during a local edit;
- the request is only an embossed image or texture;
- the object is a mold and demolding architecture is the main problem.

## Composite sequences

### New premium product

```text
requirements and hardpoints
→ semantic parameters
→ fair curves and sections
→ envelope construction
→ local blend/deformation if required
→ regenerate exact features
→ wall/print split
→ tessellation and slicer validation
```

### AI/scan reference as target, not protected source

```text
archive reference and provenance
→ orient and mark semantic landmarks
→ build low-dimensional curve/section model
→ fit with regularization
→ validate residual error and fairness
→ add exact core/features
```

### Existing mesh must remain visually authoritative

Start with `organic-mesh-functionalization`. This skill contributes only the fitted replacement envelope, cage, or morph system within the permitted regions.

## Deliverable boundary

The aesthetic envelope should expose:

- named user parameters;
- named hardpoint constraints;
- guide curves and section definitions;
- continuity intent;
- backend source or a deterministic generator;
- neutral CAD/mesh handoff where available;
- fairness, fitting, drift, topology, and tessellation reports.
