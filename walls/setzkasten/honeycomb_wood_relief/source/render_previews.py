#!/usr/bin/env python3
"""Render multi-angle PNG evidence for the textured honeycomb STL with VTK."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw
import vtk


SOURCE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SOURCE_DIR.parent
PREVIEW_DIR = PROJECT_DIR / "previews"
REPORT_DIR = PROJECT_DIR / "reports"
DEFAULT_FINAL = PROJECT_DIR / "exports" / "wabe_ohne_aufhaengung_wood_relief.stl"
DEFAULT_PREVIEW = PREVIEW_DIR / "wabe_ohne_aufhaengung_preview.stl"


def render_view(
    mesh_path: Path,
    output: Path,
    direction: tuple[float, float, float],
    view_up: tuple[float, float, float],
    scale: float,
    focal_offset: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(mesh_path))

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(reader.GetOutputPort())
    normals.ComputePointNormalsOn()
    normals.ConsistencyOn()
    normals.AutoOrientNormalsOn()
    normals.SplittingOff()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    prop = actor.GetProperty()
    prop.SetColor(0.48, 0.24, 0.085)
    prop.SetAmbient(0.22)
    prop.SetDiffuse(0.72)
    prop.SetSpecular(0.16)
    prop.SetSpecularPower(24.0)
    prop.SetInterpolationToPhong()

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.035, 0.045, 0.055)
    renderer.SetBackground2(0.13, 0.15, 0.17)
    renderer.GradientBackgroundOn()
    renderer.AddActor(actor)

    key = vtk.vtkLight()
    key.SetLightTypeToSceneLight()
    key.SetPosition(-260.0, -320.0, -280.0)
    key.SetFocalPoint(0.0, 0.0, 20.0)
    key.SetColor(1.0, 0.86, 0.68)
    key.SetIntensity(0.95)
    renderer.AddLight(key)

    fill = vtk.vtkLight()
    fill.SetLightTypeToSceneLight()
    fill.SetPosition(280.0, 180.0, -80.0)
    fill.SetFocalPoint(0.0, 0.0, 20.0)
    fill.SetColor(0.62, 0.76, 1.0)
    fill.SetIntensity(0.55)
    renderer.AddLight(fill)

    rim = vtk.vtkLight()
    rim.SetLightTypeToSceneLight()
    rim.SetPosition(80.0, 260.0, 320.0)
    rim.SetFocalPoint(0.0, 0.0, 20.0)
    rim.SetColor(1.0, 0.93, 0.82)
    rim.SetIntensity(0.65)
    renderer.AddLight(rim)

    reader.Update()
    bounds = reader.GetOutput().GetBounds()
    center = (
        (bounds[0] + bounds[1]) * 0.5 + focal_offset[0],
        (bounds[2] + bounds[3]) * 0.5 + focal_offset[1],
        (bounds[4] + bounds[5]) * 0.5 + focal_offset[2],
    )
    distance = 520.0
    camera = renderer.GetActiveCamera()
    camera.SetFocalPoint(*center)
    camera.SetPosition(
        center[0] + direction[0] * distance,
        center[1] + direction[1] * distance,
        center[2] + direction[2] * distance,
    )
    camera.SetViewUp(*view_up)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(scale)
    renderer.ResetCameraClippingRange()

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1000, 800)
    window.SetMultiSamples(4)
    window.AddRenderer(renderer)
    window.Render()

    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGBA()
    capture.ReadFrontBufferOff()
    capture.Update()

    output.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(output))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()


def contact_sheet(images: list[tuple[str, Path]], output: Path) -> None:
    thumb_size = (700, 560)
    canvas = Image.new("RGB", (thumb_size[0] * 2, thumb_size[1] * 2), (10, 13, 16))
    draw = ImageDraw.Draw(canvas)
    for index, (label, path) in enumerate(images):
        image = Image.open(path).convert("RGB")
        image.thumbnail((thumb_size[0], thumb_size[1] - 36), Image.Resampling.LANCZOS)
        x = (index % 2) * thumb_size[0] + (thumb_size[0] - image.width) // 2
        y = (index // 2) * thumb_size[1] + 34
        canvas.paste(image, (x, y))
        draw.text(((index % 2) * thumb_size[0] + 18, (index // 2) * thumb_size[1] + 10), label, fill=(232, 224, 208))
    canvas.save(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=Path)
    parser.add_argument("--prefix", default="wood_relief")
    args = parser.parse_args()
    mesh = args.mesh.resolve() if args.mesh else (DEFAULT_FINAL if DEFAULT_FINAL.exists() else DEFAULT_PREVIEW)
    prefix = args.prefix.strip().replace(" ", "_")
    if not prefix:
        raise ValueError("prefix must not be empty")
    if not mesh.is_file():
        raise FileNotFoundError(f"No textured STL available: {mesh}")

    views = [
        ("front", (0.0, 0.0, -1.0), (0.0, 1.0, 0.0), 135.0, (0.0, 0.0, 0.0)),
        ("front_oblique", (0.85, -1.0, -0.80), (0.0, 1.0, 0.0), 142.0, (0.0, 0.0, 0.0)),
        ("rear_oblique", (-0.85, 0.95, 0.75), (0.0, 1.0, 0.0), 142.0, (0.0, 0.0, 0.0)),
        ("wood_detail", (1.0, -0.55, -0.45), (0.0, 1.0, 0.0), 58.0, (68.0, -16.0, -8.0)),
    ]
    outputs: list[tuple[str, Path]] = []
    for label, direction, up, scale, offset in views:
        path = PREVIEW_DIR / f"{prefix}_{label}.png"
        render_view(mesh, path, direction, up, scale, offset)
        outputs.append((label.replace("_", " ").title(), path))
        print(f"Rendered: {path}")

    sheet = PREVIEW_DIR / f"{prefix}_multiview.png"
    contact_sheet(outputs, sheet)
    report = {
        "mesh": str(mesh),
        "renderer": f"VTK {vtk.vtkVersion.GetVTKVersion()} off-screen",
        "views": [{"label": label, "path": str(path)} for label, path in outputs],
        "contact_sheet": str(sheet),
        "passed": all(path.is_file() and path.stat().st_size > 0 for _, path in outputs) and sheet.is_file(),
    }
    report_path = REPORT_DIR / f"preview_rendering_{prefix}.json"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
