# Edge cases and recovery strategies

## Source is open or only a decorative surface

Decide whether to close it, thicken it, or treat it as a skin around a new parametric core. Do not run volume Booleans until inside/outside is defined.

## Multiple internal shells

Separate components, classify each, and remove only proven debris. Eyes, teeth, ornaments, or textile layers may be intentional disconnected shells.

## Cutter intersects fine exterior detail

Reduce/reshape the cutter, change its axis, create a separate insert, or enlarge the object. Do not accept exterior damage just because the Boolean succeeds.

## Residual wall approaches zero

Use a conservative available-volume fit and wall map. A tiny triangulated sliver may slice unpredictably. Increase wall, reduce cavity, or move the operation.

## Coplanar interface

Create overlap or a stepped/tongue interface. Never depend on two zero-gap surfaces becoming one printable body.

## Highly symmetric alignment

Use asymmetric landmarks or keyed features. PCA/ICP may rotate to an equivalent but functionally wrong orientation.

## Voxel remesh erases engravings

Limit remesh to the transition patch, reduce voxel size only after memory estimation, or preserve the original exterior and rebuild the hidden side.

## Boolean creates many fragments

Inspect each fragment by volume, location, and relationship to ROI. Do not automatically keep only the largest body if a courtyard, horn, shoe rim, or door is intentionally separate.

## Shoe segmentation ambiguity

Ask for a cross-section, additional image, manually painted boundary, or measured sole interface. External appearance alone may not reveal where the sole ends or the upper begins.

## Thin toy limbs near a compartment

Choose another cavity orientation or smaller rounded cavity. Avoid relying on automatic thickness estimation around branches/limbs where ray methods can hit the wrong surface.

## Nonuniform scale

Nonuniform object scale distorts circles, wall offsets, and clearances. Apply or explicitly include it before fitting and generation.
