"""CadQuery handoff pattern: combine an imported aesthetic STEP shell with late exact features.

Replace the illustrative dimensions and feature selectors with project data.
The key pattern is architectural: import/construct the approved envelope first,
then regenerate holes, seats, split interfaces, and other exact features rather
than deforming those features with the freeform shell.
"""
from pathlib import Path

import cadquery as cq

ENVELOPE_STEP = Path("source/aesthetic-envelope.step")
OUTPUT_STEP = Path("exports/final-with-exact-features.step")
OUTPUT_STL = Path("exports/final-with-exact-features.stl")

body = cq.importers.importStep(str(ENVELOPE_STEP))

# Example late feature: exact through-hole from an authoritative datum.
# In production, establish the workplane from named hardpoints/axes.
result = (
    body
    .faces(">Z")
    .workplane(centerOption="CenterOfMass")
    .hole(4.2)
)

OUTPUT_STEP.parent.mkdir(parents=True, exist_ok=True)
cq.exporters.export(result, str(OUTPUT_STEP), exportType="STEP", unit="MM")
cq.exporters.export(result, str(OUTPUT_STL), exportType="STL", tolerance=0.05, angularTolerance=0.08, unit="MM")
