# Run inside FreeCAD Python console or as a macro.
# This is appropriate only for a repaired, moderate-size closed mesh.
import FreeCAD as App
import Mesh
import Part

SOURCE = "source.stl"
OUTPUT_STEP = "result.step"
SEW_TOLERANCE = 0.05

mesh = Mesh.Mesh(SOURCE)
if mesh.CountFacets > 500_000:
    raise RuntimeError("Dense mesh conversion is likely impractical; use Blender/Manifold/SDF instead")

shape = Part.Shape()
shape.makeShapeFromMesh(mesh.Topology, SEW_TOLERANCE)
if not shape.isClosed():
    raise RuntimeError("Mesh-derived shape is not closed")
solid = Part.makeSolid(shape)

cutter = Part.makeCylinder(20.0, 80.0, App.Vector(0, 0, -40))
result = solid.cut(cutter)
if result.isNull():
    raise RuntimeError("Boolean returned a null shape")
result.exportStep(OUTPUT_STEP)
