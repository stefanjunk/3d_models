"""FreeCAD macro template for measured placement of a mesh and STEP functional part."""
from pathlib import Path
import FreeCAD as App
import Mesh
import Part

DOC = App.newDocument("OrganicFunctionalAssembly")
ROOT = Path(__file__).resolve().parent

mesh_obj = DOC.addObject("Mesh::Feature", "OrganicSource")
mesh_obj.Mesh = Mesh.Mesh(str(ROOT / "source-clean.stl"))

step_shape = Part.read(str(ROOT / "functional-part.step"))
part_obj = DOC.addObject("PartDesign::Feature", "FunctionalPart")
part_obj.Shape = step_shape

# Replace with the recorded transform/Placement from the operation plan.
part_obj.Placement.Base = App.Vector(0, 0, 0)

DOC.recompute()
DOC.saveAs(str(ROOT / "assembly.FCStd"))
