# Berlin site-marker build iterations — revision 0.5.0

`digital-candidate-r7` is the selected DRAFT result. It applies the 0.5 mm marker reveal to the shared 0.25 mm manufacturing raster before contour generation. That removes the point-contact failures seen in the earlier iterations without changing the approved map, split, mounting or lighting architecture.

| Iteration | Result | Reason |
|---|---|---|
| r1 | Rejected | Microscopic Boolean slivers produced a second qualified composite component. |
| r2 | Aborted | Deterministic component-sorting `NameError`. |
| r3 | Rejected | Unintended secondary composite component remained. |
| r4 | Rejected | Shared raster improved the result, but a microscopic residual remained. |
| r5 | Rejected | Marker reveal worked; context-left tool 2 retained one point-touch non-manifold edge. |
| r6 | Rejected | Lower simplification tolerance did not remove the point contact. |
| r7 | Pass | Sixteen watertight color bodies and four connected watertight composites. |

The failed iterations are evidence, not alternatives for slicing or printing.
