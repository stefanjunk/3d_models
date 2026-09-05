"""Export a reduced-tessellation un-bevelled envelope for the shared sweep runner.

This is a geometry adapter, not a substitute validation implementation.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from build_fluent import ROOT, envelope

parser = argparse.ArgumentParser()
parameters = json.loads((ROOT / "parameters.json").read_text())
for name in parameters["allowed_ranges"]:
    parser.add_argument("--" + name, type=float, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
for name, limits in parameters["allowed_ranges"].items():
    value = getattr(args, name)
    if not limits[0] <= value <= limits[1]:
        raise ValueError(name)
    parameters[name] = int(value) if name == "rib_count" else value
vertices, faces = envelope(parameters, na=168, nz=100)
with args.output.open("w") as f:
    f.write("# mm; parameter diagnostic, NOT FOR PRINT\n")
    for v in vertices:
        f.write("v %.7f %.7f %.7f\n" % tuple(v))
    for a, b, c, d in faces:
        f.write("f %d %d %d\nf %d %d %d\n" % (a+1,b+1,c+1,a+1,c+1,d+1))
np.savetxt(args.output.parent / "rib-rail.csv", vertices[:168*101].reshape(101,168,3)[:,0,:], delimiter=",", header="x,y,z", comments="")
(args.output.parent / "parameters.json").write_text(json.dumps(parameters, indent=2)+"\n")
