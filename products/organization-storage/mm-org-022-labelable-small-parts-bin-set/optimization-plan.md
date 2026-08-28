# Optimization plan

Baseline: solid envelope blocks for all five unique parts.

Candidate: thin rounded shells, a local pickup ramp, compact label rails and an open registration frame. Preserve the containment walls, floor, label slot and packing datums. Select the candidate only if unique-part CAD volume is at least 65% below the solid-envelope baseline and exact-profile slicing remains warning-free.

Direct CadQuery tessellation is retained while every STL stays below 60,000 triangles and 8 MiB. Decimation is not allowed to flatten the front grip, interior ramp, rounded corners or label rails.
