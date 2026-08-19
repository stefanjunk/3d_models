from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _relief_utils import physical_fit, rasterize_physical_fit, save_square_pixel_preview


class AspectPipelineTests(unittest.TestCase):
    def make_circle(self, size=400):
        im = Image.new("L", (size, size), 0)
        d = ImageDraw.Draw(im)
        m = size // 8
        d.ellipse((m, m, size - 1 - m, size - 1 - m), fill=255)
        return np.asarray(im, dtype=np.float32) / 255.0

    def bbox(self, arr, threshold=0.5):
        ys, xs = np.where(arr > threshold)
        self.assertGreater(len(xs), 0)
        return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1

    def test_contain_preserves_physical_circle_with_anisotropic_pitch(self):
        arr = self.make_circle()
        out, info = rasterize_physical_fit(
            arr,
            source_size_mm=(40.0, 40.0),
            target_size_mm=(80.0, 40.0),
            pitch_mm=(0.20, 0.10),
            fit="contain",
            aspect_policy="preserve",
        )
        x0, y0, x1, y1 = self.bbox(out)
        physical_w = (x1 - x0) * 0.20
        physical_h = (y1 - y0) * 0.10
        self.assertLess(abs(physical_w / physical_h - 1.0), 0.01)
        self.assertLess(info["rasterization_aspect_error_pct"], 0.3)
        # Raw raster is intentionally not the same aspect as physical placement.
        self.assertGreater(abs((x1 - x0) / (y1 - y0) - 1.0), 0.25)

    def test_square_pixel_preview_restores_visual_shape(self):
        arr = self.make_circle()
        out, _ = rasterize_physical_fit(
            arr,
            source_size_mm=(40.0, 40.0),
            target_size_mm=(80.0, 40.0),
            pitch_mm=(0.20, 0.10),
            fit="contain",
        )
        with tempfile.TemporaryDirectory() as td:
            preview_path = Path(td) / "preview.png"
            save_square_pixel_preview(out, preview_path, (80.0, 40.0), 127.0)
            preview = np.asarray(Image.open(preview_path).convert("L"), dtype=np.float32) / 255.0
            x0, y0, x1, y1 = self.bbox(preview)
            self.assertLess(abs((x1 - x0) / (y1 - y0) - 1.0), 0.02)
            self.assertAlmostEqual(preview.shape[1] / preview.shape[0], 2.0, delta=0.02)

    def test_stretch_is_rejected_without_explicit_opt_in(self):
        with self.assertRaises(ValueError):
            physical_fit((40.0, 40.0), (80.0, 40.0), "stretch", "preserve", False)

    def test_stretch_can_be_explicit_and_reports_distortion(self):
        info = physical_fit((40.0, 40.0), (80.0, 40.0), "stretch", "allow-distortion", True)
        self.assertAlmostEqual(info.placed_aspect, 2.0)
        self.assertAlmostEqual(info.physical_aspect_error_pct, 100.0)

    def test_cover_preserves_physical_source_aspect_before_crop(self):
        info = physical_fit((60.0, 40.0), (50.0, 50.0), "cover")
        self.assertAlmostEqual(info.placed_width_mm / info.placed_height_mm, 1.5, places=10)
        self.assertAlmostEqual(info.physical_aspect_error_pct, 0.0, places=10)
        self.assertLess(info.placed_x_mm, 0.0)

    def test_cli_prepare_writes_aspect_validation_and_16bit(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "src.png"
            Image.fromarray((self.make_circle(240) * 65535).astype(np.uint16)).save(src)
            out = td / "height.png"
            preview = td / "preview.png"
            cmd = [
                sys.executable, str(SCRIPTS / "prepare_heightmap.py"), str(src), str(out),
                "--size-mm", "80x40", "--source-size-mm", "40x40",
                "--pitch-mm", "0.2x0.1", "--fit", "contain",
                "--image-class", "person", "--preview", str(preview),
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            with Image.open(out) as im:
                self.assertTrue(im.mode.startswith("I;16") or im.mode == "I")
            meta = json.loads((td / "height.png.json").read_text())
            self.assertTrue(meta["aspect_validation"]["passed"])
            self.assertLess(meta["aspect_validation"]["error_pct"], 0.3)
            self.assertAlmostEqual(meta["target"]["physical_aspect"], 2.0)
            self.assertNotAlmostEqual(meta["target"]["raster_aspect"], 2.0, places=1)
            self.assertTrue(preview.exists())

    def test_registration_does_not_stretch_wrong_generator_aspect(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            raw = td / "raw.png"
            Image.fromarray((self.make_circle(256) * 255).astype(np.uint8), mode="L").save(raw)
            spec = td / "spec.json"
            prompt = td / "prompt.txt"
            subprocess.run([
                sys.executable, str(SCRIPTS / "plan_ai_source.py"),
                "--size-mm", "60x40", "--authoring-ppi", "200",
                "--image-class", "person", "--description", "test portrait",
                "--output-json", str(spec), "--output-prompt", str(prompt),
            ], check=True, capture_output=True, text=True)
            master = td / "master.png"
            subprocess.run([
                sys.executable, str(SCRIPTS / "register_source_master.py"),
                str(raw), str(master), "--spec", str(spec), "--source-kind", "ai-generated",
            ], check=True, capture_output=True, text=True)
            manifest = json.loads((td / "master.png.source.json").read_text())
            self.assertEqual(manifest["authoring"]["fit_mode"], "contain")
            self.assertGreater(manifest["raw_source"]["requested_physical_aspect_error_pct"], 10.0)
            # Canonical canvas has requested physical aspect, but subject itself was contained, not stretched.
            self.assertAlmostEqual(manifest["physical"]["aspect"], 1.5)

    def test_repeat_rejects_changed_tile_aspect_without_opt_in(self):
        arr = self.make_circle(120)
        with self.assertRaises(ValueError):
            rasterize_physical_fit(
                arr,
                source_size_mm=(20.0, 20.0),
                target_size_mm=(80.0, 40.0),
                pitch_mm=(0.2, 0.1),
                fit="repeat",
                repeat_tile_size_mm=(30.0, 20.0),
                aspect_policy="preserve",
            )

    def test_cylinder_surface_metric_uses_arc_length(self):
        radius = 30.0
        width = 30.0
        proc = subprocess.run([
            sys.executable, str(SCRIPTS / "surface_patch_metrics.py"), "cylinder",
            "--radius-mm", str(radius), "--width-mm", str(width),
        ], check=True, capture_output=True, text=True)
        data = json.loads(proc.stdout)
        self.assertAlmostEqual(data["angular_span_rad"], 1.0, places=10)
        self.assertAlmostEqual(data["desired_arc_width_mm"], width, places=10)

    def test_sphere_metric_shrinks_longitude_away_from_equator(self):
        proc = subprocess.run([
            sys.executable, str(SCRIPTS / "surface_patch_metrics.py"), "sphere",
            "--radius-mm", "40", "--latitude-deg", "60",
        ], check=True, capture_output=True, text=True)
        data = json.loads(proc.stdout)
        self.assertAlmostEqual(data["longitude_scale_relative_to_equator"], 0.5, places=6)

    def test_relief_mesh_budget_and_tolerance_sweep(self):
        proc = subprocess.run([
            sys.executable, str(SCRIPTS / "relief_mesh_budget.py"),
            "--area-mm2", "72000", "--pitch-mm", "0.30x0.30",
            "--process", "fdm", "--nozzle-mm", "0.60",
            "--depth-mm", "0.32", "--layer-height-mm", "0.30",
            "--memory-budget-gib", "8", "--max-mesh-mib", "100",
            "--max-slicer-seconds", "120",
        ], check=True, capture_output=True, text=True)
        data = json.loads(proc.stdout)
        self.assertEqual(data["uniform_grid_worst_case"]["relief_triangles"], 1_600_000)
        self.assertEqual(data["policy"]["status"], "REVIEW")
        sweep = data["simplification"]["candidate_sweep_mm"]
        self.assertAlmostEqual(sweep[1], 0.0400, places=6)
        self.assertEqual(len(sweep), 3)
        self.assertEqual(data["resource_budget"]["release_status"], "PENDING")
        self.assertEqual(data["resource_budget"]["memory_planning_status"], "PASS")

    def test_relief_mesh_budget_stop_can_fail_closed(self):
        proc = subprocess.run([
            sys.executable, str(SCRIPTS / "relief_mesh_budget.py"),
            "--area-mm2", "300000", "--pitch-mm", "0.30",
            "--process", "fdm", "--nozzle-mm", "0.60",
            "--depth-mm", "0.32", "--layer-height-mm", "0.30",
            "--memory-budget-gib", "8", "--max-mesh-mib", "500",
            "--max-slicer-seconds", "120",
            "--fail-on-stop",
        ], check=False, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stdout)["policy"]["status"], "STOP")

    def test_relief_mesh_budget_can_stop_on_memory_before_geometry(self):
        proc = subprocess.run([
            sys.executable, str(SCRIPTS / "relief_mesh_budget.py"),
            "--area-mm2", "72000", "--pitch-mm", "0.30",
            "--process", "fdm", "--nozzle-mm", "0.60",
            "--depth-mm", "0.32", "--layer-height-mm", "0.30",
            "--memory-budget-gib", "0.5", "--max-mesh-mib", "500",
            "--max-slicer-seconds", "120", "--fail-on-stop",
        ], check=False, capture_output=True, text=True)
        data = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(data["resource_budget"]["memory_planning_status"], "STOP")

    def test_relief_mesh_budget_requires_measured_release_evidence(self):
        base = [
            sys.executable, str(SCRIPTS / "relief_mesh_budget.py"),
            "--area-mm2", "1000", "--pitch-mm", "0.30",
            "--process", "fdm", "--nozzle-mm", "0.60",
            "--depth-mm", "0.32", "--layer-height-mm", "0.30",
            "--memory-budget-gib", "8", "--max-mesh-mib", "100",
            "--max-slicer-seconds", "120", "--require-measured-release",
        ]
        pending = subprocess.run(base, check=False, capture_output=True, text=True)
        self.assertEqual(pending.returncode, 3)
        self.assertEqual(json.loads(pending.stdout)["resource_budget"]["release_status"], "PENDING")

        measured = subprocess.run(base + [
            "--actual-triangles", "25000",
            "--actual-peak-memory-gib", "0.25",
            "--actual-file-bytes", "1250084",
            "--actual-slicer-seconds", "24",
        ], check=False, capture_output=True, text=True)
        self.assertEqual(measured.returncode, 0)
        self.assertEqual(json.loads(measured.stdout)["resource_budget"]["release_status"], "PASS")

    def test_relief_mesh_acceptance_uses_organizer_starting_limits(self):
        example = ROOT / "examples" / "desk-organizer-relief-acceptance.json"
        proc = subprocess.run([
            sys.executable, str(SCRIPTS / "relief_mesh_acceptance.py"), str(example),
        ], check=True, capture_output=True, text=True)
        data = json.loads(proc.stdout)
        self.assertTrue(data["passed"])
        self.assertAlmostEqual(data["metrics"]["rms_limit_mm"], 0.03)

        payload = json.loads(example.read_text(encoding="utf-8"))
        payload["comparison"]["relief_correlation"] = 0.97
        with tempfile.TemporaryDirectory() as td:
            failed_input = Path(td) / "failed.json"
            failed_input.write_text(json.dumps(payload), encoding="utf-8")
            failed = subprocess.run([
                sys.executable, str(SCRIPTS / "relief_mesh_acceptance.py"),
                str(failed_input), "--fail-on-reject",
            ], check=False, capture_output=True, text=True)
        self.assertEqual(failed.returncode, 2)
        self.assertFalse(json.loads(failed.stdout)["passed"])

        payload["comparison"]["relief_correlation"] = 0.99
        payload["comparison"]["relief_contrast_loss_pct"] = 5.0
        with tempfile.TemporaryDirectory() as td:
            boundary_input = Path(td) / "boundary.json"
            boundary_input.write_text(json.dumps(payload), encoding="utf-8")
            boundary = subprocess.run([
                sys.executable, str(SCRIPTS / "relief_mesh_acceptance.py"),
                str(boundary_input), "--fail-on-reject",
            ], check=False, capture_output=True, text=True)
        boundary_report = json.loads(boundary.stdout)
        self.assertEqual(boundary.returncode, 2)
        self.assertFalse(boundary_report["checks"]["relief_contrast_loss_pct"]["passed"])

    def test_initialized_job_persists_budgets_and_mesh_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            job_dir = Path(td) / "job"
            subprocess.run([
                sys.executable, str(SCRIPTS / "init_relief_job.py"), str(job_dir),
                "--name", "test-job", "--target-size-mm", "80x40",
                "--source-size-mm", "80x40", "--description", "test relief",
                "--process", "fdm", "--nozzle-mm", "0.6", "--layer-height-mm", "0.3",
                "--depth-mm", "0.32", "--triangle-target", "1000000",
                "--triangle-stop", "5000000", "--memory-budget-gib", "8",
                "--max-mesh-mib", "100", "--max-slicer-seconds", "120",
            ], check=True, capture_output=True, text=True)
            job = json.loads((job_dir / "relief-job.json").read_text(encoding="utf-8"))
        self.assertEqual(job["schema"], "heightmap-relief-job-v2.4")
        self.assertEqual(job["complexity_budget"]["memory_budget_gib"], 8.0)
        self.assertNotEqual(job["geometry"]["reference_mesh_path"], job["geometry"]["manufacturing_mesh_path"])


if __name__ == "__main__":
    unittest.main()
