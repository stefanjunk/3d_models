#!/usr/bin/env python3
"""Generate or verify a SHA-256 manifest for a release directory."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path


LINE_RE = re.compile(r"^([0-9a-fA-F]{64})  (.+)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hash or verify final release files.")
    parser.add_argument("release_directory", type=Path)
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Relative file/directory prefix to exclude; repeat as needed",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path, help="Write SHA256SUMS")
    mode.add_argument("--verify", type=Path, help="Verify an existing SHA256SUMS")
    return parser.parse_args()


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def safe_member(root: Path, relative: str) -> Path | None:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def normalized_excludes(values: list[str]) -> list[tuple[str, ...]]:
    excludes: list[tuple[str, ...]] = []
    for value in values:
        candidate = Path(value)
        if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
            raise ValueError(f"unsafe exclude path: {value}")
        excludes.append(tuple(candidate.parts))
    return excludes


def is_excluded(relative: Path, excludes: list[tuple[str, ...]]) -> bool:
    parts = relative.parts
    return any(parts[: len(prefix)] == prefix for prefix in excludes)


def generate(root: Path, output: Path, exclude_values: list[str]) -> int:
    output = output.expanduser().resolve()
    try:
        excludes = normalized_excludes(exclude_values)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if path.resolve() == output:
            continue
        relative = path.relative_to(root)
        if ".git" in relative.parts or is_excluded(relative, excludes):
            continue
        files.append(path)
    files.sort(key=lambda item: item.relative_to(root).as_posix())
    if not files:
        print("ERROR: release directory contains no regular files", file=sys.stderr)
        return 2

    lines = [
        f"{digest(path)}  {path.relative_to(root).as_posix()}" for path in files
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=output.parent, delete=False
    ) as handle:
        handle.write("\n".join(lines) + "\n")
        temporary = Path(handle.name)
    os.replace(temporary, output)
    print(f"Wrote {len(lines)} hashes to {output}")
    print(f"Manifest SHA-256: {digest(output)}")
    return 0


def verify(root: Path, manifest: Path) -> int:
    manifest = manifest.expanduser().resolve()
    try:
        lines = manifest.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"ERROR: cannot read manifest: {exc}", file=sys.stderr)
        return 2

    failures = 0
    checked = 0
    seen: set[str] = set()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        match = LINE_RE.fullmatch(line)
        if not match:
            print(f"FAIL line {line_number}: invalid manifest syntax")
            failures += 1
            continue
        expected, relative = match.groups()
        if relative in seen:
            print(f"FAIL line {line_number}: duplicate path {relative}")
            failures += 1
            continue
        seen.add(relative)
        path = safe_member(root, relative)
        if path is None:
            print(f"FAIL line {line_number}: path escapes release root: {relative}")
            failures += 1
            continue
        if not path.is_file() or path.is_symlink():
            print(f"FAIL missing or non-regular file: {relative}")
            failures += 1
            continue
        actual = digest(path)
        checked += 1
        if actual.lower() != expected.lower():
            print(f"FAIL hash mismatch: {relative}")
            failures += 1
        else:
            print(f"OK {relative}")

    if checked == 0:
        print("FAIL no files were verified")
        failures += 1
    if failures:
        print(f"Verification BLOCKED: {failures} failure(s)")
        return 2
    print(f"Verification PASS: {checked} file(s)")
    return 0


def main() -> int:
    args = parse_args()
    root = args.release_directory.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: release directory does not exist: {root}", file=sys.stderr)
        return 2
    if args.output:
        return generate(root, args.output, args.exclude)
    return verify(root, args.verify)


if __name__ == "__main__":
    raise SystemExit(main())
