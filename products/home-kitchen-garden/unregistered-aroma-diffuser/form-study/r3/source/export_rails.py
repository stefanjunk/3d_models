"""Extract dense guide rails from the actual parametric surface for shared analysis.

Four angular samples are used only to locate centre/edge landmarks; this does
not export a coarse manufacturing mesh. No curve is refitted or smoothed.
"""
import json
from pathlib import Path
import numpy as np
from geometry import envelope

root = Path(__file__).resolve().parent.parent
p = json.loads((root / "parameters.json").read_text())
na, nz = 4, 5000
body_n = int(nz * p["petal_split_fraction"])
petal_n = nz - body_n
vertices, _ = envelope(p, na=na, nz=nz)
body_count = (body_n + 1) * na
start = 2 * body_count
width = na // 2 + 1
end = start + (petal_n - 1) * width
tip = start + 2 * (petal_n - 1) * width
out = root / "validation"
out.mkdir(exist_ok=True)
for name, body_index, petal_index in [("crest", 0, 1), ("edge", 3, 0)]:
    points = np.vstack([vertices[body_index:body_count:na],
                        vertices[start+petal_index:end:width], vertices[tip]])
    np.savetxt(out / (name + "-rail.csv"), points, delimiter=",", header="x,y,z", comments="")
