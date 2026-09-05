# FLUENT R2 — actual 3D comparison and decision

Selected development recommendation: parametric Run 003, bundled-petal crown.
This is an agent design recommendation, not human appearance approval.

| Candidate | Visual finding | Disposition |
|---|---|---|
| Parametric 001 | Too soft; nearly closed crown | Superseded diagnostic |
| Parametric 002 | Clearer ribs, but crown reads as a cut, wavy vessel | Editable comparison |
| Step1X run-001 | Better S silhouette and rounded tips; ragged/merged ribs, especially on the back | Keep immutable as form reference, reject as production surface |
| Parametric 003 | Ribs converge into two soft tongues; coherent, calm front/back/side | Recommended development basis |

Independent read-only reviewer /root/concept_visual_review agrees Run 003 is
the strongest current development basis. The cut edges of Run 002 are gone;
the surfaces are much calmer than Step1X. Reviewer modified no files.

Remaining visible differences from the R1 image:

- Crown reads as two upright leaves; the tips overlap substantially from the side.
- Ribs remain broader/softer than R1's more separated highlight lines.
- Lower body tapers earlier and appears slimmer than the source.

The next aesthetic refinement may carry the belly higher, incline the tips
more deliberately, and narrow rib crests. Do not infer that these changes are
already implemented or approved.

All comparison images are genuine Blender renders of their named meshes.
They share the Run 002 physical studio/material and canonical cameras.
Step1X uses 24 samples versus Run 002's 32; Run 003 also uses 24. There is no
AI overpaint, texture displacement or geometry-smoothing modifier on Step1X.
The source AI camera is not calibrated: this is qualitative style comparison,
not a numerical replica-fidelity claim. Hidden Step1X geometry is synthesized.

Topology, wall thickness, fit, ventilation, slicer behavior and physical
appearance are separate gates. Four Step1X components were confirmed by the
shared mesh auditor; none were silently removed.
