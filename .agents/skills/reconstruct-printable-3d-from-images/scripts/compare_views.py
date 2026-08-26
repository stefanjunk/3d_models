#!/usr/bin/env python3
"""Compare a source view and a matched model render.

The script reports several diagnostics and produces overlays. It does not turn
2D reprojection similarity into a claim of complete 3D correctness.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageOps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare matched source/render views with silhouette and image diagnostics."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--source-mask", type=Path)
    parser.add_argument("--candidate-mask", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--alignment", choices=("none", "bbox"), default="none")
    parser.add_argument("--mask-threshold", type=int, default=127)
    parser.add_argument("--boundary-tolerance-px", type=float, default=2.0)
    parser.add_argument("--landmarks", type=Path)
    parser.add_argument("--no-ssim", action="store_true")
    parser.add_argument("--fail-iou-below", type=float)
    return parser.parse_args()


def load_rgba(path: Path) -> Image.Image:
    if not path.is_file():
        raise SystemExit(f"Image not found: {path}")
    with Image.open(path) as opened:
        return ImageOps.exif_transpose(opened).convert("RGBA")


def load_mask(
    path: Path | None,
    image: Image.Image,
    threshold: int,
    label: str,
) -> tuple[Image.Image, str, list[str]]:
    warnings: list[str] = []
    if path:
        if not path.is_file():
            raise SystemExit(f"{label} mask not found: {path}")
        with Image.open(path) as opened:
            mask = ImageOps.exif_transpose(opened).convert("L")
        if mask.size != image.size:
            raise SystemExit(
                f"{label} mask size {mask.size} does not match image size {image.size}"
            )
        binary = mask.point(lambda value: 255 if value > threshold else 0, mode="L")
        return binary, f"explicit mask {path}", warnings

    alpha = image.getchannel("A")
    extrema = alpha.getextrema()
    if extrema[0] < 250:
        binary = alpha.point(lambda value: 255 if value > threshold else 0, mode="L")
        return binary, "image alpha", warnings

    warnings.append(
        f"{label} image is opaque and no mask was supplied; the full-frame mask "
        "makes silhouette metrics uninformative."
    )
    return Image.new("L", image.size, 255), "opaque full-frame fallback", warnings


def bbox_fit(
    candidate: Image.Image, candidate_mask: Image.Image, reference_mask: Image.Image
) -> tuple[Image.Image, Image.Image, dict[str, Any]]:
    ref_bbox = reference_mask.getbbox()
    cand_bbox = candidate_mask.getbbox()
    if ref_bbox is None or cand_bbox is None:
        raise SystemExit("Cannot bbox-align an empty source or candidate mask")

    rl, rt, rr, rb = ref_bbox
    cl, ct, cr, cb = cand_bbox
    ref_w, ref_h = rr - rl, rb - rt
    cand_w, cand_h = cr - cl, cb - ct
    scale = min(ref_w / cand_w, ref_h / cand_h)
    new_w = max(1, int(round(cand_w * scale)))
    new_h = max(1, int(round(cand_h * scale)))

    cropped_image = candidate.crop(cand_bbox).resize(
        (new_w, new_h), Image.Resampling.LANCZOS
    )
    cropped_mask = candidate_mask.crop(cand_bbox).resize(
        (new_w, new_h), Image.Resampling.NEAREST
    )
    center_x = (rl + rr) / 2.0
    center_y = (rt + rb) / 2.0
    dst_x = int(round(center_x - new_w / 2.0))
    dst_y = int(round(center_y - new_h / 2.0))

    canvas = Image.new("RGBA", reference_mask.size, (0, 0, 0, 0))
    mask_canvas = Image.new("L", reference_mask.size, 0)
    canvas.paste(cropped_image, (dst_x, dst_y), cropped_image)
    mask_canvas.paste(cropped_mask, (dst_x, dst_y))
    return (
        canvas,
        mask_canvas,
        {
            "mode": "bbox uniform-scale and translation",
            "uniform_scale": scale,
            "candidate_crop_box": list(cand_bbox),
            "destination_xy": [dst_x, dst_y],
            "destination_size": [new_w, new_h],
            "warning": "Diagnostic alignment can hide camera/scale error; do not use it as locked acceptance.",
        },
    )


def erode_3x3(mask: np.ndarray) -> np.ndarray:
    padded = np.pad(mask, 1, mode="constant", constant_values=False)
    result = np.ones_like(mask, dtype=bool)
    height, width = mask.shape
    for dy in range(3):
        for dx in range(3):
            result &= padded[dy : dy + height, dx : dx + width]
    return result


def boundary(mask: np.ndarray) -> np.ndarray:
    return mask & ~erode_3x3(mask)


def silhouette_metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    intersection = int(np.count_nonzero(reference & candidate))
    union = int(np.count_nonzero(reference | candidate))
    ref_area = int(np.count_nonzero(reference))
    cand_area = int(np.count_nonzero(candidate))
    iou = intersection / union if union else 1.0
    precision = intersection / cand_area if cand_area else (1.0 if ref_area == 0 else 0.0)
    recall = intersection / ref_area if ref_area else (1.0 if cand_area == 0 else 0.0)
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return {
        "reference_area_px": ref_area,
        "candidate_area_px": cand_area,
        "intersection_px": intersection,
        "union_px": union,
        "iou": iou,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def boundary_metrics(
    reference: np.ndarray, candidate: np.ndarray, tolerance_px: float
) -> tuple[dict[str, Any] | None, list[str]]:
    warnings: list[str] = []
    try:
        from scipy.ndimage import distance_transform_edt
    except ImportError:
        warnings.append(
            "SciPy is not installed; boundary distance and boundary F1 were skipped."
        )
        return None, warnings

    ref_boundary = boundary(reference)
    cand_boundary = boundary(candidate)
    if not ref_boundary.any() or not cand_boundary.any():
        warnings.append("A boundary mask is empty; boundary diagnostics were skipped.")
        return None, warnings

    distance_to_candidate = distance_transform_edt(~cand_boundary)
    distance_to_reference = distance_transform_edt(~ref_boundary)
    ref_to_cand = distance_to_candidate[ref_boundary]
    cand_to_ref = distance_to_reference[cand_boundary]
    combined = np.concatenate([ref_to_cand, cand_to_ref])
    diagonal = math.hypot(reference.shape[1], reference.shape[0])

    boundary_precision = float(np.mean(cand_to_ref <= tolerance_px))
    boundary_recall = float(np.mean(ref_to_cand <= tolerance_px))
    boundary_f1 = (
        2 * boundary_precision * boundary_recall / (boundary_precision + boundary_recall)
        if boundary_precision + boundary_recall
        else 0.0
    )
    return (
        {
            "reference_to_candidate_mean_px": float(np.mean(ref_to_cand)),
            "candidate_to_reference_mean_px": float(np.mean(cand_to_ref)),
            "symmetric_mean_px": float(np.mean(combined)),
            "symmetric_p95_px": float(np.percentile(combined, 95)),
            "symmetric_max_px": float(np.max(combined)),
            "symmetric_mean_fraction_image_diagonal": float(np.mean(combined) / diagonal),
            "tolerance_px": tolerance_px,
            "boundary_precision_at_tolerance": boundary_precision,
            "boundary_recall_at_tolerance": boundary_recall,
            "boundary_f1_at_tolerance": boundary_f1,
        },
        warnings,
    )


def composite_rgb(image: Image.Image, mask: np.ndarray) -> np.ndarray:
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    white = np.full_like(rgb, 255)
    return np.where(mask[:, :, None], rgb, white)


def image_metrics(
    reference: np.ndarray,
    candidate: np.ndarray,
    common_mask: np.ndarray,
    no_ssim: bool,
) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    difference = reference.astype(np.float32) - candidate.astype(np.float32)
    full_mae = float(np.mean(np.abs(difference)))
    mse = float(np.mean(difference**2))
    psnr = None if mse == 0 else 20 * math.log10(255.0 / math.sqrt(mse))
    if common_mask.any():
        common_mae = float(np.mean(np.abs(difference[common_mask])))
    else:
        common_mae = None

    ssim = None
    if not no_ssim:
        try:
            from skimage.metrics import structural_similarity

            ref_gray = np.dot(reference[:, :, :3], [0.2126, 0.7152, 0.0722])
            cand_gray = np.dot(candidate[:, :, :3], [0.2126, 0.7152, 0.0722])
            ssim = float(
                structural_similarity(ref_gray, cand_gray, data_range=255.0)
            )
        except ImportError:
            warnings.append("scikit-image is not installed; SSIM was skipped.")
        except ValueError as exc:
            warnings.append(f"SSIM was skipped because the image is unsuitable: {exc}")

    return (
        {
            "white_background_rgb_mae_full_frame": full_mae,
            "rgb_mae_common_foreground": common_mae,
            "white_background_psnr_db": psnr,
            "white_background_psnr_is_infinite": mse == 0,
            "white_background_luma_ssim": ssim,
            "warning": "Appearance metrics require matched lighting and color management.",
        },
        warnings,
    )


def landmark_metrics(path: Path | None, width: int, height: int) -> dict[str, Any] | None:
    if path is None:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        entries = data.get("landmarks", [])
    elif isinstance(data, list):
        entries = data
    else:
        entries = []
    if not isinstance(entries, list) or not entries:
        raise SystemExit("Landmark JSON must contain a non-empty 'landmarks' list")
    diagonal = math.hypot(width, height)
    weighted_sum = 0.0
    total_weight = 0.0
    output = []
    for entry in entries:
        ref = entry["reference"]
        cand = entry["candidate"]
        weight = float(entry.get("weight", 1.0))
        distance = math.hypot(float(ref[0]) - float(cand[0]), float(ref[1]) - float(cand[1]))
        weighted_sum += weight * distance
        total_weight += weight
        output.append(
            {
                "id": entry.get("id", str(len(output) + 1)),
                "distance_px": distance,
                "distance_fraction_image_diagonal": distance / diagonal,
                "weight": weight,
            }
        )
    mean = weighted_sum / total_weight if total_weight else 0.0
    return {
        "landmarks": output,
        "weighted_mean_distance_px": mean,
        "weighted_mean_fraction_image_diagonal": mean / diagonal,
    }


def save_outputs(
    output_dir: Path,
    source_rgb: np.ndarray,
    candidate_rgb: np.ndarray,
    source_mask: np.ndarray,
    candidate_mask: np.ndarray,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_image = Image.fromarray(source_rgb.astype(np.uint8), mode="RGB")
    candidate_image = Image.fromarray(candidate_rgb.astype(np.uint8), mode="RGB")
    Image.blend(source_image, candidate_image, 0.5).save(output_dir / "overlay.png")

    absolute = np.abs(source_rgb.astype(np.int16) - candidate_rgb.astype(np.int16))
    difference = np.clip(absolute * 3, 0, 255).astype(np.uint8)
    Image.fromarray(difference, mode="RGB").save(output_dir / "difference-x3.png")

    silhouette = np.zeros((*source_mask.shape, 3), dtype=np.uint8)
    silhouette[source_mask & candidate_mask] = [230, 230, 230]
    silhouette[source_mask & ~candidate_mask] = [255, 70, 70]
    silhouette[~source_mask & candidate_mask] = [40, 220, 255]
    Image.fromarray(silhouette, mode="RGB").save(
        output_dir / "silhouette-overlay.png"
    )

    Image.fromarray(source_mask.astype(np.uint8) * 255, mode="L").save(
        output_dir / "source-mask-used.png"
    )
    Image.fromarray(candidate_mask.astype(np.uint8) * 255, mode="L").save(
        output_dir / "candidate-mask-used.png"
    )


def main() -> int:
    args = parse_args()
    if not 0 <= args.mask_threshold <= 255:
        raise SystemExit("--mask-threshold must be between 0 and 255")
    if args.boundary_tolerance_px < 0:
        raise SystemExit("--boundary-tolerance-px cannot be negative")
    if args.fail_iou_below is not None and not 0 <= args.fail_iou_below <= 1:
        raise SystemExit("--fail-iou-below must be between 0 and 1")

    source = load_rgba(args.source)
    candidate = load_rgba(args.candidate)
    source_mask_img, source_mask_method, warnings = load_mask(
        args.source_mask, source, args.mask_threshold, "source"
    )
    candidate_mask_img, candidate_mask_method, candidate_warnings = load_mask(
        args.candidate_mask, candidate, args.mask_threshold, "candidate"
    )
    warnings.extend(candidate_warnings)

    alignment_report: dict[str, Any] = {"mode": "none (locked pixels)"}
    if args.alignment == "none":
        if candidate.size != source.size:
            raise SystemExit(
                f"Image sizes differ: source={source.size}, candidate={candidate.size}. "
                "Render/crop matched views or use --alignment bbox for diagnosis."
            )
    else:
        candidate, candidate_mask_img, alignment_report = bbox_fit(
            candidate, candidate_mask_img, source_mask_img
        )
        warnings.append(alignment_report["warning"])

    source_mask = np.asarray(source_mask_img) > args.mask_threshold
    candidate_mask = np.asarray(candidate_mask_img) > args.mask_threshold
    if source_mask.mean() > 0.98 or candidate_mask.mean() > 0.98:
        warnings.append(
            "At least one mask covers almost the full frame; inspect silhouette metrics carefully."
        )

    source_composite = composite_rgb(source, source_mask)
    candidate_composite = composite_rgb(candidate, candidate_mask)
    silhouette = silhouette_metrics(source_mask, candidate_mask)
    boundary_result, boundary_warnings = boundary_metrics(
        source_mask, candidate_mask, args.boundary_tolerance_px
    )
    warnings.extend(boundary_warnings)
    appearance, appearance_warnings = image_metrics(
        source_composite,
        candidate_composite,
        source_mask & candidate_mask,
        args.no_ssim,
    )
    warnings.extend(appearance_warnings)
    landmarks = landmark_metrics(args.landmarks, source.width, source.height)

    save_outputs(
        args.output_dir,
        source_composite,
        candidate_composite,
        source_mask,
        candidate_mask,
    )

    report = {
        "source": str(args.source.resolve()),
        "candidate": str(args.candidate.resolve()),
        "canvas_px": [source.width, source.height],
        "source_mask_method": source_mask_method,
        "candidate_mask_method": candidate_mask_method,
        "alignment": alignment_report,
        "silhouette": silhouette,
        "boundary": boundary_result,
        "landmarks": landmarks,
        "appearance": appearance,
        "warnings": warnings,
        "interpretation": [
            "Review silhouette-overlay.png: red is missing candidate area; cyan is extra candidate area.",
            "A source-view match does not validate unseen geometry, scale, wall thickness, or function.",
            "Set project-specific thresholds from evidence uncertainty and physical tolerances.",
        ],
    }
    rendered = json.dumps(report, indent=2, allow_nan=False)
    (args.output_dir / "comparison.json").write_text(
        rendered + "\n", encoding="utf-8"
    )
    print(rendered)

    if args.fail_iou_below is not None and silhouette["iou"] < args.fail_iou_below:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
