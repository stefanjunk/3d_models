#!/usr/bin/env python3
"""Validate, audit, rank, and gate the Git-backed 3D learning store.

This tool is intentionally non-mutating. Promotion remains a reviewed edit.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import jsonschema
import yaml


SCHEMA_BY_KIND = {
    "lesson": "lesson.schema.json",
    "eval": "eval.schema.json",
    "trace": "trace.schema.json",
    "pattern": "pattern.schema.json",
    "benchmark-measurement": "benchmark-measurement.schema.json",
}
MATURITY_VALUE = {"E0": 0, "E1": 1, "E2": 2, "E3": 3, "E4": 4}
CONFIDENCE_VALUE = {"low": 0, "medium": 5, "high": 10}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+._-]*", re.IGNORECASE)


def find_repo_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        root = explicit.resolve()
        if (root / "schemas").is_dir():
            return root.parent.parent
        if (root / "libraries" / "3d-learning" / "schemas").is_dir():
            return root
        raise ValueError(f"not a repository or learning root: {explicit}")
    starts = [Path.cwd().resolve(), Path(__file__).resolve()]
    for start in starts:
        for candidate in (start, *start.parents):
            if (candidate / "libraries" / "3d-learning" / "schemas").is_dir():
                return candidate
    raise ValueError("could not locate libraries/3d-learning; pass --root")


def library_root(repo_root: Path) -> Path:
    return repo_root / "libraries" / "3d-learning"


def normalize_scalars(value: Any) -> Any:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: normalize_scalars(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_scalars(item) for item in value]
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError("top-level YAML value must be an object")
    return normalize_scalars(value)


def load_schema(repo_root: Path, kind: str) -> dict[str, Any]:
    name = SCHEMA_BY_KIND.get(kind)
    if name is None:
        raise ValueError(f"unknown record kind: {kind!r}")
    with (library_root(repo_root) / "schemas" / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def discover_records(repo_root: Path) -> list[Path]:
    root = library_root(repo_root)
    globs = (
        "experience/raw/*.yaml",
        "experience/candidates/*.yaml",
        "experience/validated/*.yaml",
        "experience/rejected/*.yaml",
        "evals/**/*.yaml",
        "patterns/**/*.yaml",
        "benchmarks/measurements/*.yaml",
    )
    return sorted({path for pattern in globs for path in root.glob(pattern) if path.is_file()})


def rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def expected_lifecycle(path: Path) -> str | None:
    parts = path.parts
    for folder, state in {
        "candidates": "candidate",
        "validated": "validated",
        "rejected": "rejected",
    }.items():
        if "experience" in parts and folder in parts:
            return state
    return None


def maturity_errors(record: dict[str, Any], target: str | None = None) -> list[str]:
    lifecycle = record.get("lifecycle", {})
    maturity = target or lifecycle.get("maturity")
    evidence = record.get("evidence", {})
    relationships = record.get("relationships", {})
    explanation = record.get("explanation", {})
    validation = record.get("validation", {})
    review = lifecycle.get("review", {})
    errors: list[str] = []

    if maturity not in MATURITY_VALUE:
        return [f"unknown maturity: {maturity!r}"]
    level = MATURITY_VALUE[maturity]
    if evidence.get("observations", 0) < 1:
        errors.append("E0 requires at least one observation")
    if level >= 1:
        if evidence.get("observations", 0) < 2:
            errors.append("E1 requires at least two observations")
        if evidence.get("same_scope_repetitions", 0) < 2:
            errors.append("E1 requires at least two same-scope repetitions")
    if level >= 2 and evidence.get("geometry_count", 0) < 2:
        errors.append("E2 requires at least two geometry instances")
    if level >= 3:
        varied = sum(
            int(evidence.get(key, 0) > 1)
            for key in ("machine_count", "material_count", "nozzle_count")
        )
        if varied < 2:
            errors.append("E3 requires variation in at least two of machine/material/nozzle")
    if level >= 4:
        if not evidence.get("measured"):
            errors.append("E4 requires measured evidence")
        if not explanation.get("validated"):
            errors.append("E4 requires a validated explanation")
        if not relationships.get("evals"):
            errors.append("E4 requires at least one linked eval")
        if validation.get("targeted") != "pass":
            errors.append("E4 requires targeted validation pass")
        if validation.get("regression") != "pass":
            errors.append("E4 requires regression pass")
        if review.get("status") != "approved":
            errors.append("E4 requires approved human review")
    return errors


def supplemental_errors(record: dict[str, Any], path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    kind = record.get("kind")
    if kind == "lesson":
        lifecycle = record.get("lifecycle", {})
        expected = expected_lifecycle(path)
        if expected and lifecycle.get("state") != expected:
            errors.append(
                f"path requires lifecycle.state={expected!r}, got {lifecycle.get('state')!r}"
            )
        if lifecycle.get("state") == "validated":
            if lifecycle.get("review", {}).get("status") != "approved":
                errors.append("validated lesson requires approved human review")
            if record.get("relationships", {}).get("conflicts"):
                errors.append("validated lesson has unresolved conflicts")
        if lifecycle.get("state") == "rejected" and not lifecycle.get("rejection_reason"):
            errors.append("rejected lesson requires lifecycle.rejection_reason")
        if record.get("source_type") == "user-correction" and not record.get("relationships", {}).get("evals"):
            errors.append("user correction requires at least one linked eval")
        errors.extend(maturity_errors(record))
    elif kind == "pattern" and record.get("status") == "validated":
        if not record.get("evidence"):
            errors.append("validated pattern requires at least one evidence lesson")
        if not record.get("evals"):
            errors.append("validated pattern requires at least one linked eval")
    return errors


def schema_errors(record: dict[str, Any], repo_root: Path) -> list[str]:
    try:
        schema = load_schema(repo_root, str(record.get("kind")))
    except ValueError as exc:
        return [str(exc)]
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    result: list[str] = []
    for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        result.append(f"{location}: {error.message}")
    return result


def validate_one(path: Path, repo_root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        record = load_yaml(path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return None, [f"cannot load YAML: {exc}"]
    errors = schema_errors(record, repo_root)
    if not errors:
        errors.extend(supplemental_errors(record, path, repo_root))
    return record, errors


def validate_paths(paths: Iterable[Path], repo_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in paths:
        record, path_errors = validate_one(path, repo_root)
        if record is not None:
            record["__path__"] = rel(path, repo_root)
            records.append(record)
        errors.extend(f"{rel(path, repo_root)}: {message}" for message in path_errors)
    return records, errors


def record_id(record: dict[str, Any]) -> str:
    return str(record.get("id", "<missing-id>"))


def lesson_signature(record: dict[str, Any]) -> tuple[str, ...]:
    scope = record.get("scope", {})
    machine = scope.get("machine", {})
    material = scope.get("material", {})
    nozzle = scope.get("nozzle", {})
    feature = record.get("feature", {})
    observation = record.get("observation", {})
    return tuple(
        str(value or "").strip().casefold()
        for value in (
            feature.get("type"),
            feature.get("geometry"),
            scope.get("process"),
            machine.get("manufacturer"),
            machine.get("model"),
            material.get("manufacturer"),
            material.get("product"),
            material.get("variant"),
            material.get("color"),
            nozzle.get("diameter_mm"),
            nozzle.get("material"),
            observation.get("parameter"),
        )
    )


def audit_records(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids: dict[str, list[str]] = defaultdict(list)
    for record in records:
        ids[record_id(record)].append(record["__path__"])
    for item_id, paths in sorted(ids.items()):
        if len(paths) > 1:
            errors.append(f"duplicate ID {item_id}: {', '.join(paths)}")

    known_ids = set(ids)
    lesson_signatures: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for record in records:
        if record.get("kind") == "lesson":
            lesson_signatures[lesson_signature(record)].append(record_id(record))
            relationships = record.get("relationships", {})
            for key in ("duplicates", "conflicts", "supersedes", "related", "evals"):
                for target in relationships.get(key, []):
                    if target not in known_ids:
                        errors.append(f"{record_id(record)} links unknown {key} ID {target}")
        elif record.get("kind") == "eval":
            relationships = record.get("relationships", {})
            for target in relationships.get("lessons", []):
                if target not in known_ids:
                    errors.append(f"{record_id(record)} links unknown lesson ID {target}")
            for target in relationships.get("regression_suites", []):
                if target not in known_ids:
                    errors.append(f"{record_id(record)} links unknown regression eval ID {target}")
    for signature, lesson_ids in lesson_signatures.items():
        if len(lesson_ids) > 1:
            errors.append(
                f"possible duplicate lesson scope {signature}: {', '.join(sorted(lesson_ids))}"
            )
    return errors


def fold_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(fold_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(fold_text(item) for item in value)
    return str(value or "")


def contains(haystack: str, needle: str) -> bool:
    folded_haystack = haystack.casefold()
    folded_needle = needle.casefold()
    if folded_needle in folded_haystack:
        return True
    requested_tokens = set(TOKEN_RE.findall(folded_needle))
    available_tokens = set(TOKEN_RE.findall(folded_haystack))
    return bool(requested_tokens) and requested_tokens <= available_tokens


def scope_values(record: dict[str, Any]) -> dict[str, str]:
    scope = record.get("scope", {})
    machine = scope.get("machine", {})
    material = scope.get("material", {})
    nozzle = scope.get("nozzle", {})
    return {
        "process": str(scope.get("process", "")),
        "machine": " ".join(str(machine.get(key, "") or "") for key in ("manufacturer", "model", "unit_id")),
        "material": " ".join(str(material.get(key, "") or "") for key in ("manufacturer", "product", "variant", "color", "batch")),
        "nozzle": str(nozzle.get("diameter_mm", "") or ""),
        "feature": str(record.get("feature", {}).get("type", "")),
        "tags": " ".join(record.get("tags", [])),
    }


def filter_record(record: dict[str, Any], args: argparse.Namespace) -> tuple[bool, int]:
    values = scope_values(record)
    score = 0
    for name, weight in (("process", 100), ("machine", 100), ("material", 100), ("feature", 80), ("tag", 60)):
        requested = getattr(args, name, None)
        if requested is None:
            continue
        key = "tags" if name == "tag" else name
        if not values[key] or not contains(values[key], str(requested)):
            return False, 0
        score += weight
    if args.nozzle is not None:
        try:
            actual = float(values["nozzle"])
        except ValueError:
            return False, 0
        if abs(actual - args.nozzle) > 1e-9:
            return False, 0
        score += 100
    return True, score


def rank_record(record: dict[str, Any], base_score: int, query: str | None) -> float:
    lifecycle = record.get("lifecycle", {})
    score = float(base_score)
    score += MATURITY_VALUE.get(lifecycle.get("maturity"), 0) * 10
    score += CONFIDENCE_VALUE.get(lifecycle.get("confidence"), 0)
    if query:
        query_tokens = set(TOKEN_RE.findall(query.casefold()))
        record_tokens = set(TOKEN_RE.findall(fold_text(record).casefold()))
        if query_tokens:
            score += 20 * len(query_tokens & record_tokens) / len(query_tokens)
    try:
        captured = dt.date.fromisoformat(str(record.get("captured_at")))
        age_days = max(0, (dt.date.today() - captured).days)
        score += max(0.0, 5.0 - min(age_days, 3650) / 730.0)
    except ValueError:
        pass
    return round(score, 3)


def resolve_input_paths(raw_paths: list[str], repo_root: Path) -> list[Path]:
    if not raw_paths:
        return discover_records(repo_root)
    result: list[Path] = []
    for raw in raw_paths:
        path = Path(raw)
        if not path.is_absolute():
            path = repo_root / path
        if path.is_dir():
            result.extend(sorted(path.rglob("*.yaml")))
        else:
            result.append(path)
    return result


def command_validate(args: argparse.Namespace, repo_root: Path) -> int:
    paths = resolve_input_paths(args.paths, repo_root)
    records, errors = validate_paths(paths, repo_root)
    output = {
        "status": "fail" if errors else "pass",
        "records": len(records),
        "paths": len(paths),
        "errors": errors,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 1 if errors else 0


def command_audit(args: argparse.Namespace, repo_root: Path) -> int:
    paths = discover_records(repo_root)
    records, errors = validate_paths(paths, repo_root)
    errors.extend(audit_records(records))
    output = {
        "status": "fail" if errors else "pass",
        "records": len(records),
        "errors": errors,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 1 if errors else 0


def command_retrieve(args: argparse.Namespace, repo_root: Path) -> int:
    paths = list((library_root(repo_root) / "experience" / "validated").glob("*.yaml"))
    if args.include_candidates:
        paths.extend((library_root(repo_root) / "experience" / "candidates").glob("*.yaml"))
    records, errors = validate_paths(sorted(paths), repo_root)
    if errors:
        print(json.dumps({"status": "fail", "errors": errors}, indent=2, ensure_ascii=False))
        return 1
    ranked: list[dict[str, Any]] = []
    for record in records:
        matches, base = filter_record(record, args)
        if not matches:
            continue
        lifecycle = record["lifecycle"]
        ranked.append(
            {
                "id": record["id"],
                "path": record["__path__"],
                "title": record["title"],
                "state": lifecycle["state"],
                "maturity": lifecycle["maturity"],
                "confidence": lifecycle["confidence"],
                "score": rank_record(record, base, args.query),
                "scope": scope_values(record),
                "warning": "UNVALIDATED CANDIDATE" if lifecycle["state"] == "candidate" else None,
            }
        )
    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    print(
        json.dumps(
            {"status": "pass", "count": min(len(ranked), args.limit), "results": ranked[: args.limit]},
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def command_next_id(args: argparse.Namespace, repo_root: Path) -> int:
    maximum = 0
    for path in discover_records(repo_root):
        try:
            match = re.fullmatch(r"EXP-([0-9]{5})", str(load_yaml(path).get("id", "")))
        except (OSError, ValueError, yaml.YAMLError):
            continue
        if match:
            maximum = max(maximum, int(match.group(1)))
    print(f"EXP-{maximum + 1:05d}")
    return 0


def command_promotion_check(args: argparse.Namespace, repo_root: Path) -> int:
    path = Path(args.path)
    if not path.is_absolute():
        path = repo_root / path
    record, errors = validate_one(path, repo_root)
    if record is not None and record.get("kind") != "lesson":
        errors.append("promotion-check accepts lesson records only")
    if record is not None:
        proposed = copy.deepcopy(record)
        proposed["lifecycle"]["maturity"] = args.target
        proposed["lifecycle"]["state"] = "validated"
        errors.extend(maturity_errors(proposed, args.target))
        if proposed["lifecycle"].get("review", {}).get("status") != "approved":
            errors.append("promotion requires approved human review")
        if proposed.get("relationships", {}).get("conflicts"):
            errors.append("promotion blocked by unresolved conflicts")
    output = {
        "status": "blocked" if errors else "ready-for-reviewed-move",
        "path": rel(path, repo_root),
        "target": args.target,
        "mutated": False,
        "errors": sorted(set(errors)),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 1 if errors else 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "--root",
        type=Path,
        help="Repository root or libraries/3d-learning directory (auto-detected by default).",
    )
    sub = result.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate schemas and maturity/lifecycle invariants.")
    validate.add_argument("paths", nargs="*", help="Optional YAML paths or directories.")
    validate.set_defaults(func=command_validate)

    audit = sub.add_parser("audit", help="Validate and audit IDs, links, duplicates, and conflicts.")
    audit.set_defaults(func=command_audit)

    retrieve = sub.add_parser("retrieve", help="Scope-filter and rank lesson context.")
    retrieve.add_argument("--process")
    retrieve.add_argument("--machine")
    retrieve.add_argument("--material")
    retrieve.add_argument("--nozzle", type=float)
    retrieve.add_argument("--feature")
    retrieve.add_argument("--tag")
    retrieve.add_argument("--query")
    retrieve.add_argument("--limit", type=int, default=5)
    retrieve.add_argument("--include-candidates", action="store_true")
    retrieve.set_defaults(func=command_retrieve)

    next_id = sub.add_parser("next-id", help="Print the next unused EXP identifier.")
    next_id.set_defaults(func=command_next_id)

    promotion = sub.add_parser("promotion-check", help="Check a target maturity without mutating files.")
    promotion.add_argument("path")
    promotion.add_argument("--target", choices=sorted(MATURITY_VALUE), required=True)
    promotion.set_defaults(func=command_promotion_check)
    return result


def main() -> int:
    args = parser().parse_args()
    if getattr(args, "limit", 1) < 1:
        print("--limit must be at least 1", file=sys.stderr)
        return 2
    try:
        repo_root = find_repo_root(args.root)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return int(args.func(args, repo_root))


if __name__ == "__main__":
    raise SystemExit(main())
