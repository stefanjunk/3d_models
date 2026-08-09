from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "scripts" / "common"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def test_shrinkage_formula(tmp_path: Path) -> None:
    out = tmp_path / "scale.json"
    result = run_script(
        COMMON / "shrinkage_calculator.py",
        "--final", "300", "100", "50",
        "--shrink", "10", "20", "0",
        "--json", str(out),
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(out.read_text())
    assert data["tool_or_green_dimensions_mm"][0] == pytest.approx(333.333333, rel=1e-6)
    assert data["tool_or_green_dimensions_mm"][1] == pytest.approx(125.0)
    assert data["tool_or_green_dimensions_mm"][2] == pytest.approx(50.0)


def test_memory_estimator_heightmap() -> None:
    result = run_script(
        COMMON / "memory_estimator.py",
        "--physical-size-mm", "200", "200",
        "--sample-pitch-mm", "0.2",
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["heightmap_sampling"]["derived_pixels"] == [1001, 1001]
    assert data["heightmap_mesh"]["triangles"] == 2_000_000


def test_heightmap_preparation(tmp_path: Path) -> None:
    src = tmp_path / "source.png"
    dst = tmp_path / "height.png"
    arr = np.tile(np.arange(32, dtype=np.uint8), (24, 1))
    Image.fromarray(arr).save(src)
    result = run_script(
        COMMON / "prepare_heightmap.py",
        str(src), str(dst),
        "--pixels", "101", "51",
        "--mode", "tile",
        "--tile-count", "2", "1",
        "--invert",
    )
    assert result.returncode == 0, result.stderr
    image = Image.open(dst)
    assert image.size == (101, 51)
    assert image.mode in {"I;16", "I"}


def test_planner_food_bowl(tmp_path: Path) -> None:
    spec = ROOT / "assets" / "examples" / "food-bowl.json"
    out = tmp_path / "plan.md"
    result = run_script(COMMON / "mold_planner.py", str(spec), "--output", str(out))
    assert result.returncode == 0, result.stderr
    text = out.read_text()
    assert "printed_case_to_plaster" in text
    assert "Compensation scale" in text
    assert "migration" in text.lower()


def test_mesh_preflight_closed_cube(tmp_path: Path) -> None:
    trimesh = pytest.importorskip("trimesh")
    cube = tmp_path / "cube.stl"
    report = tmp_path / "report.json"
    trimesh.creation.box(extents=(10, 20, 30)).export(cube)
    result = run_script(COMMON / "mesh_preflight.py", str(cube), "--json", str(report))
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(report.read_text())
    assert data["mesh"]["watertight"] is True
    assert data["topology"]["boundary_edges"] == 0
