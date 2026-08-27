# Parametric Labyrinth Gift Box Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a tested Python/CadQuery generator that exports two printable gift-box parts with a uniquely solvable cylindrical maze on either mating surface.

**Architecture:** Keep graph generation and preflight independent from CadQuery so uniqueness and safety can be unit-tested without geometry. Convert accepted graph edges into annular and axial channel cutters, then create the cup, sleeve, and follower as valid single-solid B-Reps.

**Tech Stack:** Python 3, CadQuery 2.8, `unittest`, Trimesh 5, standard-library `argparse` and `json`.

---

### Task 1: Maze Model And Perfect-Maze Generation

**Files:**
- Create: `labyrinth_box/__init__.py`
- Create: `labyrinth_box/maze.py`
- Create: `tests/test_maze.py`

**Steps:**
1. Write failing tests for deterministic output, graph connectivity, edge count `nodes - 1`, cylindrical seam neighbors, and exactly one entry-to-exit path.
2. Run `python3 -m unittest tests/test_maze.py -v` and confirm failures are caused by missing implementation.
3. Implement immutable cell/edge data, wrapped neighbors, seeded DFS generation, path extraction, and path counting.
4. Re-run the focused test file and confirm all tests pass.

### Task 2: Difficulty And FDM Preflight

**Files:**
- Create: `labyrinth_box/config.py`
- Create: `labyrinth_box/preflight.py`
- Create: `tests/test_preflight.py`

**Steps:**
1. Write failing tests for difficulty-to-grid scaling, residual wall checks, valid default dimensions, and warning plus failure for an undersized high-difficulty request.
2. Run `python3 -m unittest tests/test_preflight.py -v` and verify expected failures.
3. Implement frozen configuration, derived dimensions, printable grid capacity, warnings, and validation errors.
4. Re-run focused tests, then run all graph/preflight tests.

### Task 3: CadQuery Geometry

**Files:**
- Create: `labyrinth_box/geometry.py`
- Create: `tests/test_geometry.py`

**Steps:**
1. Write failing tests asserting two valid single solids, cavity bounds, overall dimensions, and both maze-location modes.
2. Run `python3 -m unittest tests/test_geometry.py -v` and confirm geometry functions are missing.
3. Implement cup and sleeve revolved profiles, annular-sector and axial channel cutters, lead-in, and follower tabs.
4. Validate solids with CadQuery and re-run all tests.

### Task 4: Export CLI And Manifest

**Files:**
- Create: `generate_labyrinth_box.py`
- Create: `tests/test_cli.py`
- Create: `pyproject.toml`

**Steps:**
1. Write a failing CLI test that exports two STL files, two STEP files, assembly STEP, and manifest into a temporary directory.
2. Run `python3 -m unittest tests/test_cli.py -v` and confirm the expected failure.
3. Implement argument parsing, generation, path verification, export, and manifest serialization.
4. Re-run the CLI test and full test suite.

### Task 5: Documentation And Samples

**Files:**
- Create: `README.md`
- Create: `exports/inner_maze/*`
- Create: `exports/outer_maze/*`

**Steps:**
1. Document parameters, safety behavior, export commands, print orientation, slicer guidance, and fit-coupon recommendation.
2. Export default examples for `maze_location=inner` and `maze_location=outer`.
3. Record manifest values and dimensions for both samples.

### Task 6: Geometry, Mesh, Visual, And FDM Gates

**Files:**
- Create: `reports/*.cadquery.json`
- Create: `reports/*.mesh.json`
- Create: `reports/*.fdm.json`
- Create: `previews/*.png`

**Steps:**
1. Run the complete `unittest` suite.
2. Inspect each named CadQuery result and export/reload it.
3. Run mesh validation on all sample STL files with one-body limits.
4. Run FDM inspection with PLA, 0.4 mm nozzle, 0.2 mm layer, and declared minimum features.
5. Render and inspect multiple angles of both parts and separated assemblies.
6. Review the implementation against every approved requirement and document any residual physical-test risk.
