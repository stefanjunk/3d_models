from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import check, report
from .mesh import _load_mesh


def _sample(mesh, count: int, seed: int):
    import trimesh

    points, _ = trimesh.sample.sample_surface(mesh, count, seed=seed)
    return points


def _distance(target, points):
    import numpy as np
    import trimesh

    try:
        _, distances, _ = trimesh.proximity.closest_point(target, points)
        return np.asarray(distances, dtype=float), "triangle-indexed", True
    except Exception:
        try:
            from scipy.spatial import cKDTree

            tree = cKDTree(target.vertices)
            distances, _ = tree.query(points, workers=1)
            return np.asarray(distances, dtype=float), "nearest-vertex-fallback", False
        except Exception as exc:
            raise RuntimeError(f"no surface-distance backend available: {exc}") from exc


def _stats(values) -> dict[str, float]:
    import numpy as np

    return {
        "mean_mm": float(np.mean(values)),
        "rms_mm": float(np.sqrt(np.mean(values * values))),
        "p50_mm": float(np.percentile(values, 50)),
        "p95_mm": float(np.percentile(values, 95)),
        "p99_mm": float(np.percentile(values, 99)),
        "max_mm": float(np.max(values)),
    }


def compare(
    reference_path: Path,
    candidate_path: Path,
    policy: dict[str, Any] | None = None,
    profile: str = "release",
) -> dict[str, Any]:
    policy = policy or {}
    checks: list[dict[str, Any]] = []
    missing = [path for path in (reference_path, candidate_path) if not path.is_file()]
    if missing:
        return report(
            "compare-meshes",
            [check("mesh-inputs", "FAIL", "Missing mesh input(s): " + ", ".join(map(str, missing)))],
            inputs=[reference_path, candidate_path],
            profile=profile,
        )
    try:
        _, reference = _load_mesh(reference_path)
        _, candidate = _load_mesh(candidate_path)
    except ImportError as exc:
        return report(
            "compare-meshes",
            [check("mesh-distance-capability", "NOT_RUN", str(exc))],
            inputs=[reference_path, candidate_path],
            profile=profile,
            capabilities=["mesh-distance"],
        )
    except Exception as exc:
        return report(
            "compare-meshes",
            [check("mesh-load", "FAIL", f"{type(exc).__name__}: {exc}")],
            inputs=[reference_path, candidate_path],
            profile=profile,
        )

    count = max(100, min(int(policy.get("samples", 30000)), 1_000_000))
    seed = int(policy.get("seed", 42))
    try:
        ref_points = _sample(reference, count, seed)
        cand_points = _sample(candidate, count, seed + 1)
        ref_to_cand, method_a, exact_a = _distance(candidate, ref_points)
        cand_to_ref, method_b, exact_b = _distance(reference, cand_points)
    except Exception as exc:
        return report(
            "compare-meshes",
            [check("surface-distance", "NOT_RUN", f"{type(exc).__name__}: {exc}")],
            inputs=[reference_path, candidate_path],
            profile=profile,
            capabilities=["mesh-distance"],
        )

    a = _stats(ref_to_cand)
    b = _stats(cand_to_ref)
    worst = {key: max(a[key], b[key]) for key in a}
    ref_extents = [float(value) for value in reference.extents]
    cand_extents = [float(value) for value in candidate.extents]
    extent_delta = [abs(a0 - b0) for a0, b0 in zip(ref_extents, cand_extents)]
    reference_volume = float(reference.volume)
    candidate_volume = float(candidate.volume)
    volume_delta_percent = (
        abs(candidate_volume - reference_volume) / abs(reference_volume) * 100.0
        if abs(reference_volume) > 1e-12
        else None
    )
    metrics = {
        "samples_per_direction": count,
        "seed": seed,
        "reference_to_candidate": a,
        "candidate_to_reference": b,
        "worst_bidirectional": worst,
        "distance_methods": [method_a, method_b],
        "triangle_exact": bool(exact_a and exact_b),
        "reference_extents_mm": ref_extents,
        "candidate_extents_mm": cand_extents,
        "absolute_extent_delta_mm": extent_delta,
        "reference_volume_mm3": reference_volume,
        "candidate_volume_mm3": candidate_volume,
        "absolute_volume_delta_percent": volume_delta_percent,
    }
    checks.append(check("surface-distance-executed", "PASS", "Bidirectional sampled distance completed", metrics={"method": [method_a, method_b]}))
    require_triangle_exact = bool(policy.get("require_triangle_exact", profile == "release"))
    if require_triangle_exact and not (exact_a and exact_b):
        checks.append(
            check(
                "triangle-distance-backend",
                "NOT_RUN",
                "Exact indexed triangle distance was unavailable; nearest-vertex fallback is diagnostic only",
            )
        )
    thresholds = {
        "max_rms_mm": "rms_mm",
        "max_p95_mm": "p95_mm",
        "max_p99_mm": "p99_mm",
        "max_surface_mm": "max_mm",
    }
    declared_thresholds = [key for key in (*thresholds, "max_extent_delta_mm", "max_volume_delta_percent") if key in policy]
    if not declared_thresholds:
        checks.append(check("comparison-thresholds", "REVIEW_REQUIRED", "No acceptance threshold was declared; distance metrics are diagnostic only"))
    for policy_key, metric_key in thresholds.items():
        if policy_key in policy:
            limit = float(policy[policy_key])
            actual = worst[metric_key]
            checks.append(
                check(
                    policy_key.replace("max_", "surface-").replace("_mm", ""),
                    "PASS" if limit >= 0 and actual <= limit else "FAIL",
                    f"{metric_key}={actual:.6g} mm; limit={limit:g} mm",
                    metrics={"actual_mm": actual, "limit_mm": limit},
                )
            )
    if "max_extent_delta_mm" in policy:
        actual = max(extent_delta)
        limit = float(policy["max_extent_delta_mm"])
        checks.append(
            check(
                "extent-regression",
                "PASS" if limit >= 0 and actual <= limit else "FAIL",
                f"Maximum extent delta {actual:.6g} mm; limit {limit:g} mm",
                metrics={"actual_mm": actual, "limit_mm": limit},
            )
        )
    if "max_volume_delta_percent" in policy:
        limit = float(policy["max_volume_delta_percent"])
        passed = limit >= 0 and volume_delta_percent is not None and volume_delta_percent <= limit
        checks.append(
            check(
                "volume-regression",
                "PASS" if passed else "FAIL",
                f"Absolute volume delta {volume_delta_percent}% ; limit {limit:g}%",
                metrics={"actual_percent": volume_delta_percent, "limit_percent": limit},
            )
        )
    return report(
        "compare-meshes",
        checks,
        inputs=[reference_path, candidate_path],
        profile=profile,
        metrics=metrics,
        limitations=[
            "This is a seeded sampled comparison, not a mathematical Hausdorff proof.",
            "Evaluate protected interfaces and ROIs separately; a global percentile can hide a small critical breach.",
        ],
        capabilities=["mesh-distance"],
    )
