#!/usr/bin/env python3
"""List reviewed optional skills, MCPs, parts libraries, and safe next steps."""
from __future__ import annotations

import argparse
import json

from common import load_data


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["list", "references-json"])
    args = p.parse_args()
    data = load_data("external-integrations.yaml")["integrations"]
    if args.command == "list":
        print(json.dumps(data, indent=2))
    else:
        refs = {}
        for key, item in data.items():
            repo = item.get("repository")
            if repo:
                refs[key] = {"repository": repo, "description": item.get("purpose", "Optional design reference")}
        print(json.dumps({"$schema": "https://opencode.ai/config.json", "references": refs}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
