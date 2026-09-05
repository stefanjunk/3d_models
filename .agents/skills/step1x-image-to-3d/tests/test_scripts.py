#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(script: str, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        text=True,
        capture_output=True,
        check=False,
    )


def load_script(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load test module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compatible_api() -> dict[str, object]:
    parameters = []
    for name in (
        "input_image_path",
        "guidance_scale",
        "inference_steps",
        "max_facenum",
        "symmetry",
        "edge_type",
    ):
        schema: dict[str, object] = {"type": "string"}
        if name == "symmetry":
            schema["enum"] = ["x", "asymmetry"]
        elif name == "edge_type":
            schema["enum"] = ["sharp", "normal", "smooth"]
        parameters.append(
            {
                "parameter_name": name,
                "parameter_default": None,
                "parameter_has_default": False,
                "type": schema,
            }
        )
    return {
        "named_endpoints": {
            "/generate_func": {
                "parameters": parameters,
                "returns": [{"type": {"type": "string"}}],
            }
        }
    }


@contextmanager
def api_server(payload: bytes, http_status: int = 200):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path != "/gradio_api/info":
                self.send_error(404)
                return
            self.send_response(http_status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


class ScriptTests(unittest.TestCase):
    def test_probe_validates_named_api_contract(self) -> None:
        payload = json.dumps(compatible_api()).encode("utf-8")
        with api_server(payload) as url:
            result = run(
                "step1x_client.py",
                "probe",
                "--url",
                url,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "compatible")
        self.assertEqual(report["return_count"], 1)
        self.assertEqual(len(report["api_schema_sha256"]), 64)

    def test_probe_rejects_removed_two_output_contract(self) -> None:
        api = compatible_api()
        api["named_endpoints"]["/generate_func"]["returns"] *= 2
        payload = json.dumps(api).encode("utf-8")
        with api_server(payload) as url:
            result = run("step1x_client.py", "probe", "--url", url)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("exactly one geometry GLB", result.stderr)

    def test_status_confirms_loaded_only_for_compatible_live_api(self) -> None:
        payload = json.dumps(compatible_api()).encode("utf-8")
        with api_server(payload) as url:
            result = run(
                "step1x_client.py",
                "status",
                "--url",
                url,
                "--skip-docker",
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "ready")
        self.assertEqual(report["model_state"], "loaded_and_ready")
        self.assertTrue(report["model_loaded"])
        self.assertTrue(report["safe_to_submit_generation"])

    def test_status_does_not_claim_loaded_for_unavailable_api(self) -> None:
        with api_server(b"{}", http_status=503) as url:
            result = run(
                "step1x_client.py",
                "status",
                "--url",
                url,
                "--skip-docker",
            )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "not_ready")
        self.assertEqual(report["model_state"], "model_load_not_confirmed")
        self.assertIsNone(report["model_loaded"])
        self.assertFalse(report["safe_to_submit_generation"])

    def test_generate_rejects_unpinned_client_before_creating_run(self) -> None:
        client = load_script("step1x_client.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "input.png"
            source.write_bytes(b"not decoded before version check")
            output = root / "run-001"
            args = SimpleNamespace(
                input=source,
                guidance=7.5,
                max_faces=400000,
                steps=50,
                output_dir=output,
            )
            with mock.patch.object(client, "package_version", return_value="1.3.0"):
                result = client.command_generate(args)

            self.assertEqual(result, 2)
            self.assertFalse(output.exists())

    def test_status_classifies_stopped_and_loading_containers(self) -> None:
        client = load_script("step1x_client.py")
        unavailable_api = {"reachable": False, "contract_status": "not_observed"}
        stopped = client.classify_readiness(
            unavailable_api,
            {"observation": "observed", "running": False},
        )
        loading = client.classify_readiness(
            unavailable_api,
            {
                "observation": "observed",
                "running": True,
                "startup_markers": {
                    "model_loading_seen": True,
                    "server_listening_seen": False,
                },
            },
        )
        self.assertEqual(stopped[1], "not_loaded_container_stopped")
        self.assertFalse(stopped[2])
        self.assertFalse(stopped[3])
        self.assertEqual(loading[1], "loading_or_initializing")
        self.assertFalse(loading[2])
        self.assertFalse(loading[3])

    def test_glb_conversion_requires_and_records_explicit_registration(self) -> None:
        try:
            import trimesh
        except ImportError:
            self.skipTest("trimesh is not installed")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "box.glb"
            output = root / "box.stl"
            report_path = root / "conversion.json"
            trimesh.Scene(trimesh.creation.box(extents=[1.0, 2.0, 3.0])).export(source)

            result = run(
                "glb_to_print_mesh.py",
                "convert",
                source,
                "--output",
                output,
                "--target-longest-mm",
                120,
                "--y-up-to-z-up",
                "--place-on-bed",
                "--report",
                report_path,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            extents = report["output"]["mesh"]["extents"]
            bounds = report["output"]["mesh"]["bounds"]
            self.assertAlmostEqual(max(extents), 120.0, places=6)
            self.assertAlmostEqual(bounds[0][2], 0.0, places=6)
            self.assertEqual(
                report["output"]["unit_convention"],
                "millimeter (STL itself has no unit metadata)",
            )
            self.assertTrue(report["output"]["mesh"]["watertight"])

    def test_glb_conversion_fails_closed_for_open_mesh(self) -> None:
        try:
            import trimesh
        except ImportError:
            self.skipTest("trimesh is not installed")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "open.glb"
            output = root / "open.stl"
            mesh = trimesh.Trimesh(
                vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
                faces=[[0, 1, 2]],
                process=False,
            )
            trimesh.Scene(mesh).export(source)
            result = run(
                "glb_to_print_mesh.py",
                "convert",
                source,
                "--output",
                output,
                "--target-longest-mm",
                50,
                "--keep-orientation",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("not watertight", result.stderr)
            self.assertFalse(output.exists())

    def test_runtime_capture_preserves_porcelain_status_columns(self) -> None:
        capture = load_script("capture_step1x_runtime.py")
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            for command in (
                ["git", "init", "-q"],
                ["git", "config", "user.name", "Skill Test"],
                ["git", "config", "user.email", "skill-test@example.invalid"],
            ):
                result = subprocess.run(
                    command, cwd=repo, text=True, capture_output=True, check=False
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            (repo / "tracked.txt").write_text("before\n", encoding="utf-8")
            subprocess.run(["git", "add", "tracked.txt"], cwd=repo, check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "fixture"], cwd=repo, check=True
            )
            subprocess.run(
                ["git", "remote", "add", "origin", "https://example.invalid/repo.git"],
                cwd=repo,
                check=True,
            )
            (repo / "tracked.txt").write_text("after\n", encoding="utf-8")

            record = capture.capture_source(repo, None, False)
            self.assertIn(" M tracked.txt", record["status_porcelain"])
            self.assertIn("tracked.txt", record["runtime_file_hashes"])


if __name__ == "__main__":
    unittest.main()
