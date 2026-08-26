# Tests

The standard-library `unittest` suite checks:

- curve fairing and Fourier filtering;
- closed loft and profile-extrusion topology;
- vertex welding across CAD tessellation patches;
- identity and protected-region FFD behavior;
- routing, hardpoint comparison, project initialization, and OpenCode skill metadata;
- all three example builds;
- optional SciPy B-spline fitting, Trimesh section extraction, and CadQuery STEP lofting when installed.

Run from the package root:

```bash
make test
```

Missing optional backends are skipped in tests and must be reported as `NOT_RUN` in project work.
