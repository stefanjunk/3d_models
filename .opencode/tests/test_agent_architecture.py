import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
OPENCODE = ROOT / ".opencode"
AGENTS = OPENCODE / "agents"
COMMANDS = OPENCODE / "commands"


class AgentArchitectureTests(unittest.TestCase):
    def test_project_config_selects_control_plane_and_preserves_image_plugin(self) -> None:
        config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
        self.assertEqual(config["default_agent"], "3d-design")
        self.assertIn(".opencode/instructions/3d-design-policy.md", config["instructions"])
        self.assertIn("opencode-gpt-imagegen@0.1.9", config["plugin"])
        self.assertTrue(config["agent"]["build"]["disable"])

    def test_production_commands_do_not_bypass_primary(self) -> None:
        allowed = {"3d-design", "cad-reviewer"}
        for path in COMMANDS.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            match = re.search(r"(?m)^agent:\s*(\S+)\s*$", text)
            self.assertIsNotNone(match, path)
            self.assertIn(match.group(1), allowed, path)

    def test_leaf_agents_are_flat_and_models_are_explicit(self) -> None:
        for path in AGENTS.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertRegex(text, r"(?m)^model:\s*\S+", path)
            if path.name != "3d-design.md":
                self.assertRegex(text, r"(?m)^\s*task:\s*deny\s*$", path)

    def test_sol_is_frontier_only_and_bounded(self) -> None:
        sol_agents = []
        for path in AGENTS.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            if re.search(r"(?m)^model:\s*openai/gpt-5\.6-sol\s*$", text):
                sol_agents.append(path.name)
        self.assertEqual(sol_agents, ["frontier.md"])
        primary = (AGENTS / "3d-design.md").read_text(encoding="utf-8")
        self.assertIn("at most one frontier call per user request", primary)

    def test_specialist_skills_are_reachable(self) -> None:
        required = (
            "3d-print-heightmap-relief",
            "organic-mesh-functionalization",
            "casting-negative-molds",
        )
        for agent in ("medium-general.md", "medium-coding.md", "frontier.md", "cad-reviewer.md"):
            text = (AGENTS / agent).read_text(encoding="utf-8")
            for skill in required:
                self.assertIn(f'"{skill}": allow', text, f"{agent}: {skill}")

    def test_two_human_gates_are_mandatory(self) -> None:
        policy = (OPENCODE / "instructions" / "3d-design-policy.md").read_text(encoding="utf-8")
        primary = (AGENTS / "3d-design.md").read_text(encoding="utf-8")
        for phrase in ("Requirements approval", "Concept-image approval", "DESIGN_INTAKE_PASS"):
            self.assertIn(phrase, policy)
        self.assertIn("Never combine the two approval questions", primary)
        self.assertIn("gpt_imagegen: allow", primary)

    def test_runtime_prompts_do_not_require_uninstalled_placeholder_skills(self) -> None:
        prohibited = (
            "cadquery-functional-geometry",
            "implicit-3d-modeling",
            "fdm-printability",
            "parameter-sweep",
        )
        text = (OPENCODE / "instructions" / "3d-design-policy.md").read_text(encoding="utf-8")
        text += "\n" + "\n".join(path.read_text(encoding="utf-8") for path in AGENTS.glob("*.md"))
        for skill in prohibited:
            self.assertNotIn(f'"{skill}": allow', text)
            self.assertNotIn(f"`{skill}`", text)

    def test_retired_domain_agents_are_absent(self) -> None:
        for name in (
            "cad-microtask.md",
            "mesh-microtask.md",
            "organic-mesh-engineer.md",
            "organic-mesh-reviewer.md",
        ):
            self.assertFalse((AGENTS / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
