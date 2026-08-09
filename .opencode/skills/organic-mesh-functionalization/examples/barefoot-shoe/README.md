# Replace an AI-generated shoe interior and upper

The external AI mesh is used only as a decorative/source envelope. The script creates a parameterized zero-drop sole and broad cutters for removing material above the sole interface. It does not infer a safe or comfortable internal last from the outside shell.

Recommended sequence:

1. Establish ground plane, heel-to-toe axis, handedness, and a reviewed sole/upper boundary.
2. Segment/remove the textile-looking upper with Blender vertex groups or a fitted interface surface; do not rely on a horizontal plane if the rim curves.
3. Decide whether the original outsole skin/rim is retained.
4. Fit the generated sole to foot/last data and transform it into the shell.
5. Add a conformal bonding flange or keep the sole separate.
6. Validate protected outsole texture, zero drop, internal foot volume, flex, attachment, and full print orientation.
