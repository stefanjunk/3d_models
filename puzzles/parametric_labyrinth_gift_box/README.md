# Parametric Labyrinth Gift Box

A two-piece cylindrical gift box generated with Python and CadQuery. The inner cup has an optional full-diameter grip collar, one part carries a recessed cylindrical maze, and the other carries a single follower. The maze graph is a perfect spanning tree, so it has exactly one validated graph route between the locked position and the opening.

The defaults target PLA, a 0.4 mm nozzle, and a 0.2 mm layer height.

## Generate The Parts

Python 3.11 or newer and CadQuery `>=2.8,<3` are required. From this directory:

```bash
python3 -m pip install .
```

Install the validation extra when running the tests, mesh checks, or preview renderer:

```bash
python3 -m pip install '.[validation]'
```

Detailed grayscale image relief is optional and STL-only. Install its dependencies in a project-local environment only when needed:

```bash
python3 -m pip install '.[image-relief]'
```

```bash
python3 generate_labyrinth_box.py --output-dir exports/default
```

The command creates:

- `inner.stl`: inner gift cup, translated to `zmin=0` and oriented grip-down when the grip is enabled.
- `outer.stl`: outer sleeve, automatically oriented cap-down.
- `inner.step` and `outer.step`: print-oriented exact B-Rep solids containing the grip and built-in ornaments, but intentionally omitting raster image relief.
- `assembly.step`: a side-by-side presentation assembly, not a mated assembly.
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

Built-in flutes are exact in STEP and STL:

```bash
python3 generate_labyrinth_box.py \
  --ornament-type flutes \
  --decoration-mode emboss \
  --decoration-depth 0.6 \
  --output-dir exports/fluted
```

A grayscale image can wrap once around the grip and sleeve. This postprocesses only the two STL files:

```bash
python3 generate_labyrinth_box.py \
  --image-relief artwork.png \
  --image-relief-resolution 256 \
  --decoration-mode engrave \
  --decoration-depth 0.6 \
  --output-dir exports/image-relief
```

## Main Parameters

| Parameter | Default | Meaning |
| --- | ---: | --- |
| `--cavity-diameter` | 40 mm | Usable internal diameter of the gift cup. |
| `--cavity-length` | 80 mm | Usable internal length above the cup bottom. |
| `--difficulty` | 5 | Difficulty from 1 to 10; increases grid density and selects a higher challenge-score quantile. |
| `--maze-location` | `inner` | `inner` cuts the maze outside the cup; `outer` cuts it inside the sleeve. |
| `--seed` | 20260805 | Reproduces the same candidate set and selected maze. |
| `--radial-clearance` | 0.35 mm | Radial running clearance between cup and sleeve. |
| `--grip-length` | 15 mm | Solid collar below the cup; `0` disables it. Its base radius equals the sleeve radius. |
| `--channel-width` | 2.0 mm | Axial/tangential width of maze channels. |
| `--channel-depth` | 1.2 mm | Radial depth of maze channels. |
| `--follower-clearance` | 0.25 mm | Total width clearance between follower and channel. |
| `--minimum-wall` | 1.6 mm | Required residual wall after a maze cut. |
| `--minimum-web` | 1.2 mm | Required material between adjacent unconnected channels. |
| `--ornament-type` | `none` | Exact B-Rep `none`, `flutes`, `diamonds`, or `rings`. |
| `--decoration-mode` | `engrave` | Shared `engrave` or `emboss` mode for ornaments and image relief. |
| `--decoration-depth` | 0.6 mm | Shared relief depth, bounded to 0.2–2.0 mm. |
| `--decoration-count` | 16 | Repeat count for exact ornaments, bounded to 3–128. |
| `--decoration-margin` | 3 mm | Blank bands at grip bottom, seam sides, and sleeve top. |
| `--image-relief` | none | Optional grayscale source for detailed STL-only relief. |
| `--image-relief-resolution` | 256 | Circumferential samples, bounded to 32–1024. |
| `--image-relief-invert` | off | Makes light rather than dark pixels produce stronger relief. |
| `--angular-facets` | 96 | Requested minimum channel-sector resolution; automatically raised for large radii. |

Run `python3 generate_labyrinth_box.py --help` for every fit and tessellation parameter.

## Safety Checks

The generator emits a `PrintabilityWarning` and exits with status 2 when preflight detects unsafe spacing, walls, end margins, decoration bands, clearances, follower dimensions, caps/bottoms, STL tolerances, image inputs, or non-finite/out-of-range values. For engraved outer mazes, residual wall checks subtract both the internal channel depth and external decoration depth. Ring ornaments additionally require a ring pitch of at least the declared minimum feature on both bands. Combining `--ornament-type` with `--image-relief` is rejected because mesh booleans over already-ornamented STLs are unreliable; choose one decoration source per generation. The implementation rationale and physical thresholds are documented under [Printability Method](#printability-method).

The JSON manifest contains an independent path count. `unique_solution_count` must be `1`, and the edge count must equal `rows * columns - 1`.

## Printing

- Material: PLA.
- Nozzle: 0.4 mm.
- Layer height: 0.2 mm.
- Perimeters: at least 3.
- Top/bottom layers: at least 4.
- Inner STL: print as exported, grip-down (`zmin=0`); with `--grip-length 0`, the original cup base is down.
- Outer STL: print as exported, closed cap-down.
- Supports: start with supports disabled. The follower projection and groove roofs are approximately 1.2 to 1.4 mm; inspect the sliced layers and use local support only if your printer cannot bridge them cleanly.
- Elephant-foot compensation: recommended on both mating rims.

Do not scale the two STLs independently. Scaling changes fit clearance and follower engagement.

### Image Preparation

Use a grayscale PNG or JPEG. The image width maps to one full circumference; make the left and right edges tile cleanly if a hidden vertical seam matters. Image height is stretched across the usable grip and sleeve bands together, then split in proportion to their visible heights. Both halves share the same assembly-angle origin, while blank margins remain at the grip bottom, both sides of the grip/sleeve seam, and sleeve top. Dark pixels are stronger by default; pass `--image-relief-invert` for the reverse. Start at resolution 64–128 for proofing before a denser final export.

Raster relief requires a robust mesh boolean backend. The optional group installs Manifold; Blender is also accepted when available. STEP never contains this image relief, even when the STL does. Image relief cannot be combined with `--ornament-type` ornaments; run one decoration style per generation. If relief processing fails, the output directory is left untouched rather than partially decorated.

## Fit Calibration

The 0.35 mm radial default is a starting point, not a universal printer calibration. Print short low-difficulty parts first. If the fit binds, increase `--radial-clearance` in 0.05 mm steps or use slicer XY/hole compensation. If the follower binds in corners, increase `--follower-clearance` in 0.05 mm steps. Regenerate both pieces after changing model dimensions.

## Assembly And Use

1. Put the gift in the inner cup.
2. Start the outer sleeve over the cup.
3. Rotate gently while applying light axial pressure until the follower finds the open exit lead.
4. Follow the maze in reverse until the sleeve reaches the locked entry at the opposite axial end.
5. To open, explore branches from the locked entry until the unique solution reaches the exit lead.

Do not force the sleeve. Excess force can shear the round follower or wedge PLA layer ridges together.

## How This Was Created

### Method Decision

This extension uses a deliberate hybrid. CadQuery remains the exact B-Rep master for the cup, grip, sleeve, maze, follower, and optional built-in ornaments, so those features are present in STEP and STL. Optional image relief is a periodic cylindrical mesh solid booleaned against the print-oriented STL exports. It is not a STEP-equivalent representation, and the manifest records that limitation.

### Design Contract

The model started with these non-negotiable requirements:

- Exactly two separately printable round parts: a gift cup and a closed sleeve.
- Usable cavity diameter and length must be direct parameters, not side effects of outside dimensions.
- Difficulty must affect more than the random seed.
- The maze must have exactly one solution route.
- The maze must work either outside the inner cup or inside the outer sleeve.
- Unsafe combinations of size, difficulty, and feature dimensions must stop before export.
- Default geometry must suit PLA, a 0.4 mm nozzle, and 0.2 mm layers.
- The grip must preserve the closed outer silhouette and export grip-down.
- Exact ornaments belong in both STEP and STL; detailed image relief is intentionally STL-only.

The resulting architecture separates configuration and preflight in `config.py` and `preflight.py`, graph generation in `maze.py`, exact B-Rep construction in `geometry.py`, optional lazy-loaded raster mesh work in `image_relief.py`, and file/manifest export in `generate_labyrinth_box.py`. This separation allows solvability and print constraints to be tested without invoking the CAD kernel.

### Maze Research

The project does not depend on an external maze library. The strongest general Python option found was [`john-science/mazelib`](https://github.com/john-science/mazelib), but it models planar grids rather than cylindrical mechanical topology. Circular-specific projects such as [`Leoche/Svg-Circular-Maze-Generator`](https://github.com/Leoche/Svg-Circular-Maze-Generator) and [`MazeFX/MazeGenerator`](https://github.com/MazeFX/MazeGenerator) are small visualization tools. [`mutantbob/3d-printed-maze-generator`](https://github.com/mutantbob/3d-printed-maze-generator) is directly relevant but unmaintained and GPL-3.0.

A local generator was smaller and easier to audit than adapting those projects. It also made cylindrical seam behavior, deterministic seeds, unique-path verification, and physical spacing part of this project's own test contract.

### Maze Generation Method

The cylindrical surface is represented as a rectangular cell grid whose first and last columns are neighbors. A seeded randomized depth-first search creates a spanning tree. A tree with `N` cells has `N - 1` edges, is fully connected, and contains one graph path between any two cells.

The entry is fixed on the first axial row. The exit is the most distant cell on the final row. The implementation then reconstructs the solution and separately counts simple entry-to-exit paths with an early limit of two. Geometry is generated only when that independent count equals one.

Difficulty from 1 to 10 affects both scale and topology:

- Requested rows are `4 + difficulty`.
- Requested columns are `8 + 2 * difficulty`.
- Twenty-four deterministic candidate trees are generated from the requested seed.
- Candidates are ranked by a normalized challenge score: 65% solution-path ratio, 25% turn ratio, and 10% dead-end ratio.
- Difficulty selects a quantile from that ranking on the requested grid. This makes selection monotonic within one candidate set; scores are not guaranteed to rise across different grid sizes.

### From Graph To CAD

Each cell maps to an angle and an axial height. Axial graph edges become radial rectangular cutters; circumferential edges become annular-sector cutters. Overlapping cutters create connected channel intersections. A final axial cutter extends the chosen exit to the open edge.

For an inner maze, the channels are cut inward from the cup's outside surface and the follower projects inward from the sleeve. For an outer maze, channels are cut outward from the sleeve bore and the follower projects from the cup. The outer-maze axial mapping is reversed because opening the sleeve moves its local maze coordinates in the opposite direction around the stationary cup follower.

The follower is a round radial pin rather than a square key. The round section is less likely to catch when motion changes between axial and rotational directions at a maze node. Its diameter is the channel width minus the configured follower clearance; radial projection includes sleeve clearance and channel engagement while retaining tip clearance at the groove floor.

### Main Engineering Decisions

| Decision | Reason |
| --- | --- |
| Python and CadQuery | Precise parametric solids, reliable booleans, and direct STEP/STL export. |
| Local perfect-maze generator | Small auditable algorithm with cylindrical wraparound and no unsuitable dependency. |
| Recessed channels | Keeps both parts as robust tube-like solids and supports either maze location. |
| Round follower pin | Reduces corner snagging and supports an analytic width-clearance contract. |
| Fail instead of silently reducing difficulty | The requested puzzle remains honest; unsafe dimensions are not disguised as a lower difficulty. |
| Usable cavity dimensions as inputs | Gift size stays predictable when wall or maze parameters change. |
| Print-oriented STL and STEP parts | The inner part exports grip-down at `zmin=0` and the sleeve cap-down, avoiding a large cap bridge. |
| Hybrid exact/mesh decoration | STEP preserves the grip and exact ornaments; only STL receives detailed raster image relief. |
| Lazy optional image stack | No image path means Pillow, Trimesh, and boolean backends are not loaded by generation. |
| JSON manifest per export | Preserves the exact graph, solution, selected seed, dimensions, orientation, and representation fidelity. |

### Printability Method

Preflight checks use the physical location where spacing is smallest, not only the visible outside surface. For an inner maze, circumferential spacing is measured as a chord at the groove floor. For an outer maze it is measured at the bore. The cell pitch must preserve `channel_width + minimum_web`.

The end margin must leave a full web beyond half the channel width; otherwise unrelated final-row channels could break through the rim and create unintended exits. Maze cuts must leave the configured residual wall. External engraving is included in that same sleeve budget, including simultaneous outer-maze channel and decoration cuts. Bottom and cap thickness must also meet the wall value. Decoration margins must leave usable sleeve and enabled-grip bands. Fixed PLA/0.4 mm floors prevent users from making walls or webs thinner than 0.8 mm or individual features thinner than 0.4 mm through parameter overrides.

Annular channels are polygonal B-Rep sectors. Their effective facet count scales with radius so chord sag stays at or below 0.02 mm and below the follower/tessellation allowance. This matters on large boxes: a fixed low facet count can move the channel boundary far enough inward to collide with the pin even when a small model works.

### Tools And Methods

| Tool or method | Use |
| --- | --- |
| Python 3 standard library | Configuration, deterministic random generation, graph traversal, CLI, and JSON manifests. |
| CadQuery 2.8 / OpenCascade | Cup, sleeve, channel cutters, follower, booleans, assemblies, STEP, and STL. |
| Pillow | Optional grayscale loading, EXIF orientation, and relief sampling. |
| Trimesh 4+ plus Manifold or Blender | Periodic image height fields, STL booleans, and reloaded-mesh integrity checks. |
| Matplotlib | Multi-angle previews of the actual exported STL files. |
| `unittest` | Test-first graph, preflight, geometry, kinematic, and CLI coverage without another test dependency. |
| GitHub repository metadata | Comparison of existing general, circular, and cylindrical maze generators. |
| Independent code-review passes | Discovery of parameter and large-radius edge cases beyond the default model. |

The implementation followed a red-green workflow: define a failing behavior test, confirm the failure, add the smallest implementation, and rerun focused plus full tests. Exported files were reloaded from disk rather than trusting only in-memory CadQuery objects.

### Challenges And Resolutions

| Challenge | Resolution |
| --- | --- |
| General maze libraries did not model a mechanical cylinder | Implemented a compact depth-first spanning tree with wrapped columns. |
| The two maze locations have opposite relative axial motion | Reversed row-to-height mapping for the outer-sleeve maze. |
| Cutting with one compound of overlapping tools returned fragmented cutter-like results | Passed all cutters directly to one OpenCascade cut operation. |
| A square follower had unnecessary corner-snag risk | Replaced it with a round radial pin and sampled no-interference along the solution. |
| A graph can be unique while wide channels accidentally touch | Enforced axial pitch, groove-floor chord spacing, residual webs, and end margins. |
| Small end margins opened extra physical exits | Required a closed band of at least half a channel plus one minimum web. |
| Non-positive clearances could create intersecting parts | Added finite, positive, and printer-oriented parameter validation. |
| Fixed channel facets failed on large diameters | Derived additional facets from radius and maximum chord sag. |
| A cap-up sleeve would require bridging the full bore | Rotated exported sleeve files to cap-down and tested bottom-versus-top solid area. |
| The assembly grip lives below `z=0`, but slicers require nonnegative Z | Translated only the print-oriented inner STL/STEP by `grip_length`; maze and follower assembly coordinates remain unchanged. |
| Blender exact booleans emitted isolated zero-volume triangle pairs | Retained the sole positive watertight body, rejected every nontrivial extra body, and recorded discarded zero-volume fragment counts in the manifest. |
| Internal-maze previews were difficult to inspect | Added an exact half-space triangle clipper for a dependency-light cutaway render. |

### Validation Performed

The final suite contains 53 tests. It covers deterministic cylindrical neighbors, tree invariants, independent path counting, candidate difficulty ranking, unsafe parameter warnings, grip dimensions and zero-grip behavior, every exact ornament and mode, ring pitch limits, the ornament/image-relief combination rejection, image mapping, invert handling, zero-grip relief, dependency errors, atomic output on relief failure, STEP invariance under relief, watertight emboss/engrave image outputs, both maze modes, measured cavity behavior, print export orientation, STL reloads, and zero ideal-CAD overlap between the round follower and maze-bearing solid at every solution node and edge midpoint.

A 200 mm cavity regression starts with only 48 requested facets, automatically raises the effective resolution, and verifies both maze locations without sampled follower collision. The checked-in default artifacts add four STEP reload checks, four STL mesh checks, and four FDM risk reports. Every sample is a valid single solid/body; each STL is watertight, consistently wound, positive-volume, and free of broken or degenerate faces.

The validation boundary is deliberate. Raster STL booleans do not update STEP, and grayscale sampling cannot preserve detail below its circumferential/axial mesh spacing. Node and midpoint sampling is not a continuous swept-volume proof. It does not prove corner transitions, all dead-end branches, the complete entry/exit lead, assembled removal, or the absence of every possible physical shortcut. It also does not model extrusion variation, seam blobs, elephant foot, bridge sag, shrinkage, or wear. The normal-based reports therefore remain marked for slicer review, and a short physical calibration pair is required before trusting a final locked gift.

Detailed machine-readable results are in `reports/`, exact maze data is in each `maze.json`, and the reviewed STL renders are in `previews/`.

## Reproduce Validation

```bash
python3 generate_labyrinth_box.py \
  --maze-location inner --output-dir exports/inner_maze
python3 generate_labyrinth_box.py \
  --maze-location outer --output-dir exports/outer_maze
python3 -m unittest discover -s tests -v
python3 validation/render_previews.py
```

The checked-in reports were generated with local shared utilities under `/workspace/skills`. They are not installed by `.[validation]` or versioned by this project, so the commands below reproduce those reports only in a workspace containing the same utilities. The unit tests and preview renderer above are the self-contained validation path. Example report commands for one part are:

```bash
SKILLS=/workspace/skills

python3 "$SKILLS/cadquery-functional-geometry/scripts/inspect_cadquery.py" \
  validation/cadquery_exports.py \
  --variable inner_maze_inner \
  --report reports/inner_maze_inner.cadquery.json

python3 "$SKILLS/mesh-validation/scripts/validate_mesh.py" \
  exports/inner_maze/inner.stl \
  --units mm --max-bodies 1 \
  --report reports/inner_maze_inner.mesh.json

python3 "$SKILLS/fdm-printability/scripts/inspect_printability.py" \
  exports/inner_maze/inner.stl \
  --units mm --bed 220,220,250 --nozzle 0.4 --layer-height 0.2 \
  --declared-min-wall 1.6 --declared-min-feature 0.8 --material PLA \
  --report reports/inner_maze_inner.fdm.json
```

Repeat those commands for the inner/outer part in each maze mode. Report JSON records the source path, dimensions, and check parameters. Automated geometry and mesh checks do not replace slicer inspection or a physical fit test.

The checked-in `exports/inner_maze/` and `exports/outer_maze/` directories contain default examples.
