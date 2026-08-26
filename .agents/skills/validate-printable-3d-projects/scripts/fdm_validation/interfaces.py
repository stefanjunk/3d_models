from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from .common import ValidationInputError, check, finite_number, load_data, report, resolve_path
from .mesh import _load_mesh


def _part_mesh(base: Path, part: dict[str, Any]):
    import numpy as np

    path = resolve_path(base, str(part.get("path", "")))
    _, mesh = _load_mesh(path)
    transform = part.get("transform")
    if transform is not None:
        matrix = np.asarray(transform, dtype=float)
        if matrix.shape == (16,):
            matrix = matrix.reshape((4, 4))
        if matrix.shape != (4, 4) or not np.isfinite(matrix).all():
            raise ValidationInputError(f"part {part.get('id')} transform must be a finite 4x4 matrix")
        mesh.apply_transform(matrix)
    return path, mesh


def _intersection_volume(a, b) -> tuple[float, str]:
    import trimesh

    try:
        result = trimesh.boolean.intersection([a, b], engine="manifold", check_volume=True)
        if result is None:
            return 0.0, "manifold"
        return abs(float(result.volume)), "manifold"
    except Exception as exc:
        raise RuntimeError(f"exact Manifold intersection failed: {exc}") from exc


def _minimum_distance(a, b) -> tuple[float, str]:
    import trimesh

    try:
        manager = trimesh.collision.CollisionManager()
        manager.add_object("a", a)
        manager.add_object("b", b)
        return float(manager.min_distance_internal()), "python-fcl"
    except Exception:
        try:
            import numpy as np
            from scipy.spatial import cKDTree

            tree_a = cKDTree(a.vertices)
            tree_b = cKDTree(b.vertices)
            da, _ = tree_a.query(b.vertices, workers=1)
            db, _ = tree_b.query(a.vertices, workers=1)
            return float(min(np.min(da), np.min(db))), "nearest-vertex-fallback"
        except Exception as exc:
            raise RuntimeError(f"distance backend unavailable: {exc}") from exc


def validate_contract(contract_path: Path, profile: str = "release") -> dict[str, Any]:
    if not contract_path.is_file():
        return report(
            "check-interfaces",
            [check("interface-contract", "FAIL", f"Contract not found: {contract_path}")],
            inputs=[contract_path],
            profile=profile,
        )
    try:
        data = load_data(contract_path)
        if not isinstance(data, dict):
            raise ValidationInputError("interface contract root must be an object")
        parts_data = data.get("parts")
        if not isinstance(parts_data, list) or not parts_data:
            raise ValidationInputError("parts must be a non-empty array")
        interfaces_data = data.get("interfaces", [])
        motions_data = data.get("motions", [])
        if not isinstance(interfaces_data, list) or not all(isinstance(item, dict) for item in interfaces_data):
            raise ValidationInputError("interfaces must be an array of objects")
        if not isinstance(motions_data, list) or not all(isinstance(item, dict) for item in motions_data):
            raise ValidationInputError("motions must be an array of objects")
        part_defs = {}
        for item in parts_data:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise ValidationInputError("every part needs a string id")
            if item["id"] in part_defs:
                raise ValidationInputError(f"duplicate part id {item['id']}")
            part_defs[item["id"]] = item
        base = contract_path.parent
        paths: list[Path] = [contract_path]
        meshes = {}
        for part_id, item in part_defs.items():
            path, mesh = _part_mesh(base, item)
            paths.append(path)
            meshes[part_id] = mesh
    except ImportError as exc:
        return report(
            "check-interfaces",
            [check("interface-capability", "NOT_RUN", str(exc))],
            inputs=[contract_path],
            profile=profile,
            capabilities=["mesh-boolean"],
        )
    except Exception as exc:
        return report(
            "check-interfaces",
            [check("interface-contract", "FAIL", f"{type(exc).__name__}: {exc}")],
            inputs=[contract_path],
            profile=profile,
        )

    checks: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {"interfaces": [], "motions": []}
    for item in interfaces_data:
        interface_id = str(item.get("id", "unnamed-interface"))
        a_id, b_id = item.get("a"), item.get("b")
        required = bool(item.get("required", True))
        if a_id not in meshes or b_id not in meshes or a_id == b_id:
            checks.append(check(interface_id, "FAIL", "Interface endpoints are invalid", required=required))
            continue
        mode = item.get("mode")
        row: dict[str, Any] = {"id": interface_id, "a": a_id, "b": b_id, "mode": mode}
        try:
            if mode == "overlap":
                volume, method = _intersection_volume(meshes[a_id], meshes[b_id])
                minimum = float(item.get("min_overlap_volume_mm3", 0.001))
                maximum = item.get("max_overlap_volume_mm3")
                limits_valid = finite_number(minimum) and minimum >= 0 and (maximum is None or finite_number(maximum) and float(maximum) >= minimum)
                passed = limits_valid and volume + 1e-12 >= minimum and (maximum is None or volume <= float(maximum) + 1e-12)
                row.update({"intersection_volume_mm3": volume, "method": method, "minimum_mm3": minimum, "maximum_mm3": maximum})
                checks.append(
                    check(
                        interface_id,
                        "PASS" if passed else "FAIL",
                        f"Intersection volume {volume:.6g} mm³",
                        required=required,
                        metrics=row,
                    )
                )
            elif mode == "clearance":
                distance, method = _minimum_distance(meshes[a_id], meshes[b_id])
                minimum = float(item.get("min_clearance_mm", 0.0))
                maximum = item.get("max_clearance_mm")
                exact = method == "python-fcl"
                limits_valid = finite_number(minimum) and minimum >= 0 and (maximum is None or finite_number(maximum) and float(maximum) >= minimum)
                passed = limits_valid and distance + 1e-12 >= minimum and (maximum is None or distance <= float(maximum) + 1e-12)
                row.update({"minimum_distance_mm": distance, "method": method, "minimum_mm": minimum, "maximum_mm": maximum})
                status = "PASS" if passed and exact else ("FAIL" if not passed else "REVIEW_REQUIRED")
                checks.append(
                    check(
                        interface_id,
                        status,
                        f"Minimum surface distance {distance:.6g} mm via {method}",
                        required=required,
                        metrics=row,
                    )
                )
            else:
                checks.append(check(interface_id, "FAIL", f"Unknown interface mode {mode!r}", required=required))
        except (TypeError, ValueError, ValidationInputError) as exc:
            checks.append(
                check(
                    interface_id,
                    "FAIL",
                    f"Invalid interface contract: {type(exc).__name__}: {exc}",
                    required=required,
                )
            )
        except Exception as exc:
            checks.append(
                check(
                    interface_id,
                    "NOT_RUN",
                    f"{type(exc).__name__}: {exc}",
                    required=required,
                )
            )
        metrics["interfaces"].append(row)

    for motion in motions_data:
        motion_id = str(motion.get("id", "unnamed-motion"))
        required = bool(motion.get("required", True))
        moving_id = motion.get("moving")
        stationary_ids = motion.get("stationary", [])
        translation = motion.get("translation_mm")
        try:
            steps = int(motion.get("steps", 40))
            tolerance = float(motion.get("max_intersection_volume_mm3", 0.001))
        except (TypeError, ValueError):
            checks.append(check(motion_id, "FAIL", "steps and max_intersection_volume_mm3 must be numeric", required=required))
            continue
        ignore_step_zero = bool(motion.get("ignore_step_zero", True))
        if moving_id not in meshes or not isinstance(stationary_ids, list) or any(item not in meshes for item in stationary_ids):
            checks.append(check(motion_id, "FAIL", "Motion part references are invalid", required=required))
            continue
        if not isinstance(translation, list) or len(translation) != 3 or not all(finite_number(value) for value in translation) or not 1 <= steps <= 10000 or not finite_number(tolerance) or tolerance < 0:
            checks.append(check(motion_id, "FAIL", "finite translation_mm, 1..10000 steps, and a non-negative finite intersection limit are required", required=required))
            continue
        step_distance = sum(float(value) ** 2 for value in translation) ** 0.5 / steps
        maximum_step = motion.get("max_step_mm")
        if maximum_step is not None and (not finite_number(maximum_step) or float(maximum_step) <= 0 or step_distance > float(maximum_step) + 1e-12):
            checks.append(check(motion_id, "FAIL", f"Motion step distance {step_distance:.6g} mm exceeds or cannot satisfy max_step_mm={maximum_step}", required=required))
            continue
        worst = 0.0
        worst_step = None
        methods = set()
        try:
            for step_index in range(steps + 1):
                if step_index == 0 and ignore_step_zero:
                    continue
                factor = step_index / steps
                moved = copy.deepcopy(meshes[moving_id])
                moved.apply_translation([float(value) * factor for value in translation])
                for stationary_id in stationary_ids:
                    volume, method = _intersection_volume(moved, meshes[stationary_id])
                    methods.add(method)
                    if volume > worst:
                        worst = volume
                        worst_step = {"step": step_index, "stationary": stationary_id, "fraction": factor}
            passed = worst <= tolerance + 1e-12
            row = {
                "id": motion_id,
                "moving": moving_id,
                "stationary": stationary_ids,
                "translation_mm": translation,
                "steps": steps,
                "worst_intersection_volume_mm3": worst,
                "worst_step": worst_step,
                "limit_mm3": tolerance,
                "methods": sorted(methods),
                "step_distance_mm": step_distance,
            }
            metrics["motions"].append(row)
            accepted_discrete = bool(motion.get("accept_discrete", False))
            status = "FAIL" if not passed else ("PASS" if accepted_discrete else "REVIEW_REQUIRED")
            checks.append(
                check(
                    motion_id,
                    status,
                    f"Motion sweep worst intersection {worst:.6g} mm³" + ("" if accepted_discrete or not passed else "; discrete coverage requires acceptance"),
                    required=required,
                    metrics=row,
                )
            )
        except Exception as exc:
            checks.append(check(motion_id, "NOT_RUN", f"{type(exc).__name__}: {exc}", required=required))

    if not checks:
        checks.append(check("interface-checks-present", "FAIL", "Contract defines no interfaces or motions"))
    return report(
        "check-interfaces",
        checks,
        inputs=paths,
        profile=profile,
        metrics=metrics,
        limitations=[
            "Motion sweeps are discretized; increase steps for narrow interference regions.",
            "Nearest-vertex clearance fallback is diagnostic and yields REVIEW_REQUIRED.",
            "Clearance does not replace a process-matched physical fit coupon.",
        ],
        capabilities=["mesh-boolean"],
    )
