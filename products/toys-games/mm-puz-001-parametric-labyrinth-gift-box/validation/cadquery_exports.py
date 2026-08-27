"""Named exported STEP results for the CadQuery validation utility."""

from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parent.parent

inner_maze_inner = cq.importers.importStep(
    str(ROOT / "exports" / "inner_maze" / "inner.step")
)
inner_maze_outer = cq.importers.importStep(
    str(ROOT / "exports" / "inner_maze" / "outer.step")
)
outer_maze_inner = cq.importers.importStep(
    str(ROOT / "exports" / "outer_maze" / "inner.step")
)
outer_maze_outer = cq.importers.importStep(
    str(ROOT / "exports" / "outer_maze" / "outer.step")
)
