# P2 digital-candidate handoff

Use this reference whenever a product is assigned, audited for, or retained at
a lifecycle stage beginning with `P2`.

## Required product-local contract

Create `p2-stage/p2-manifest.json` and bind every artifact below to the same
SKU and named product revision with its exact SHA-256:

1. `product-description.en.md`: concise English product description covering
   intended function, included printed parts, and important draft limitations.
   It is not release copy and must not add untested claims.
2. A whole-product concept image: the approved Gate 0B asset when one exists.
   For a legacy product whose earlier process did not retain an image, a
   clearly labelled retrospective design-intent sheet may close only the P2
   inventory gap. Record its current model/reference basis; do not describe it
   as prior approval or use it to bypass Gate 0B.
3. A rendered image of the current model revision, separate from the concept
   image. Render the actual candidate geometry, not an AI approximation or a
   photograph. Label limitations when only a digital draft exists.
4. One 3MF print set containing every intended printed product part and the
   correct quantity. Do not substitute a coupon-only file, one member of a
   multipart product, an assembly/reference scene, or a family variant that is
   not the named candidate.

## Orientation and support inside the print set

Author each 3MF in the intended manufacturing orientation. Preserve that
choice in the 3MF build transforms or in the destination-slicer project data.
Record one support decision for the exact candidate:

- `disabled` only when the geometry and intended orientation are deliberately
  support-free;
- `enabled` with the intended support mode and removal-access rationale; or
- `mixed` when parts require different object-level settings.

Prefer a destination-slicer project 3MF with embedded machine, process,
filament, plate, orientation, and support settings. When a standard core 3MF is
the controlled artifact, link a complete exact profile set and a fresh target-
slicer report that used that 3MF without rearranging it. A prose instruction
without hash-bound profile/slicer evidence does not prove the manufacturing
decision.

For Anycubic work, use `slice-anycubic-next` with a new output directory. STL
or OBJ input requires the complete machine/process/filament profile set; an
authored 3MF may use its embedded profiles. Never upload or start a print from
this handoff.

## Validation and status boundary

Run:

```bash
python3 .agents/skills/validate-printable-3d-projects/scripts/fdm_ci.py \
  validate-p2-stage path/to/product/p2-stage/p2-manifest.json \
  --json-out path/to/product/p2-stage/p2-validation.json
```

P2 requires `PASS`. A missing, stale, mismatched, same-file concept/render,
incomplete print set, unrecorded orientation, or unrecorded support decision
fails the stage. P2 does not require a physical print, but it also does not
permit claims of physical fit, finish, strength, safety, rights clearance, or
commercial readiness.
