#!/usr/bin/env python3
from __future__ import annotations
import os, subprocess, sys
from pathlib import Path

def locate() -> Path:
    env=os.environ.get('FDM_MECH_LIBRARY_ROOT')
    if env and (Path(env)/'tools/query_catalog.py').is_file(): return Path(env)
    here=Path(__file__).resolve()
    for parent in here.parents:
        if (parent/'tools/query_catalog.py').is_file() and (parent/'catalog/catalog.json').is_file(): return parent
    cwd=Path.cwd()
    for parent in [cwd,*cwd.parents]:
        if (parent/'tools/query_catalog.py').is_file() and (parent/'catalog/catalog.json').is_file(): return parent
    raise SystemExit('Library root not found. Set FDM_MECH_LIBRARY_ROOT.')
root=locate()
raise SystemExit(subprocess.call([sys.executable,str(root/'tools/query_catalog.py'),*sys.argv[1:]],cwd=root))
