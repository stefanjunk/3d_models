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
