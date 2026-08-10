import hashlib
import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "functional-3d-design"
    / "scripts"
    / "validate_design_intake.py"
)
VALID_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def create_intake(root: Path) -> Path:
    references = root / "references"
    references.mkdir()
    summary = references / "requirements-summary.md"
    prompt = references / "concept-prompt-v1.md"
    image = references / "concept-v1.png"
    summary.write_text("# Approved requirements\n", encoding="utf-8")
    prompt.write_text("# Approved concept prompt\n", encoding="utf-8")
    image.write_bytes(VALID_PNG)
    intake = root / "design-intake.json"
    intake.write_text(
        json.dumps(
            {
                "project": "test-object",
                "requirements_summary": "references/requirements-summary.md",
                "requirements_summary_sha256": hashlib.sha256(summary.read_bytes()).hexdigest(),
                "requirements_status": "APPROVED",
                "requirements_approved_at": "2026-08-09T12:00:00Z",
                "requirements_approval_note": "User approved the summarized requirements.",
                "concept_prompt": "references/concept-prompt-v1.md",
                "concept_requirements_sha256": hashlib.sha256(summary.read_bytes()).hexdigest(),
                "concept_prompt_sha256": hashlib.sha256(prompt.read_bytes()).hexdigest(),
                "concept_image": "references/concept-v1.png",
                "concept_image_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                "concept_status": "APPROVED",
                "concept_approved_at": "2026-08-09T12:05:00Z",
                "concept_approval_note": "User approved concept V1.",
            }
        ),
        encoding="utf-8",
    )
    return intake


def run(path: Path, expected_project: str | None = "test-object") -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), str(path)]
    if expected_project is not None:
        command.extend(["--expected-project", expected_project])
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )


class DesignIntakeTests(unittest.TestCase):
    def test_approved_hashed_artifacts_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run(create_intake(Path(tmp)))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "DESIGN_INTAKE_PASS")

    def test_changed_summary_invalidates_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            intake = create_intake(root)
            (root / "references" / "requirements-summary.md").write_text(
                "# Changed after approval\n", encoding="utf-8"
            )
            result = run(intake)
        self.assertEqual(result.returncode, 2)
        self.assertIn("requirements_summary_sha256 mismatch", result.stdout)

    def test_rejects_pending_concept(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            intake = create_intake(root)
            data = json.loads(intake.read_text(encoding="utf-8"))
            data["concept_status"] = "PENDING"
            intake.write_text(json.dumps(data), encoding="utf-8")
            result = run(intake)
        self.assertEqual(result.returncode, 2)
        self.assertIn("concept_status must be APPROVED", result.stdout)

    def test_rejects_invalid_image_and_reversed_approval_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            intake = create_intake(root)
            image = root / "references" / "concept-v1.png"
            image.write_bytes(b"\x89PNG\r\n\x1a\nnot-an-image")
            data = json.loads(intake.read_text(encoding="utf-8"))
            data["concept_image_sha256"] = hashlib.sha256(image.read_bytes()).hexdigest()
            data["concept_approved_at"] = "2026-08-09T11:59:00Z"
            intake.write_text(json.dumps(data), encoding="utf-8")
            result = run(intake)
        self.assertEqual(result.returncode, 2)
        self.assertIn("not a supported", result.stdout)
        self.assertIn("must be later", result.stdout)

    def test_standalone_validator_rejects_wrong_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run(create_intake(Path(tmp)), expected_project="other-object")
        self.assertEqual(result.returncode, 2)
        self.assertIn("project does not match expected project", result.stdout)


if __name__ == "__main__":
    unittest.main()
