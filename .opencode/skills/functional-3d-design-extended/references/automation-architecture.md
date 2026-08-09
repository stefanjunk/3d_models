# Automation architecture for an LLM-driven 3D design system

## Recommended roles

Use one accountable primary agent and several bounded workers rather than a single unconstrained code generator.

| Role | Responsibility | Appropriate model class |
|---|---|---|
| design lead | requirements, architecture, risks, trade-offs, final acceptance | capable/frontier |
| CAD microtask | small parameterized feature, source edit, export fix | fast coding model |
| research scout | upstream docs, library/API/version/license lookup | fast general/research model |
| geometry reviewer | dimensions, body count, interference, design-rule checks | medium/capable coding |
| simulation planner | model fidelity, loads, constraints, uncertainty | capable/frontier |
| librarian | component metadata, test evidence, deprecation | fast structured-data model |

The design lead remains responsible for decisions. A worker returns evidence and a recommendation, not silent approval.

## Bounded subagent contract

Every delegated task should state:

```yaml
objective: one measurable result
inputs: explicit files and parameters
allowed_changes: named files or read-only
forbidden_decisions: safety/load/material assumptions
acceptance_command: deterministic command to run
output_schema: json-or-short-markdown
budget: time-or-tool-call bound
```

Good fast-agent tasks:

- add one parameter and one assertion;
- search the local parts library for an M4 insert;
- calculate a gear center distance;
- classify tool/material/nozzle options;
- run mesh validation and summarize failed checks;
- update a README from already verified results.

Poor fast-agent tasks:

- design the complete product from an ambiguous prompt;
- choose an unverified wall load;
- define nonlinear FEM contact and approve the result;
- refactor several CAD representations without a regression test.

## Tool boundary

Use MCPs and local commands as execution mechanisms, not as sources of engineering truth.

```text
OpenCode skill           tells the agent how to decide
CAD/MCP/CLI              executes, renders, measures, exports
validator scripts        produce machine-readable checks
slicer/simulation tools  estimate manufacturing/behavior
physical tests           resolve process and service uncertainty
```

High-risk capabilities such as arbitrary Python, shell access, external file access, and printer control should be permission-scoped. Automatic printer start is outside this package's default flow.

## Reference pipeline

```text
request
  -> design-spec.yaml
  -> decomposition + print-vs-buy + BOM
  -> tool route
  -> calibration gaps/coupons
  -> source CAD/mesh code
  -> source unit tests
  -> STEP/3MF/STL export
  -> geometry checks
  -> slicer dry-run and layer inspection
  -> useful calculation/simulation
  -> coupon/subassembly/full prototype
  -> measured test record
  -> revision or local qualification
```

## CI-friendly checks

A repository pipeline can run:

1. YAML/JSON/schema and Python syntax checks;
2. source generation with small and default parameter sets;
3. STEP/STL export;
4. body count, bounds, volume, watertightness, and bed-fit checks;
5. geometric metric regression against approved limits;
6. slicer CLI dry-run for selected printer profiles;
7. package manifest and checksum generation.

Do not make pixel similarity the only CAD regression test. Compare dimensions, volume, critical interface samples, body count, and a visual render.

## Suggested OpenCode routing

- `/design-3d`: primary session, loads the skill and creates the design contract.
- `/cad-microtask`: child session for a bounded edit/calculation.
- `/review-3d`: independent reviewer with read-oriented permissions.
- `/learn-part`: librarian flow for evidence-backed reuse.

The supplied agent files inherit the configured provider model. A separate example pins `openai/gpt-5.3-codex-spark` for short coding tasks when available.
