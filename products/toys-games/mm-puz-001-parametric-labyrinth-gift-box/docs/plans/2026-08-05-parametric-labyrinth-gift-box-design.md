# Parametric Labyrinth Gift Box Design

## Goal

Create a two-piece cylindrical gift box for PLA printing with a 0.4 mm nozzle. A single follower on one part moves through a recessed cylindrical maze on the mating part. The usable cavity diameter and length, puzzle difficulty, seed, and maze location are parameterized.

## Mechanical Design

The inner piece is a closed-bottom cup. `cavity_diameter` and `cavity_length` describe its usable internal space. The outer piece is a closed-top sleeve that covers the cup opening. Both parts print separately.

`maze_location` has two modes:

- `inner`: channels are recessed into the outside of the inner cup; the sleeve carries one inward follower.
- `outer`: channels are recessed into the inside of the sleeve; the cup carries one outward follower.

The follower enters or leaves through a lead-in at the open end. Radial clearance, channel clearance, wall thicknesses, channel depth, and base/cap thickness are explicit parameters with PLA-oriented defaults.

## Maze Design

The maze is a rectangular cell grid wrapped around a cylinder. Circumferential neighbors wrap across the seam. A seeded randomized depth-first search produces a spanning tree, so every cell is connected and every pair of cells has exactly one graph path. Entry and exit are on opposite axial boundaries.

Difficulty from 1 through 10 controls row and column targets. Multiple deterministic candidate trees are scored by solution length, turn count, and dead ends; the candidate closest to the requested difficulty profile is selected. The generator verifies that the graph is a tree and independently counts entry-to-exit paths before geometry is created.

## Printability Contract

Defaults target PLA, a 0.4 mm nozzle, and 0.2 mm layers:

- Structural walls: at least 1.6 mm after maze cuts.
- Channels: at least 1.8 mm wide.
- Webs between unconnected channels: at least 1.2 mm.
- Radial running clearance: 0.35 mm.
- Follower clearance inside channels: 0.25 mm total.

Preflight derives the largest printable grid from diameter, length, channel width, and minimum web. If the requested difficulty cannot fit without violating these limits, the script emits a warning and exits before export. It also rejects insufficient residual walls, invalid fits, and follower dimensions below declared printable features.

## Deliverables And Validation

The command-line script exports inner and outer STL files, editable STEP files, a separated assembly STEP, and a JSON manifest containing parameters, maze edges, solution, score, and checks. Unit tests cover deterministic generation, cylindrical wraparound, tree invariants, unique solvability, difficulty sizing, and unsafe parameter warnings.

Generated B-Reps must be valid single solids. Reloaded STL files must be watertight, consistently wound, positive-volume, single-body meshes with expected dimensions. Multi-angle preview images and normal-based FDM reports complete the automated gate. A slicer preview and physical fit coupon remain required before relying on a final print.

## Library Research

- `john-science/mazelib`: mature general Python maze library, MIT licensed, but uses planar grids rather than cylindrical mechanical topology.
- `Leoche/Svg-Circular-Maze-Generator`: small JavaScript circular SVG generator, not intended for cylindrical movement or printable fits.
- `MazeFX/MazeGenerator`: small Python/Kivy circular maze generator, no maintained packaging or mechanical geometry layer.
- `mutantbob/3d-printed-maze-generator`: directly relevant cylindrical Rust generator, but unmaintained, GPL-3.0, and not suitable as a dependency for this self-contained CadQuery tool.

The project therefore implements the small spanning-tree algorithm locally and uses no maze-generation dependency.
