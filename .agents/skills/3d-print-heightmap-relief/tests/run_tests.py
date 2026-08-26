#!/usr/bin/env python3
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
raise SystemExit(subprocess.call([sys.executable, "-m", "unittest", "-v", "test_aspect_pipeline.py"], cwd=ROOT))
