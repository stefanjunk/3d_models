from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import unittest

import yaml

JSONSCHEMA_AVAILABLE = importlib.util.find_spec("jsonschema") is not None
if JSONSCHEMA_AVAILABLE:
    import jsonschema

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(JSONSCHEMA_AVAILABLE, "jsonschema not installed")
class SchemaTests(unittest.TestCase):
    def test_template_validates(self):
        schema = json.loads((ROOT / "assets/schemas/multicolor-job.schema.json").read_text(encoding="utf-8"))
        job = yaml.safe_load((ROOT / "assets/templates/multicolor-job.yaml").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(job)


if __name__ == "__main__":
    unittest.main()
