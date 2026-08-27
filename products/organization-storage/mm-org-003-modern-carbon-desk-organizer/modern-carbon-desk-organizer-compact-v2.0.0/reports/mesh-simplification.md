# Mesh simplification decision

Decision: **not beneficial**.

The master geometry is analytic CadQuery/OCCT B-Rep and is tessellated directly at 0.05 mm chordal and 0.15 rad angular tolerances. The selected production job totals 4,572 triangles, including the drawer twice. That is already about 99.85% below the 2,958,702-triangle manufacturing burden of the dense v1.1.2 job.

Global or local lossy decimation would risk drawer contact faces, thin divider junctions, stack pegs/sockets and shallow texture grooves without a meaningful storage or slicing benefit. Any future mesh change must be made by changing parametric geometry or export tolerance, then rerunning the mesh and interface contracts.
