# Parametric Labyrinth Gift Box

A two-piece cylindrical gift box generated with Python and CadQuery. One part carries a recessed cylindrical maze and the other carries a single follower. The maze is a perfect spanning tree, so there is exactly one route between the locked position and the opening.

The defaults target PLA, a 0.4 mm nozzle, and a 0.2 mm layer height.

## Generate The Parts

CadQuery 2.8 or newer is required.

```bash
python3 generate_labyrinth_box.py --output-dir exports/default
```

For mesh reports and local preview rendering, install the optional validation dependencies with `pip install '.[validation]'`.

The command creates:

- `inner.stl`: inner gift cup, already oriented base-down.
- `outer.stl`: outer sleeve, automatically oriented cap-down.
- `inner.step` and `outer.step`: editable print-oriented CAD files.
- `assembly.step`: separated parts in their common assembly coordinate system.
- `maze.json`: exact parameters, graph edges, unique solution, and difficulty metrics.

Example with a 55 mm usable cavity, 110 mm usable length, difficulty 8, and the maze recessed inside the outer sleeve:

```bash
python3 generate_labyrinth_box.py \
  --cavity-diameter 55 \
  --cavity-length 110 \
  --difficulty 8 \
  --maze-location outer \
  --seed 314159 \
  --output-dir exports/custom
```

## Main Parameters

| Parameter | Default | Meaning |
| --- | ---: | --- |
| `--cavity-diameter` | 40 mm | Usable internal diameter of the gift cup. |
| `--cavity-length` | 80 mm | Usable internal length above the cup bottom. |
| `--difficulty` | 5 | Difficulty from 1 to 10; increases grid density and candidate challenge score. |
| `--maze-location` | `inner` | `inner` cuts the maze outside the cup; `outer` cuts it inside the sleeve. |
| `--seed` | 20260805 | Reproduces the same candidate set and selected maze. |
| `--radial-clearance` | 0.35 mm | Radial running clearance between cup and sleeve. |
| `--channel-width` | 2.0 mm | Axial/tangential width of maze channels. |
| `--channel-depth` | 1.2 mm | Radial depth of maze channels. |
| `--follower-clearance` | 0.25 mm | Total width clearance between follower and channel. |
| `--minimum-wall` | 1.6 mm | Required residual wall after a maze cut. |
| `--minimum-web` | 1.2 mm | Required material between adjacent unconnected channels. |
| `--angular-facets` | 96 | Requested minimum channel-sector resolution; automatically raised for large radii. |

Run `python3 generate_labyrinth_box.py --help` for every fit and tessellation parameter.

## Safety Checks

The generator calculates the requested rows and columns from difficulty, then checks axial pitch and groove-floor chord spacing against `channel_width + minimum_web`. It emits a `PrintabilityWarning` and exits with status 2 if the requested difficulty, length, and diameter would force details below the declared print limits. It also blocks inadequate residual walls, undersized followers, invalid clearances, non-finite values, thin caps/bottoms, unsafe STL tolerances, and invalid difficulty or maze-location values.

PLA/0.4 mm safety floors cannot be lowered below 0.8 mm for walls/webs and 0.4 mm for individual features. Channel polygon resolution is automatically increased until chord sag is at most 0.02 mm and remains below the available follower/tessellation allowance.

The JSON manifest contains an independent path count. `unique_solution_count` must be `1`, and the edge count must equal `rows * columns - 1`.

## Printing

- Material: PLA.
- Nozzle: 0.4 mm.
- Layer height: 0.2 mm.
- Perimeters: at least 3.
- Top/bottom layers: at least 4.
- Inner STL: print as exported, base-down.
- Outer STL: print as exported, closed cap-down.
- Supports: start with supports disabled. The follower projection and groove roofs are approximately 1.2 to 1.4 mm; inspect the sliced layers and use local support only if your printer cannot bridge them cleanly.
- Elephant-foot compensation: recommended on both mating rims.

Do not scale the two STLs independently. Scaling changes fit clearance and follower engagement.

## Fit Calibration

The 0.35 mm radial default is a starting point, not a universal printer calibration. Print short low-difficulty parts first. If the fit binds, increase `--radial-clearance` in 0.05 mm steps or use slicer XY/hole compensation. If the follower binds in corners, increase `--follower-clearance` in 0.05 mm steps. Regenerate both pieces after changing model dimensions.

## Assembly And Use

1. Put the gift in the inner cup.
2. Start the outer sleeve over the cup.
3. Rotate gently while applying light axial pressure until the follower finds the open exit lead.
4. Follow the maze in reverse until the sleeve reaches the locked entry at the opposite axial end.
5. To open, explore branches from the locked entry until the unique solution reaches the exit lead.

Do not force the sleeve. Excess force can shear the round follower or wedge PLA layer ridges together.

## Maze Generator Research

The project does not depend on an external maze library. The strongest general Python option found was [`john-science/mazelib`](https://github.com/john-science/mazelib), but it models planar grids rather than cylindrical mechanical topology. Circular-specific projects such as [`Leoche/Svg-Circular-Maze-Generator`](https://github.com/Leoche/Svg-Circular-Maze-Generator) and [`MazeFX/MazeGenerator`](https://github.com/MazeFX/MazeGenerator) are small visualization tools. [`mutantbob/3d-printed-maze-generator`](https://github.com/mutantbob/3d-printed-maze-generator) is directly relevant but unmaintained and GPL-3.0.

This implementation keeps the short seeded depth-first spanning-tree algorithm local so cylindrical wraparound, unique solvability, and physical spacing checks are directly testable.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Automated geometry and mesh checks do not replace slicer inspection or a physical fit test.

The checked-in `exports/inner_maze/` and `exports/outer_maze/` directories contain default examples. `reports/` contains B-Rep, mesh-integrity, and FDM-risk results, while `previews/` contains multi-angle renders of the actual exported STLs.
