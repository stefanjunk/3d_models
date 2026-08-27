from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from fdm_validation.common import check, exit_code, sha256_file, status_from_checks  # noqa: E402
from fdm_validation.autonomy import (  # noqa: E402
    approve_agent_stage,
    approve_human_stage,
    init_policy,
    request_human_approval,
    validate_approvals,
    validate_policy,
)
from fdm_validation.gcode import analyze  # noqa: E402
from fdm_validation.freeze import freeze_project  # noqa: E402
from fdm_validation.profile import validate_profile  # noqa: E402
from fdm_validation.project import validate_project  # noqa: E402
from fdm_validation.slicer import slice_anycubic_next  # noqa: E402
from fdm_validation.skillcheck import validate as validate_skill  # noqa: E402
from fdm_validation.sweep import generate_cases, run as run_sweep  # noqa: E402
from fdm_validation.threemf import REL_NS, validate as validate_3mf  # noqa: E402


MODEL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <resources>
    <basematerials id="1"><base name="orange" displaycolor="#FF6600FF"/></basematerials>
    <object id="2" type="model" name="triangle" pid="1" pindex="0">
      <mesh>
        <vertices>
          <vertex x="0" y="0" z="0"/><vertex x="1" y="0" z="0"/><vertex x="0" y="1" z="0"/>
        </vertices>
        <triangles><triangle v1="0" v2="1" v3="2"/></triangles>
      </mesh>
    </object>
  </resources>
  <build><item objectid="2"/></build>
</model>
"""

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
"""

RELATIONSHIPS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""


class CoreTests(unittest.TestCase):
    def test_all_json_assets_parse(self) -> None:
        for path in sorted((ROOT / "assets").rglob("*.json")):
            with self.subTest(path=path):
                json.loads(path.read_text(encoding="utf-8"))

    def test_autonomous_print_candidate_and_signed_human_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            policy_path = root / "autonomy.json"
            agent_ledger = root / "agent.json"
            human_ledger = root / "human.json"
            self.assertEqual(init_policy("part", "autonomous-to-print-candidate", "project-owner", policy_path)["status"], "PASS")
            self.assertEqual(validate_policy(policy_path)["status"], "PASS")

            artifact = root / "candidate.3mf"
            artifact.write_bytes(b"candidate")
            evidence_report = root / "evidence.json"
            evidence_report.write_text(json.dumps({
                "schema_version": "1.0",
                "tool": "test-validator",
                "status": "PASS",
                "inputs": [{"path": str(artifact), "sha256": sha256_file(artifact), "size_bytes": artifact.stat().st_size}],
                "checks": [{"id": "acceptance", "status": "PASS", "required": True}],
            }), encoding="utf-8")

            for stage in ("requirements-normalization", "concept", "decomposition"):
                result = approve_agent_stage(policy_path, agent_ledger, stage, agent_id="agent-1", model_id="local-27b", evidence=[], attestation=f"{stage} contract satisfied")
                self.assertEqual(result["status"], "PASS", result)
            for stage in ("parametric-source", "mesh-generation", "interface-validation", "slicer-preflight", "print-candidate"):
                result = approve_agent_stage(policy_path, agent_ledger, stage, agent_id="agent-1", model_id="local-27b", evidence=[evidence_report])
                self.assertEqual(result["status"], "PASS", result)
            candidate = validate_approvals(policy_path, agent_ledger, target_stage="print-candidate")
            self.assertEqual(candidate["status"], "PASS", candidate)

            project_path = root / "validation-project.json"
            project_path.write_text(json.dumps({
                "schema_version": "1.0",
                "project": {"id": "part", "revision": "R1", "units": "mm", "risk_class": "decorative"},
                "artifacts": [
                    {"id": "policy", "path": policy_path.name, "kind": "autonomy-policy", "revision": "R1", "sha256": sha256_file(policy_path)},
                    {"id": "agent-ledger", "path": agent_ledger.name, "kind": "approval-ledger", "revision": "R1", "sha256": sha256_file(agent_ledger)},
                ],
                "checks": [{"id": "candidate-provenance", "type": "approvals", "policy_artifact": "policy", "agent_ledger_artifact": "agent-ledger", "target_stage": "print-candidate"}],
                "release": {"required_approvals": [], "approvals": {}},
            }), encoding="utf-8")
            integrated = validate_project(project_path, "release")
            self.assertEqual(integrated["status"], "PASS", integrated)

            before = agent_ledger.read_bytes()
            refused = approve_agent_stage(policy_path, agent_ledger, "physical-print", agent_id="agent-1", model_id="local-27b", evidence=[evidence_report])
            self.assertEqual(refused["status"], "FAIL", refused)
            self.assertEqual(agent_ledger.read_bytes(), before)

            physical_evidence = root / "print-observation.txt"
            physical_evidence.write_text("Printed and inspected by operator", encoding="utf-8")
            request_path = root / "physical-request.json"
            self.assertEqual(request_human_approval(policy_path, "physical-print", "part", [physical_evidence], request_path)["status"], "PASS")
            secret = root / "human.key"
            secret.write_bytes(b"human-controlled-test-key")
            approved = approve_human_stage(policy_path, request_path, human_ledger, human_id="operator-1", agent_ledger_path=agent_ledger, secret_file=secret, key_id="operator-key-1")
            self.assertEqual(approved["status"], "PASS", approved)
            verified = validate_approvals(policy_path, agent_ledger, target_stage="physical-print", human_ledger_path=human_ledger, human_secret_file=secret)
            self.assertEqual(verified["status"], "PASS", verified)

            wrong_secret = root / "wrong.key"
            wrong_secret.write_bytes(b"wrong")
            rejected = validate_approvals(policy_path, agent_ledger, target_stage="physical-print", human_ledger_path=human_ledger, human_secret_file=wrong_secret)
            self.assertEqual(rejected["status"], "FAIL", rejected)

    def test_agent_stage_is_blocked_by_non_pass_evidence_and_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            policy_path = root / "autonomy.json"
            agent_ledger = root / "agent.json"
            init_policy("part", "autonomous-to-print-candidate", "project-owner", policy_path)
            for stage in ("requirements-normalization", "concept", "decomposition"):
                approve_agent_stage(policy_path, agent_ledger, stage, agent_id="agent", model_id="27b", evidence=[], attestation="recorded")
            artifact = root / "source.step"
            artifact.write_text("source", encoding="utf-8")
            evidence = root / "failed.json"
            evidence.write_text(json.dumps({
                "tool": "test",
                "status": "NOT_RUN",
                "inputs": [{"path": str(artifact), "sha256": sha256_file(artifact)}],
                "checks": [{"id": "backend", "status": "NOT_RUN", "required": True}],
            }), encoding="utf-8")
            blocked = approve_agent_stage(policy_path, agent_ledger, "parametric-source", agent_id="agent", model_id="27b", evidence=[evidence])
            self.assertEqual(blocked["status"], "REVIEW_REQUIRED", blocked)
            self.assertEqual(json.loads(agent_ledger.read_text(encoding="utf-8"))["events"][-1]["decision"], "BLOCKED")
            evidence.write_text("{}", encoding="utf-8")
            validation = validate_approvals(policy_path, agent_ledger, target_stage="parametric-source")
            self.assertEqual(validation["status"], "FAIL", validation)

    def test_freeze_project_writes_hashes_without_overwriting_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "part.txt"
            artifact.write_text("part", encoding="utf-8")
            source = root / "validation-project.json"
            source.write_text(json.dumps({
                "schema_version": "1.0",
                "project": {"id": "freeze", "revision": "R1", "units": "mm", "risk_class": "decorative"},
                "artifacts": [{"id": "part", "path": "part.txt", "kind": "source"}],
                "checks": [{"id": "review", "type": "review", "status": "REVIEW_REQUIRED"}],
                "release": {"required_approvals": [], "approvals": {}},
            }), encoding="utf-8")
            original = source.read_bytes()
            output = root / "validation-project.lock.json"
            result = freeze_project(source, output)
            self.assertEqual(result["status"], "PASS", result)
            self.assertEqual(source.read_bytes(), original)
            frozen = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(frozen["artifacts"][0]["sha256"], sha256_file(artifact))

    def test_profile_requires_fail_closed_release_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profile.json"
            path.write_text(json.dumps({
                "schema_version": "1.0",
                "skill": "example",
                "artifact_roles": [{"id": "mesh", "kind": "mesh", "required": True}],
                "checks": [{"id": "audit", "type": "mesh", "required": True, "artifact_roles": ["mesh"]}],
                "manual_gates": [{"id": "fit", "kind": "physical", "required": True}],
                "release_policy": {
                    "block_statuses": ["FAIL", "NOT_RUN", "REVIEW_REQUIRED"],
                    "require_sha256": True,
                    "require_fresh_external_reports": True,
                },
            }), encoding="utf-8")
            self.assertEqual(validate_profile(path)["status"], "PASS")

    def test_status_is_fail_closed(self) -> None:
        self.assertEqual(status_from_checks([check("a", "PASS", "ok")]), "PASS")
        self.assertEqual(status_from_checks([check("a", "NOT_RUN", "missing")]), "NOT_RUN")
        self.assertEqual(status_from_checks([check("a", "REVIEW_REQUIRED", "review")]), "REVIEW_REQUIRED")
        self.assertEqual(status_from_checks([check("a", "FAIL", "bad")]), "FAIL")
        self.assertEqual(exit_code("NOT_RUN", "release"), 2)
        self.assertEqual(exit_code("NOT_RUN", "draft"), 0)

    def test_pairwise_cases_are_deterministic(self) -> None:
        parameters = {
            "wall": {"default": 2.4, "min": 1.8, "max": 4.0},
            "width": {"default": 60, "min": 40, "max": 100},
        }
        first = generate_cases(parameters)
        second = generate_cases(parameters)
        self.assertEqual(first, second)
        self.assertEqual(first[0]["id"], "default")
        self.assertGreaterEqual(len(first), 7)

    def test_sweep_refuses_nonempty_output_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "out"
            output.mkdir()
            (output / "stale.txt").write_text("stale", encoding="utf-8")
            manifest = root / "sweep.json"
            manifest.write_text(json.dumps({
                "command": [sys.executable, "-c", "print('ok')"],
                "parameters": {},
                "output_root": "out",
                "validators": [],
            }), encoding="utf-8")
            result = run_sweep(manifest)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue((output / "stale.txt").is_file())

    def test_gcode_parser_and_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.gcode"
            path.write_text(
                ";LAYER:0\nG90\nM82\nG1 X10 Y10 Z0.2 F1200\nG1 X20 E1.0 F600\nT1\n;LAYER:1\nG1 Z0.4\nG1 X30 E2.0 F600\n",
                encoding="utf-8",
            )
            result = analyze(path, {"max_tool_changes": 1, "bed_mm": [100, 100, 100], "require_layer_markers": True})
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["metrics"]["tool_changes"], 1)
            self.assertEqual(result["metrics"]["layers_from_comments"], 2)

    def test_anycubic_gcode_layer_and_normal_time_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "anycubic.gcode"
            path.write_text(
                "; total layer number: 2\n"
                ";LAYER_CHANGE\n;Z:0.2\nG90\nM83\nG1 X1 Y1 Z0.2 E0.1 F600\n"
                ";LAYER_CHANGE\n;Z:0.4\nG1 X2 Y2 Z0.4 E0.1 F600\n"
                "; total layers count = 2\n"
                "; estimated printing time (normal mode) = 10m 2s\n"
                "; estimated printing time (silent mode) = 14m 22s\n"
                "; estimated printing time (sport mode) = 9m 26s\n",
                encoding="utf-8",
            )
            result = analyze(path, {"require_layer_markers": True})
            self.assertEqual(result["status"], "PASS", result)
            self.assertEqual(result["metrics"]["layers_from_comments"], 2)
            self.assertEqual(result["metrics"]["layers_declared"], 2)
            self.assertEqual(result["metrics"]["slicer_metadata_time_s"], 602)

    def test_anycubic_off_by_one_footer_is_reported_without_discarding_executable_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "anycubic-summary.gcode"
            path.write_text(
                "; total layer number: 2\n"
                ";LAYER_CHANGE\n;Z:0.2\nG90\nM83\nG1 X1 Y1 Z0.2 E0.1 F600\n"
                ";LAYER_CHANGE\n;Z:0.4\nG1 X2 Y2 Z0.4 E0.1 F600\n"
                "; total layers count = 3\n",
                encoding="utf-8",
            )
            result = analyze(path, {"require_layer_markers": True})
            self.assertEqual(result["status"], "PASS", result)
            self.assertEqual(result["metrics"]["layers_declared"], 2)
            self.assertEqual(result["metrics"]["layers_declared_summary"], 3)
            summary_check = next(item for item in result["checks"] if item["id"] == "layer-summary-consistency")
            self.assertEqual(summary_check["status"], "REVIEW_REQUIRED")
            self.assertFalse(summary_check["required"])

    def test_anycubic_slicer_adapter_uses_boolean_default_filament_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slicer = root / "AnycubicSlicerNext"
            probe_side_effect = f"anycubic-probe-side-effect-{root.name}.json"
            slicer.write_text(
                "#!/usr/bin/env python3\n"
                "import json, pathlib, sys\n"
                "if '--help' in sys.argv:\n"
                f"    pathlib.Path({probe_side_effect!r}).write_text('probe', encoding='utf-8')\n"
                "    print('AnycubicSlicerNext-9.8.7:')\n"
                "    raise SystemExit(0)\n"
                "out = pathlib.Path(sys.argv[sys.argv.index('--outputdir') + 1])\n"
                "(out / 'plate_1.gcode').write_text('; total layer number: 1\\n;LAYER_CHANGE\\n;Z:0.2\\nG90\\nM83\\nG1 X1 Y1 Z0.2 E0.1 F600\\n; total layers count = 2\\n; estimated printing time (normal mode) = 1s\\n', encoding='utf-8')\n"
                "(out / 'result.json').write_text(json.dumps({'return_code': 0, 'error_string': 'Success.', 'plate_index': 0, 'sliced_plates': [{'id': 1, 'triangle_count': 12, 'warning_message': str(pathlib.Path.cwd())}]}), encoding='utf-8')\n",
                encoding="utf-8",
            )
            slicer.chmod(0o755)
            source = root / "part.stl"
            source.write_text("solid part\nendsolid part\n", encoding="utf-8")

            profiles = {}
            for kind in ("machine", "process", "filament"):
                path = root / f"{kind}.json"
                path.write_text(json.dumps({"type": kind, "name": f"Test {kind}"}), encoding="utf-8")
                profiles[kind] = path

            output = root / "slice"
            result = slice_anycubic_next(
                source,
                output,
                machine_profile=profiles["machine"],
                process_profile=profiles["process"],
                filament_profiles=[profiles["filament"]],
                executable=str(slicer),
            )
            self.assertEqual(result["status"], "PASS", result)
            self.assertEqual(result["slicer"]["version"], "9.8.7")
            self.assertFalse((Path.cwd() / probe_side_effect).exists())
            slicer_cwd = Path(result["native_result"]["sliced_plates"][0]["warning_message"])
            self.assertNotEqual(slicer_cwd, Path.cwd())
            self.assertTrue(slicer_cwd.name.startswith("fdm-anycubic-next-"))
            invocation = result["slicer"]["invocation"]
            flag_index = invocation.index("--load-defaultfila")
            self.assertNotEqual(invocation[flag_index + 1], "1")
            self.assertEqual(result["gcode_reports"]["plate_1.gcode"]["metrics"]["layers_from_comments"], 1)
            self.assertTrue(any(item["relative_path"] == "plate_1.gcode" for item in result["outputs"]))
            detail = next(item for item in result["checks"] if item["id"].endswith("layer-summary-consistency"))
            self.assertEqual(detail["status"], "REVIEW_REQUIRED")
            self.assertFalse(detail["required"])

    def test_anycubic_slicer_adapter_refuses_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "project.3mf"
            source.write_bytes(b"fixture")
            output = root / "slice"
            output.mkdir()
            sentinel = output / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            result = slice_anycubic_next(source, output, executable="missing-anycubic-slicer")
            self.assertEqual(result["status"], "FAIL", result)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_gcode_tracks_extrusion_per_tool_and_units(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "multi.gcode"
            path.write_text(
                "G20\nM82\nG1 X1 E1 F60\nT1\nG92 E0\nG1 X2 E0.5 F60\nT0\nG1 X3 E1.5 F60\n",
                encoding="utf-8",
            )
            result = analyze(path, {"allowed_tools": [0, 1], "bed_mm": [100, 100, 100]})
            self.assertEqual(result["status"], "PASS", result)
            self.assertAlmostEqual(result["metrics"]["positive_extrusion_mm_by_tool"]["0"], 38.1)
            self.assertAlmostEqual(result["metrics"]["positive_extrusion_mm_by_tool"]["1"], 12.7)

    def test_gcode_arc_blocks_strict_motion_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "arc.gcode"
            path.write_text("G21\nG90\nG2 X10 Y10 I5 J0 F1200\n", encoding="utf-8")
            result = analyze(path, {"bed_mm": [100, 100, 100]})
            self.assertEqual(result["status"], "NOT_RUN")
            self.assertEqual(result["metrics"]["arc_moves"], 1)

    def test_minimal_3mf_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.3mf"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
                archive.writestr("_rels/.rels", RELATIONSHIPS_XML)
                archive.writestr("3D/3dmodel.model", MODEL_XML)
            result = validate_3mf(path, {"inspect_meshes": False})
            self.assertEqual(result["status"], "PASS", result)

    def test_3mf_requires_standard_root_relationship(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.3mf"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
                archive.writestr("_rels/.rels", f"<Relationships xmlns=\"{REL_NS}\"/>")
                archive.writestr("3D/3dmodel.model", MODEL_XML)
            result = validate_3mf(path, {"inspect_meshes": False})
            self.assertEqual(result["status"], "FAIL")

    def test_project_release_blocks_unresolved_physical_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evidence = root / "source.txt"
            evidence.write_text("source", encoding="utf-8")
            project = {
                "schema_version": "1.0",
                "project": {"id": "test", "revision": "R1", "units": "mm", "risk_class": "normal-functional"},
                "artifacts": [{"id": "source", "path": "source.txt", "kind": "source", "revision": "R1"}],
                "checks": [{"id": "fit", "type": "physical", "required": True, "status": "REVIEW_REQUIRED", "criterion": "Fit coupon"}],
                "release": {"required_approvals": [], "approvals": {}},
            }
            project_path = root / "project.json"
            project_path.write_text(json.dumps(project), encoding="utf-8")
            release = validate_project(project_path, "release")
            draft = validate_project(project_path, "draft")
            self.assertEqual(release["status"], "REVIEW_REQUIRED")
            self.assertEqual(draft["status"], "REVIEW_REQUIRED")
            self.assertEqual(exit_code(draft["status"], "draft"), 0)

    def test_skill_validation_uses_ast_without_cache_writes(self) -> None:
        cache_directories_before = {path.resolve() for path in ROOT.rglob("__pycache__")}
        result = validate_skill(ROOT, runtime="opencode", profile="draft")
        self.assertNotEqual(result["status"], "FAIL", result)
        cache_directories_after = {path.resolve() for path in ROOT.rglob("__pycache__")}
        self.assertEqual(cache_directories_after, cache_directories_before)


if __name__ == "__main__":
    unittest.main()
