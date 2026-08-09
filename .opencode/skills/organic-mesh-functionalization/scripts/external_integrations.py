#!/usr/bin/env python3
"""List optional external integrations without installing or executing them."""
from __future__ import annotations

import argparse

from common import dump_json, load_structured, DATA_ROOT


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["list"], nargs="?", default="list")
    args = p.parse_args()
    data = load_structured(DATA_ROOT / "external-integrations.yaml")
    print(dump_json(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
