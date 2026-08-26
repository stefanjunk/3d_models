from __future__ import annotations

import json
from pathlib import Path
import unittest

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def test_template_validates(self):
        schema = json.loads((ROOT / "assets/schemas/multicolor-job.schema.json").read_text(encoding="utf-8"))
        job = yaml.safe_load((ROOT / "assets/templates/multicolor-job.yaml").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(job)


if __name__ == "__main__":
    unittest.main()
