from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[4]
SCRIPT = REPO / ".agents/skills/3d-skill-maintainer/scripts/learning_records.py"
FILAMENT_EVAL = REPO / ".agents/skills/3d-skill-maintainer/scripts/evaluate_filament_identity.py"
FIXTURE = REPO / "libraries/3d-learning/evals/interfaces/fixtures/sunlu-pla-plus-silver-label.json"


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO,
        check=False,
        text=True,
        capture_output=True,
    )


def test_full_store_validates_and_audits() -> None:
    validated = run_script("validate")
    assert validated.returncode == 0, validated.stdout + validated.stderr
    assert json.loads(validated.stdout)["status"] == "pass"

    audited = run_script("audit")
    assert audited.returncode == 0, audited.stdout + audited.stderr
    assert json.loads(audited.stdout)["status"] == "pass"


def test_candidates_are_opt_in_and_clearly_labeled() -> None:
    default = run_script("retrieve", "--material", "SUNLU PLA+ Silver")
    assert default.returncode == 0
    assert json.loads(default.stdout)["count"] == 0

    included = run_script(
        "retrieve",
        "--material",
        "SUNLU PLA+ Silver",
        "--feature",
        "filament-profile",
        "--include-candidates",
    )
    result = json.loads(included.stdout)
    assert included.returncode == 0
    assert result["results"][0]["id"] == "EXP-00001"
    assert result["results"][0]["warning"] == "UNVALIDATED CANDIDATE"


def test_promotion_is_fail_closed_without_human_approval() -> None:
    result = run_script(
        "promotion-check",
        "libraries/3d-learning/experience/candidates/EXP-00001.yaml",
        "--target",
        "E1",
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "blocked"
    assert payload["mutated"] is False
    assert any("human review" in error for error in payload["errors"])
    assert any("same-scope" in error for error in payload["errors"])


def test_filament_fixture_passes_and_overtemperature_fails(tmp_path: Path) -> None:
    passing = subprocess.run(
        [sys.executable, str(FILAMENT_EVAL), str(FIXTURE)],
        cwd=REPO,
        check=False,
        text=True,
        capture_output=True,
    )
    assert passing.returncode == 0, passing.stdout + passing.stderr

    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["proposals"][1]["temperature_c"] = 225
    failing_fixture = tmp_path / "overtemperature.json"
    failing_fixture.write_text(json.dumps(data), encoding="utf-8")
    failing = subprocess.run(
        [sys.executable, str(FILAMENT_EVAL), str(failing_fixture)],
        cwd=REPO,
        check=False,
        text=True,
        capture_output=True,
    )
    assert failing.returncode == 1
    assert "outside the exact label range" in failing.stdout


def test_templates_are_valid_yaml_and_match_schemas() -> None:
    template_dir = REPO / "libraries/3d-learning/templates"
    for template in sorted(template_dir.glob("*.yaml")):
        assert isinstance(yaml.safe_load(template.read_text(encoding="utf-8")), dict)
        result = run_script("validate", str(template))
        assert result.returncode == 0, result.stdout + result.stderr


REGISTRY = REPO / "libraries/3d-learning/knowledge/processes/fff-calibration-registry.yaml"


def test_calibration_registry_is_wellformed() -> None:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    assert data["kind"] == "process-calibration-registry"
    quantity_ids = [q["id"] for q in data["quantities"]]
    assert len(quantity_ids) == len(set(quantity_ids))
    # Every quantity must name the coupon that qualifies it, so an UNQUALIFIED
    # lookup is directly actionable.
    for quantity in data["quantities"]:
        assert quantity.get("coupon"), quantity["id"]
        assert quantity.get("unit"), quantity["id"]
    process_ids = [p["id"] for p in data["processes"]]
    assert len(process_ids) == len(set(process_ids))
    for process in data["processes"]:
        for key in ("process", "machine", "material", "nozzle", "slicer_profile"):
            assert key in process["scope"], (process["id"], key)


def test_calibration_fails_closed_when_unqualified() -> None:
    result = run_script(
        "calibration",
        "--machine", "Anycubic Kobra 3 Max",
        "--material", "SUNLU PETG",
        "--nozzle", "0.6",
        "--quantity", "xy_clearance_sliding",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "UNQUALIFIED"
    assert payload["qualified"] == {}
    assert payload["unqualified"][0]["quantity"] == "xy_clearance_sliding"
    assert payload["unqualified"][0]["coupon"] == "fit-coupon-xy-series"


def test_calibration_reports_missing_process_identity() -> None:
    result = run_script(
        "calibration",
        "--machine", "Machine That Does Not Exist",
        "--material", "PLA",
        "--nozzle", "0.4",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "NO_MATCHING_PROCESS"
    assert payload["matched_process_ids"] == []


def test_calibration_rejects_unknown_quantity() -> None:
    result = run_script(
        "calibration",
        "--machine", "Anycubic Kobra 3 Max",
        "--material", "SUNLU PETG",
        "--nozzle", "0.6",
        "--quantity", "not-a-quantity",
    )
    assert result.returncode == 2
    assert "unknown quantity" in result.stderr


def test_calibration_returns_a_qualified_value(tmp_path: Path) -> None:
    """A QUALIFIED entry must be returned with its evidence and exit zero."""
    library = tmp_path / "libraries" / "3d-learning"
    (library / "knowledge" / "processes").mkdir(parents=True)
    (library / "schemas").mkdir(parents=True)
    source = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    source["processes"][0]["values"] = {
        "xy_clearance_sliding": {
            "state": "QUALIFIED",
            "value": 0.35,
            "unit": "mm",
            "evidence": "libraries/3d-learning/benchmarks/measurements/BENCH-fit-0001.yaml",
            "maturity": "E1",
        }
    }
    target = library / "knowledge" / "processes" / "fff-calibration-registry.yaml"
    target.write_text(yaml.safe_dump(source), encoding="utf-8")

    scope = source["processes"][0]["scope"]
    result = subprocess.run(
        [
            sys.executable, str(SCRIPT), "--root", str(tmp_path), "calibration",
            "--machine", scope["machine"],
            "--material", scope["material"],
            "--nozzle", str(scope["nozzle"]),
            "--quantity", "xy_clearance_sliding",
        ],
        cwd=REPO, check=False, text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "QUALIFIED"
    assert payload["qualified"]["xy_clearance_sliding"]["value"] == 0.35
    assert payload["qualified"]["xy_clearance_sliding"]["maturity"] == "E1"
