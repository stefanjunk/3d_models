from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

from .common import (
    ValidationInputError,
    check,
    load_data,
    report,
    resolve_path,
    sha256_file,
)
from .threemf import NS
from .threemf import validate as validate_3mf

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
PLACEHOLDER_TOKENS = {"replace-me", "todo", "lorem ipsum", "tbd"}


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationInputError(f"{label} must be an object")
    return value


def _resolve_artifact(
    entry: dict[str, Any], label: str, product_root: Path, checks: list[dict[str, Any]]
) -> Path | None:
    raw = entry.get("path")
    expected = entry.get("sha256")
    if not isinstance(raw, str) or not raw:
        checks.append(
            check(f"{label}-path", "FAIL", f"{label}.path must be a non-empty string")
        )
        return None
    path = resolve_path(product_root, raw)
    try:
        path.relative_to(product_root)
    except ValueError:
        checks.append(
            check(
                f"{label}-containment",
                "FAIL",
                f"{label} is outside the product root: {path}",
            )
        )
        return None
    if not path.is_file():
        checks.append(check(f"{label}-file", "FAIL", f"{label} not found: {path}"))
        return None
    actual = sha256_file(path)
    passed = (
        isinstance(expected, str)
        and re.fullmatch(r"[0-9a-f]{64}", expected)
        and actual == expected
    )
    checks.append(
        check(
            f"{label}-hash",
            "PASS" if passed else "FAIL",
            f"{label} SHA-256 matches the manifest"
            if passed
            else f"{label} SHA-256 mismatch",
            metrics={"path": str(path), "sha256": actual, "expected_sha256": expected},
        )
    )
    return path


def _project_part_count(path: Path) -> tuple[int, bool, str | None]:
    with zipfile.ZipFile(path, "r") as archive:
        names = set(archive.namelist())
        embedded = {
            "Metadata/project_settings.config",
            "Metadata/model_settings.config",
        } <= names
        support_value: str | None = None
        if embedded:
            settings = json.loads(archive.read("Metadata/project_settings.config"))
            support_value = (
                str(settings.get("enable_support"))
                if "enable_support" in settings
                else None
            )
            model_settings = ET.fromstring(
                archive.read("Metadata/model_settings.config")
            )
            object_count = len(model_settings.findall("object"))
            if object_count:
                return object_count, True, support_value
        root = ET.fromstring(archive.read("3D/3dmodel.model"))
        build = root.find("m:build", NS)
        build_count = len(build.findall("m:item", NS)) if build is not None else 0
        return build_count, embedded, support_value


def validate(manifest_path: Path, profile: str = "release") -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    inputs = [manifest_path]
    if not manifest_path.is_file():
        return report(
            "validate-p2-stage",
            [
                check(
                    "p2-manifest-file",
                    "FAIL",
                    f"P2 manifest not found: {manifest_path}",
                )
            ],
            inputs=inputs,
            profile=profile,
        )
    try:
        data = _mapping(load_data(manifest_path), "manifest")
        product = _mapping(data.get("product"), "product")
        artifacts = _mapping(data.get("artifacts"), "artifacts")
    except Exception as exc:
        return report(
            "validate-p2-stage",
            [check("p2-manifest-data", "FAIL", f"{type(exc).__name__}: {exc}")],
            inputs=inputs,
            profile=profile,
        )

    schema_ok = data.get("schema_version") == "1.0"
    checks.append(
        check(
            "p2-schema-version",
            "PASS" if schema_ok else "FAIL",
            "P2 schema version is 1.0"
            if schema_ok
            else "Unsupported P2 schema version",
        )
    )
    stage = product.get("lifecycle_stage")
    stage_ok = isinstance(stage, str) and bool(re.match(r"^P2(?:\s|$)", stage))
    identity_ok = all(
        isinstance(product.get(key), str) and product.get(key)
        for key in ("record_id", "sku", "name", "revision")
    )
    checks.append(
        check(
            "p2-product-identity",
            "PASS" if identity_ok and stage_ok else "FAIL",
            "SKU, revision, record and P2 lifecycle identity are present"
            if identity_ok and stage_ok
            else "Incomplete product identity or lifecycle stage is not P2",
        )
    )

    root_value = product.get("root", "..")
    product_root = (
        resolve_path(manifest_path.parent, root_value)
        if isinstance(root_value, str)
        else manifest_path.parent.parent
    )
    if not product_root.is_dir():
        checks.append(
            check("p2-product-root", "FAIL", f"Product root not found: {product_root}")
        )
        return report("validate-p2-stage", checks, inputs=inputs, profile=profile)

    description = _mapping(artifacts.get("description_en"), "artifacts.description_en")
    concept = _mapping(artifacts.get("concept_image"), "artifacts.concept_image")
    rendered = _mapping(artifacts.get("rendered_image"), "artifacts.rendered_image")
    print_set = _mapping(artifacts.get("print_set_3mf"), "artifacts.print_set_3mf")
    description_path = _resolve_artifact(
        description, "p2-description", product_root, checks
    )
    concept_path = _resolve_artifact(concept, "p2-concept-image", product_root, checks)
    rendered_path = _resolve_artifact(
        rendered, "p2-rendered-image", product_root, checks
    )
    three_mf_path = _resolve_artifact(
        print_set, "p2-print-set-3mf", product_root, checks
    )

    if description_path:
        text = description_path.read_text(encoding="utf-8")
        words = re.findall(r"[A-Za-z][A-Za-z'-]+", text)
        lower = text.lower()
        content_ok = (
            description_path.suffix.lower() == ".md"
            and description.get("language") == "en"
            and len(words) >= 35
            and not any(token in lower for token in PLACEHOLDER_TOKENS)
        )
        checks.append(
            check(
                "p2-description-english",
                "PASS" if content_ok else "FAIL",
                "English product description is non-placeholder Markdown"
                if content_ok
                else "Description must declare English, use Markdown, contain at least 35 words and contain no placeholders",
                metrics={"english_word_tokens": len(words)},
            )
        )

    image_meta_ok = concept.get("scope") == "whole-product" and concept.get(
        "approval_state"
    ) in {"approved", "pending", "retrospective-unapproved"}
    checks.append(
        check(
            "p2-concept-scope",
            "PASS" if image_meta_ok else "FAIL",
            "Concept is classified as a whole-product image with an explicit approval state"
            if image_meta_ok
            else "Concept must be whole-product and declare approved, pending or retrospective-unapproved",
        )
    )
    render_meta_ok = rendered.get("basis") == "current-model"
    checks.append(
        check(
            "p2-render-basis",
            "PASS" if render_meta_ok else "FAIL",
            "Render is tied to the current model"
            if render_meta_ok
            else "Rendered image must declare current-model basis",
        )
    )
    for label, path in (("concept", concept_path), ("render", rendered_path)):
        if path:
            checks.append(
                check(
                    f"p2-{label}-format",
                    "PASS" if path.suffix.lower() in IMAGE_EXTENSIONS else "FAIL",
                    f"{label.title()} uses a supported image format"
                    if path.suffix.lower() in IMAGE_EXTENSIONS
                    else f"Unsupported {label} image format: {path.suffix}",
                )
            )
    if concept_path and rendered_path:
        distinct = concept_path != rendered_path and sha256_file(
            concept_path
        ) != sha256_file(rendered_path)
        checks.append(
            check(
                "p2-concept-render-distinct",
                "PASS" if distinct else "FAIL",
                "Concept and current-model render are distinct assets"
                if distinct
                else "Concept and current-model render must be separate, non-identical assets",
            )
        )

    parts = print_set.get("print_parts")
    declared_count = 0
    parts_ok = isinstance(parts, list) and bool(parts)
    if parts_ok:
        for item in parts:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("name"), str)
                or not item.get("name")
                or not isinstance(item.get("quantity"), int)
                or item.get("quantity", 0) < 1
            ):
                parts_ok = False
                break
            declared_count += item["quantity"]
    completeness_ok = print_set.get("all_print_parts_included") is True and parts_ok
    checks.append(
        check(
            "p2-print-parts-declared",
            "PASS" if completeness_ok else "FAIL",
            "Manifest declares every intended printed part and quantity"
            if completeness_ok
            else "Print-set manifest must enumerate all printed parts and assert completeness",
            metrics={"declared_object_quantity": declared_count},
        )
    )

    orientation = (
        print_set.get("orientation")
        if isinstance(print_set.get("orientation"), dict)
        else {}
    )
    orientation_ok = (
        orientation.get("status") == "considered"
        and orientation.get("encoding")
        in {"3mf-build-transform", "embedded-slicer-project"}
        and isinstance(orientation.get("summary"), str)
        and len(orientation["summary"].strip()) >= 12
    )
    checks.append(
        check(
            "p2-orientation-decision",
            "PASS" if orientation_ok else "FAIL",
            "Print orientation is explicitly considered and encoded"
            if orientation_ok
            else "Orientation must be considered, summarized and encoded in the 3MF",
        )
    )

    supports = (
        print_set.get("supports") if isinstance(print_set.get("supports"), dict) else {}
    )
    support_ok = (
        supports.get("status") == "considered"
        and supports.get("mode") in {"disabled", "enabled", "mixed"}
        and supports.get("encoding")
        in {"embedded-slicer-project", "linked-exact-profile"}
        and isinstance(supports.get("summary"), str)
        and len(supports["summary"].strip()) >= 12
    )
    checks.append(
        check(
            "p2-support-decision",
            "PASS" if support_ok else "FAIL",
            "Support mode is explicitly considered"
            if support_ok
            else "Support mode, encoding and rationale are incomplete",
        )
    )

    three_mf_metrics: dict[str, Any] = {}
    if three_mf_path:
        inputs.append(three_mf_path)
        structure = validate_3mf(three_mf_path, {"require_unit": "millimeter"}, profile)
        structure_ok = structure.get("status") == "PASS"
        checks.append(
            check(
                "p2-3mf-structure",
                "PASS" if structure_ok else "FAIL",
                "3MF package structure is valid in millimetres"
                if structure_ok
                else "3MF structural validation failed",
                metrics={"validator_status": structure.get("status")},
            )
        )
        try:
            actual_count, embedded, embedded_support = _project_part_count(
                three_mf_path
            )
            count_ok = completeness_ok and actual_count == declared_count
            checks.append(
                check(
                    "p2-3mf-object-count",
                    "PASS" if count_ok else "FAIL",
                    f"3MF print objects {actual_count}; declared quantity {declared_count}",
                    metrics={"actual": actual_count, "declared": declared_count},
                )
            )
            encoding = supports.get("encoding")
            if encoding == "embedded-slicer-project":
                expected_support = (
                    "0"
                    if supports.get("mode") == "disabled"
                    else "1"
                    if supports.get("mode") == "enabled"
                    else None
                )
                embedded_ok = (
                    embedded
                    and embedded_support is not None
                    and (
                        expected_support is None or embedded_support == expected_support
                    )
                )
                checks.append(
                    check(
                        "p2-embedded-support-settings",
                        "PASS" if embedded_ok else "FAIL",
                        "Destination-slicer support setting is embedded and matches the manifest"
                        if embedded_ok
                        else "Embedded support setting is missing or differs from the manifest",
                        metrics={
                            "embedded": embedded,
                            "enable_support": embedded_support,
                        },
                    )
                )
            elif encoding == "linked-exact-profile":
                profile_entries = supports.get("profile_artifacts")
                slice_entry = supports.get("slice_report")
                links_ok = (
                    isinstance(profile_entries, list)
                    and len(profile_entries) >= 3
                    and isinstance(slice_entry, dict)
                )
                if links_ok:
                    for index, entry in enumerate(profile_entries):
                        if (
                            not isinstance(entry, dict)
                            or _resolve_artifact(
                                entry,
                                f"p2-support-profile-{index + 1}",
                                product_root,
                                checks,
                            )
                            is None
                        ):
                            links_ok = False
                    slice_path = _resolve_artifact(
                        slice_entry, "p2-support-slice-report", product_root, checks
                    )
                    if slice_path:
                        try:
                            slice_payload = load_data(slice_path)
                            links_ok = (
                                links_ok
                                and isinstance(slice_payload, dict)
                                and slice_payload.get("status") == "PASS"
                            )
                        except Exception:
                            links_ok = False
                checks.append(
                    check(
                        "p2-linked-support-evidence",
                        "PASS" if links_ok else "FAIL",
                        "Complete exact profiles and a PASS target-slicer report are hash-bound"
                        if links_ok
                        else "Linked support evidence requires three exact profiles and a PASS slicer report",
                    )
                )
            three_mf_metrics = {
                "actual_print_objects": actual_count,
                "embedded_slicer_settings": embedded,
                "embedded_enable_support": embedded_support,
            }
        except Exception as exc:
            checks.append(
                check(
                    "p2-3mf-project-data",
                    "FAIL",
                    f"Could not inspect 3MF project data: {type(exc).__name__}: {exc}",
                )
            )

    return report(
        "validate-p2-stage",
        checks,
        inputs=inputs,
        profile=profile,
        metrics={"product": product, "print_set": three_mf_metrics},
        limitations=[
            "P2 is digital evidence only; it does not prove physical fit, finish, strength, safety, rights clearance, or commercial readiness.",
            "A manifest completeness assertion remains subject to product-owner review of the intended included-part list.",
        ],
    )
