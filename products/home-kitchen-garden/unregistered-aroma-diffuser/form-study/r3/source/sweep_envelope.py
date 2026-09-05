"""Reduced-tessellation geometry adapter for the shared topology sweep runner."""
import argparse
import json
from pathlib import Path
from geometry import envelope

root = Path(__file__).resolve().parent.parent
parameters = json.loads((root / "parameters.json").read_text())
parser = argparse.ArgumentParser()
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
    f.write("# mm; reduced diagnostic, NOT FOR PRINT\n")
    for v in vertices:
        f.write("v %.7f %.7f %.7f\n" % tuple(v))
    for face in faces:
        for i in range(1, len(face)-1):
            f.write("f %d %d %d\n" % (face[0]+1, face[i]+1, face[i+1]+1))
(args.output.parent / "parameters.json").write_text(json.dumps(parameters, indent=2) + "\n")
