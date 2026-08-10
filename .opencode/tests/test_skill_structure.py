import json
import re
import unittest
from pathlib import Path


SKILLS_ROOT = Path(__file__).parents[1] / "skills"
AGENTS_ROOT = Path(__file__).parents[1] / "agents"
EXPECTED_SKILLS = {
    "3d-print-heightmap-relief": [
        "scripts/prepare_heightmap.py",
        "scripts/relief_patch.py",
    ],
    "bosl2-commercial": [],
    "commercial-cad-provenance": [
        "references/commercial-license-policy.json",
        "references/library-allowlist.md",
        "references/library-registry.json",
        "references/provenance-schema.json",
        "scripts/check_provenance.py",
    ],
    "commercial-component-interfaces": [],
    "casting-negative-molds": [
        "scripts/common/mesh_preflight.py",
        "scripts/common/shrinkage_calculator.py",
    ],
    "cq-warehouse-commercial": [],
    "fdm-process-envelope": [
        "references/coupon-matrix.md",
        "references/nozzle-classes.json",
        "scripts/evaluate_process_envelope.py",
    ],
    "fdm-joints-and-fits": ["scripts/generate_fit_coupon.py"],
    "functional-3d-design": [
        "references/design-spec-template.json",
        "references/material-selection.md",
        "references/print-vs-buy.md",
        "scripts/validate_design_spec.py",
        "scripts/validate_design_intake.py",
    ],
    "mesh-validation": [
        "scripts/validate_mesh.py",
        "scripts/estimate_memory.py",
    ],
    "organic-mesh-functionalization": [
        "scripts/validate_edit.py",
        "scripts/section_report.py",
    ],
    "snap-fit-design": ["scripts/snapfit_calculator.py"],
    "power-transmission-design": ["scripts/screen_transmission.py"],
}


class SkillStructureTests(unittest.TestCase):
    def test_local_skills_have_matching_minimal_frontmatter(self) -> None:
        discovered = sorted(path.parent for path in SKILLS_ROOT.glob("*/SKILL.md"))
        self.assertEqual({path.name for path in discovered}, set(EXPECTED_SKILLS))
        declared_names: list[str] = []
        for directory in discovered:
            name = directory.name
            with self.subTest(skill=name):
                text = (directory / "SKILL.md").read_text(encoding="utf-8")
                match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
                self.assertIsNotNone(match)
                frontmatter = match.group(1)
                self.assertIn(f"name: {name}", frontmatter)
                self.assertRegex(frontmatter, r"(?m)^description: Use when .+")
                declared = re.search(r"(?m)^name:\s*(\S+)\s*$", frontmatter)
                self.assertIsNotNone(declared)
                declared_names.append(declared.group(1))
        self.assertEqual(len(declared_names), len(set(declared_names)))

    def test_supporting_files_exist(self) -> None:
        for name, relative_paths in EXPECTED_SKILLS.items():
            for relative_path in relative_paths:
                with self.subTest(skill=name, path=relative_path):
                    self.assertTrue((SKILLS_ROOT / name / relative_path).is_file())

    def test_json_references_and_templates_parse(self) -> None:
        roots = [
            SKILLS_ROOT,
            Path(__file__).parents[1] / "templates",
            Path(__file__).parents[2] / "libraries",
        ]
        for root in roots:
            for path in root.rglob("*.json"):
                with self.subTest(path=path):
                    json.loads(path.read_text(encoding="utf-8"))

    def test_medium_general_uses_exact_gate_vocabulary(self) -> None:
        text = (AGENTS_ROOT / "medium-general.md").read_text(encoding="utf-8")
        for status in (
            "COMMERCIAL_LICENSE_PASS",
            "BLOCKED_LIBRARY_ASSET",
            "ENGINEERING_DECISION_PASS",
            "ENGINEERING_DECISION_BLOCKED",
        ):
            self.assertIn(status, text)


if __name__ == "__main__":
    unittest.main()
