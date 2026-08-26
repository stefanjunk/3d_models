# Script index

All paths below are relative to the skill directory. Core scripts use NumPy/PyYAML only unless marked optional.

| Script | Purpose | Backend |
|---|---|---|
| `surface_geometry.py` | fairing, resampling, curvature screening, lofting, mesh I/O/metrics, FFD | NumPy core |
| `route_method.py` | select NURBS/loft, SubD/FFD, SDF, or hybrid route | Python core |
| `validate_spec.py` | validate `surfacing-spec.yaml` | PyYAML core |
| `fair_curve.py` | regularized or Fourier curve fairing | NumPy core |
| `analyze_curve.py` | curvature/fairness screening report | NumPy core |
| `fit_bspline.py` | fit and report an actual parametric B-spline | optional SciPy |
| `extract_mesh_sections.py` | cut a reference mesh into closed section CSVs | optional Trimesh |
| `loft_sections.py` | seam-align and triangulate closed CSV sections | NumPy core |
| `backends/cadquery_loft_to_step.py` | exact OpenCascade loft and STEP/STL export | optional CadQuery |
| `ffd_deform.py` | Bernstein-lattice FFD for OBJ masters | NumPy core |
| `compare_hardpoints.py` | compare named points, axes, and planes | NumPy core |
| `mesh_report.py` | edge-incidence, component, area, bounds, volume report | NumPy core |
| `run_examples.py` | build all three examples | NumPy/PyYAML core |
| `environment_check.py` | report installed optional backends | Python core |
| `project_init.py` | create a source-first project tree | Python core |
| `validate_skill.py` | OpenCode frontmatter/layout and Python compile checks | PyYAML core |
| `build_manifest.py` | package manifest and checksums | Python core |

Use `--help` on each CLI. No script automatically installs software, downloads models, or overwrites an authoritative source mesh.
