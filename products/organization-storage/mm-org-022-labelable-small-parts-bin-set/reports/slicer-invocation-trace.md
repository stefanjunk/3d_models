# Anycubic slicer invocation trace — MM-ORG-022

Date: 2026-08-28

Scope: Anycubic Slicer Next 1.3.9.4, `fdm_ci.py` adapter 1.2.1, Kobra 3 Max 0.4 mm / 0.20 mm Standard / Anycubic PLA profiles, authored millimetre 3MF, Manjaro Linux host. No printer upload or start.

## Observations

1. Supplying a directory that had already been created by `mktemp -d` produced the required fail-closed result `fresh-output-directory: FAIL`. This matches the documented adapter contract; the correct pattern is a fresh temporary parent plus a not-yet-created child output path.
2. With a fresh child output path but a repository-relative 3MF path, wrapper existence and hashing checks passed, then the native slicer returned `return_code=-3` and `The input files to the slicer are not found.` The native invocation retained the relative path while running from an isolated directory.
3. Repeating the same slice with the absolute 3MF path and another fresh child output path returned exit 0, native success, one analyzed G-code file, 180 layers, one tool, no tool changes and no warnings. The exact successful report is `validation/slicer-anycubic-next.json`.
4. All temporary output parents were removed after their run. No G-code was retained in the workspace.

Interpretation: observation 1 is intended fail-closed behavior. Observation 2 reproduces the relative-source-path regression already recorded by EXP-00003; it is not evidence of a CAD or 3MF defect. Resolution of all slicer input/profile paths before entering the isolated subprocess remains an open adapter requirement.
