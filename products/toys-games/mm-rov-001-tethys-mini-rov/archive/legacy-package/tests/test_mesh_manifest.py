import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MeshManifestTests(unittest.TestCase):
    def test_all_reference_meshes_are_closed(self):
        manifest = json.loads((ROOT / "cad" / "stl" / "mesh_manifest.json").read_text())
        self.assertGreaterEqual(len(manifest["parts"]), 10)
        for name, metrics in manifest["parts"].items():
            with self.subTest(part=name):
                self.assertTrue(metrics["watertight_topology"])
                self.assertEqual(metrics["boundary_edges"], 0)
                self.assertEqual(metrics["nonmanifold_edges"], 0)
                self.assertTrue((ROOT / "cad" / "stl" / f"{name}.stl").is_file())


if __name__ == "__main__":
    unittest.main()
