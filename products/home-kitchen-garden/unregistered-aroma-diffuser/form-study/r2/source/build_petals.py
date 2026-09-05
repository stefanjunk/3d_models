"""Build the R3 bundled-petal alternative in the same R2 studio.

Authoritative source set: this file, petal_envelope.py, build_fluent.py and parameters.json.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_fluent
from petal_envelope import envelope
build_fluent.envelope=envelope
build_fluent.run()
