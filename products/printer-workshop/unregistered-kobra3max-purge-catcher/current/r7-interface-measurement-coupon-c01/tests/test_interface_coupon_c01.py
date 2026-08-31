from __future__ import annotations

import json
from pathlib import Path

import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "params/interface-coupon-c01.json").read_text(encoding="utf-8"))
RUN = ROOT / "build/run-001"
REPORT = json.loads((RUN / "reports/generation-report.json").read_text(encoding="utf-8"))
STL = RUN / "models/stl/DRAFT-R7-C01-interface-measurement-coupon.stl"


def test_clean_room_scope_and_release_boundary() -> None:
    assert PARAMS["evidence_scope"]["third_party_geometry_inputs"] == []
    assert PARAMS["evidence_scope"]["third_party_dimensions_used"] is False
    assert PARAMS["release_boundary"]["classification"] == "MEASUREMENT_COUPON_ONLY"
    assert PARAMS["release_boundary"]["powered_motion_allowed"] is False
    assert PARAMS["release_boundary"]["full_diverter_generation_allowed"] is False


def test_every_mount_tab_has_exact_owned_pitch_and_round_holes() -> None:
    assert len(REPORT["mount_tabs"]) == 11
    for tab in REPORT["mount_tabs"]:
        assert abs(tab["center_pitch_mm"] - 17.0) < 1.0e-9
        assert tab["hole_kind"] == "two closed circular through holes"
        assert tab["slot_features"] == 0
    assert REPORT["geometry"]["slot_features"] == 0
    assert REPORT["geometry"]["all_mounting_holes_closed_and_round"] is True


def test_candidate_ranges_cover_without_assuming_a_standard() -> None:
    holes = PARAMS["mount_tabs"]["hole_diameter_candidates_mm"]
    heads = PARAMS["head_gauge"]["notch_width_candidates_mm"]
    assert holes == [2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8]
    assert heads == [4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5]


def test_mesh_is_watertight_and_has_expected_loose_tools() -> None:
    mesh = trimesh.load_mesh(STL, process=True)
    assert mesh.is_watertight
    assert mesh.is_winding_consistent
    assert len(mesh.split(only_watertight=False)) == 13
    assert REPORT["geometry"]["actual_components"] == 13
    assert REPORT["mass_estimate_g"] < 30.0
