# Self-learning and reusable intervention library

Do not let an agent silently rewrite its engineering rules after one successful render. Learn through versioned evidence.

## Record each operation

Store:

- source mesh hash and metrics;
- operation-plan hash;
- tool and version;
- transform and landmarks;
- cutter/insert parameters;
- proxy, decimation, repair, Boolean, and voxel settings;
- topology/protected-surface/section results;
- slicer profile and print orientation;
- physical test result and failure mode;
- photos or measurement files by path;
- final disposition: rejected, experimental, validated, or promoted.

Use `record_operation_result.py` to append a project-local JSONL history.

## Promote reusable patterns only when

- source/license provenance permits reuse;
- parameters and coordinate conventions are documented;
- automated validation passes;
- at least one physical test relevant to the pattern passes;
- known failure ranges and minimum printable features are recorded;
- the pattern is generic rather than overfitted to one mesh.

Good reusable patterns include rounded compartment doors, conformal flange workflows, axial tower-core cutters, captured baffle inserts, sole-interface bands, and test coupons. Do not promote the user's decorative source mesh into a public library without permission.

## Learn from failures

Record failures as first-class data:

- Boolean engine and error;
- invalid operand condition;
- coplanar/tangent configuration;
- memory peak or allocation estimate;
- protected-surface breach;
- thin-wall/sliver location;
- slicer artifact;
- physical delamination, jamming, cracking, or poor fit.

Use failure records to add stop conditions and regression tests, not to merely increase Boolean tolerances.

## Updating the skill

Proposed skill changes should arrive as reviewed patches with:

1. evidence record(s);
2. changed reference/rule;
3. a deterministic test or example reproducing the issue;
4. compatibility notes;
5. changelog entry.
