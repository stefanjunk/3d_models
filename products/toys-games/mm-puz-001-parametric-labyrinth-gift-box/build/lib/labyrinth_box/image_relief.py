"""Optional STL-only cylindrical image relief.

This module is imported only when an image path is requested. Pillow, NumPy,
Trimesh, and a mesh boolean backend are loaded lazily by
:func:`load_optional_dependencies`.
"""

from __future__ import annotations

import importlib
import math
from pathlib import Path
import shutil
import warnings
from typing import Any, Sequence, TypeVar

from .config import BoxConfig
from .errors import ImageReliefError
from .preflight import DerivedDimensions


RELIEF_BOOLEAN_OVERLAP = 0.08
_Row = TypeVar("_Row")


class ImageReliefDependencyError(ImageReliefError):
    """An optional image or mesh dependency is unavailable."""


class ImageReliefInputError(ImageReliefError):
    """The requested source image cannot be read."""


class ImageReliefBooleanError(ImageReliefError):
    """The relief boolean did not produce an acceptable printable mesh."""


def load_optional_dependencies() -> tuple[Any, Any, Any, Any]:
    """Load optional modules or raise an install command with no hidden fallback."""
    try:
        image_module = importlib.import_module("PIL.Image")
        image_ops_module = importlib.import_module("PIL.ImageOps")
        numpy_module = importlib.import_module("numpy")
        trimesh_module = importlib.import_module("trimesh")
    except ModuleNotFoundError as error:
        raise ImageReliefDependencyError(
            "Image relief requires optional dependencies. Install them with "
            "python3 -m pip install '.[image-relief]' in a project-local environment."
        ) from error
    return image_module, image_ops_module, numpy_module, trimesh_module


def split_vertical_samples(
    rows: Sequence[_Row], grip_height: float, sleeve_height: float
) -> tuple[tuple[_Row, ...], tuple[_Row, ...]]:
    """Split bottom-to-top image rows in proportion to the two usable bands."""
    samples = tuple(rows)
    if grip_height <= 0:
        return (), samples
    total_height = grip_height + sleeve_height
    if total_height <= 0 or len(samples) < 2:
        raise ValueError("image relief needs positive band height and at least two rows")
    grip_count = round(len(samples) * grip_height / total_height)
    grip_count = max(1, min(len(samples) - 1, grip_count))
    return samples[:grip_count], samples[grip_count:]


def _select_boolean_engine(trimesh_module: Any) -> str:
    available = trimesh_module.boolean.engines_available
    if "manifold" in available:
        return "manifold"
    if "blender" in available and shutil.which("blender"):
        return "blender"
    raise ImageReliefDependencyError(
        "Image relief needs a robust mesh boolean backend. Install Manifold with "
        "python3 -m pip install '.[image-relief]' or provide Blender on PATH."
    )


def _load_strengths(
    image_path: Path,
    theta_samples: int,
    vertical_samples: int,
    invert: bool,
    image_module: Any,
    image_ops_module: Any,
    numpy_module: Any,
) -> Any:
    try:
        with image_module.open(image_path) as source:
            grayscale = image_ops_module.exif_transpose(source).convert("L")
            resized = grayscale.resize(
                (theta_samples, vertical_samples),
                resample=image_module.Resampling.LANCZOS,
            )
    except (OSError, ValueError) as error:
        raise ImageReliefInputError(
            f"Unable to read image relief source {image_path}: {error}"
        ) from error

    pixels = numpy_module.asarray(resized, dtype=float) / 255.0
    strengths = pixels if invert else 1.0 - pixels
    return numpy_module.flipud(numpy_module.clip(strengths, 0.0, 1.0))


def _cylindrical_heightfield_mesh(
    strengths: Any,
    radius: float,
    z_min: float,
    z_max: float,
    depth: float,
    mode: str,
    numpy_module: Any,
    trimesh_module: Any,
) -> Any:
    values = numpy_module.asarray(strengths, dtype=float)
    if values.ndim != 2 or values.shape[0] < 2 or values.shape[1] < 3:
        raise ImageReliefInputError(
            "Image relief needs at least two axial and three circumferential samples"
        )
    axial_samples, theta_samples = values.shape
    z_values = numpy_module.linspace(z_min, z_max, axial_samples)
    theta_values = numpy_module.arange(theta_samples) * (2.0 * math.pi / theta_samples)

    if mode == "emboss":
        inner_radii = numpy_module.full_like(values, radius - RELIEF_BOOLEAN_OVERLAP)
        outer_radii = radius + depth * values
    else:
        inner_radii = radius - depth * values
        outer_radii = numpy_module.full_like(values, radius + RELIEF_BOOLEAN_OVERLAP)

    vertices: list[tuple[float, float, float]] = []
    for radii in (inner_radii, outer_radii):
        for row, z_value in enumerate(z_values):
            for column, theta in enumerate(theta_values):
                local_radius = float(radii[row, column])
                vertices.append(
                    (
                        local_radius * math.cos(float(theta)),
                        local_radius * math.sin(float(theta)),
                        float(z_value),
                    )
                )

    layer_size = axial_samples * theta_samples

    def inner(row: int, column: int) -> int:
        return row * theta_samples + column

    def outer(row: int, column: int) -> int:
        return layer_size + row * theta_samples + column

    faces: list[tuple[int, int, int]] = []
    for row in range(axial_samples - 1):
        for column in range(theta_samples):
            next_column = (column + 1) % theta_samples
            oa = outer(row, column)
            ob = outer(row, next_column)
            oc = outer(row + 1, next_column)
            od = outer(row + 1, column)
            faces.extend(((oa, ob, oc), (oa, oc, od)))

            ia = inner(row, column)
            ib = inner(row, next_column)
            ic = inner(row + 1, next_column)
            id_ = inner(row + 1, column)
            faces.extend(((ia, ic, ib), (ia, id_, ic)))

    top = axial_samples - 1
    for column in range(theta_samples):
        next_column = (column + 1) % theta_samples
        bottom_inner = inner(0, column)
        bottom_inner_next = inner(0, next_column)
        bottom_outer = outer(0, column)
        bottom_outer_next = outer(0, next_column)
        faces.extend(
            (
                (bottom_inner, bottom_inner_next, bottom_outer_next),
                (bottom_inner, bottom_outer_next, bottom_outer),
            )
        )

        top_inner = inner(top, column)
        top_inner_next = inner(top, next_column)
        top_outer = outer(top, column)
        top_outer_next = outer(top, next_column)
        faces.extend(
            (
                (top_inner, top_outer, top_outer_next),
                (top_inner, top_outer_next, top_inner_next),
            )
        )

    mesh = trimesh_module.Trimesh(
        vertices=numpy_module.asarray(vertices),
        faces=numpy_module.asarray(faces),
        process=False,
    )
    if mesh.volume < 0:
        mesh.invert()
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
        raise ImageReliefBooleanError(
            "Generated cylindrical image height-field is not a closed positive solid"
        )
    return mesh


def _discard_zero_volume_boolean_fragments(
    mesh: Any, label: str
) -> tuple[Any, int]:
    """Keep one printable body and explicitly count only 2-face zero-volume artifacts.

    Blender's exact solver can emit paired coincident triangles at cylindrical
    intersection boundaries. No positive-volume or larger component is removed.
    The count is returned for manifest provenance rather than hidden as repair.
    """
    pieces = tuple(mesh.split(only_watertight=False))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        volumes = tuple(float(piece.volume) for piece in pieces)
    positive = [
        piece for piece, volume in zip(pieces, volumes) if abs(volume) > 1e-7
    ]
    artifacts = [
        piece for piece, volume in zip(pieces, volumes) if abs(volume) <= 1e-7
    ]
    if len(positive) != 1:
        raise ImageReliefBooleanError(
            f"{label} boolean produced {len(positive)} positive-volume bodies"
        )
    unacceptable = [piece for piece in artifacts if len(piece.faces) > 2]
    if unacceptable:
        raise ImageReliefBooleanError(
            f"{label} boolean produced nontrivial zero-volume components"
        )
    result = positive[0]
    if result.volume < 0:
        result.invert()
    return result, len(artifacts)


def _validate_single_body(mesh: Any, label: str) -> None:
    body_count = len(mesh.split(only_watertight=False))
    if (
        not mesh.is_watertight
        or not mesh.is_winding_consistent
        or mesh.volume <= 0
        or body_count != 1
    ):
        raise ImageReliefBooleanError(
            f"{label} image-relief boolean failed validation: "
            f"watertight={mesh.is_watertight}, "
            f"winding_consistent={mesh.is_winding_consistent}, "
            f"volume={mesh.volume:.6f}, bodies={body_count}"
        )


def _apply_boolean_to_file(
    stl_path: Path,
    relief: Any,
    transform: Any,
    mode: str,
    engine: str,
    trimesh_module: Any,
) -> int:
    base = trimesh_module.load_mesh(stl_path, force="mesh", process=True)
    if not isinstance(base, trimesh_module.Trimesh):
        raise ImageReliefBooleanError(f"{stl_path} did not reload as one mesh")
    transformed_relief = relief.copy()
    transformed_relief.apply_transform(transform)
    try:
        if mode == "emboss":
            decorated = trimesh_module.boolean.union(
                [base, transformed_relief], engine=engine
            )
        else:
            decorated = trimesh_module.boolean.difference(
                [base, transformed_relief], engine=engine
            )
    except Exception as error:
        raise ImageReliefBooleanError(
            f"Mesh boolean failed for {stl_path.name} with {engine}: {error}"
        ) from error
    if not isinstance(decorated, trimesh_module.Trimesh):
        raise ImageReliefBooleanError(
            f"Mesh boolean for {stl_path.name} did not return one mesh"
        )
    decorated, discarded_fragments = _discard_zero_volume_boolean_fragments(
        decorated, stl_path.name
    )
    _validate_single_body(decorated, stl_path.name)

    temporary_path = stl_path.with_suffix(".image-relief.tmp.stl")
    decorated.export(temporary_path)
    reloaded = trimesh_module.load_mesh(temporary_path, force="mesh", process=True)
    if not isinstance(reloaded, trimesh_module.Trimesh):
        raise ImageReliefBooleanError(
            f"Reloaded {temporary_path.name} is not one Trimesh body"
        )
    _validate_single_body(reloaded, f"reloaded {stl_path.name}")
    temporary_path.replace(stl_path)
    return discarded_fragments


def apply_image_relief_to_exports(
    config: BoxConfig,
    dimensions: DerivedDimensions,
    output_directory: Path,
) -> dict[str, object]:
    """Boolean a shared cylindrical image across print-oriented STL bands."""
    if config.image_relief_path is None:
        return {"requested": False}

    image_module, image_ops_module, numpy_module, trimesh_module = (
        load_optional_dependencies()
    )
    engine = _select_boolean_engine(trimesh_module)
    grip_height = max(0.0, config.grip_length - 2.0 * config.decoration_margin)
    sleeve_height = dimensions.sleeve_height - 2.0 * config.decoration_margin
    total_height = grip_height + sleeve_height
    circumference = 2.0 * math.pi * dimensions.sleeve_outer_radius
    vertical_samples = max(
        4,
        min(
            config.image_relief_resolution,
            round(config.image_relief_resolution * total_height / circumference) + 1,
        ),
    )
    strengths = _load_strengths(
        Path(config.image_relief_path).expanduser(),
        config.image_relief_resolution,
        vertical_samples,
        config.image_relief_invert,
        image_module,
        image_ops_module,
        numpy_module,
    )
    grip_rows, sleeve_rows = split_vertical_samples(
        tuple(strengths), grip_height, sleeve_height
    )

    identity_with_inner_translation = numpy_module.eye(4)
    identity_with_inner_translation[2, 3] = config.grip_length
    discarded_fragments = 0
    if grip_rows:
        grip_values = numpy_module.stack(grip_rows)
        if grip_values.shape[0] == 1:
            grip_values = numpy_module.vstack((grip_values, grip_values))
        grip_relief = _cylindrical_heightfield_mesh(
            grip_values,
            dimensions.grip_radius,
            -config.grip_length + config.decoration_margin,
            -config.decoration_margin,
            config.decoration_depth,
            config.decoration_mode,
            numpy_module,
            trimesh_module,
        )
        discarded_fragments += _apply_boolean_to_file(
            output_directory / "inner.stl",
            grip_relief,
            identity_with_inner_translation,
            config.decoration_mode,
            engine,
            trimesh_module,
        )

    sleeve_values = numpy_module.stack(sleeve_rows)
    if sleeve_values.shape[0] == 1:
        sleeve_values = numpy_module.vstack((sleeve_values, sleeve_values))
    sleeve_relief = _cylindrical_heightfield_mesh(
        sleeve_values,
        dimensions.sleeve_outer_radius,
        config.decoration_margin,
        dimensions.sleeve_height - config.decoration_margin,
        config.decoration_depth,
        config.decoration_mode,
        numpy_module,
        trimesh_module,
    )
    outer_transform = numpy_module.asarray(
        (
            (1.0, 0.0, 0.0, 0.0),
            (0.0, -1.0, 0.0, 0.0),
            (0.0, 0.0, -1.0, dimensions.sleeve_height),
            (0.0, 0.0, 0.0, 1.0),
        )
    )
    discarded_fragments += _apply_boolean_to_file(
        output_directory / "outer.stl",
        sleeve_relief,
        outer_transform,
        config.decoration_mode,
        engine,
        trimesh_module,
    )
    return {
        "requested": True,
        "boolean_engine": engine,
        "theta_samples": config.image_relief_resolution,
        "vertical_samples": vertical_samples,
        "step_includes_raster_relief": False,
        "stl_includes_raster_relief": True,
        "discarded_zero_volume_boolean_fragments": discarded_fragments,
    }
