# 3D Learning Architecture v1

**Version:** 1.0.0

**Status:** operational repository standard

**Date:** 2026-08-27

**Scope:** functional 3D design, FFF/FDM process development, CAD/mesh
validation, slicer settings, physical tests, and user corrections

## 1. Purpose

This system lets the repository improve from real design and print work without
turning one core skill into a growing, contradictory handbook. Its central rule
is:

> Do not learn directly from success or failure. Learn from scoped, validated
> explanations of success or failure.

A single result is an observation. It can inform the next experiment, but it is
not automatically a reusable rule. Reuse increases only after the observation,
scope, proposed mechanism, counterexamples, and acceptance tests have been
recorded and reviewed.

The architecture follows four evidence-backed ideas:

1. Keep skills procedural and load detailed resources progressively. Agent
   Skills exposes metadata first, the core instructions second, and optional
   resources only when required; executable code is appropriate for
   deterministic work ([Anthropic: Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills),
   [Agent Skills specification](https://agentskills.io/specification)).
2. Convert structured production traces and expert corrections into focused
   evals before implementing durable changes, then run targeted and regression
   checks ([OpenAI: self-improving agents](https://openai.com/index/building-self-improving-tax-agents-with-codex/)).
3. Preserve AM context. NIST's DfAM ontology separates design features, design
   parameters, process parameters, and material parameters so that knowledge can
   be retrieved within the conditions that make it applicable
   ([NIST DfAM ontology](https://www.nist.gov/publications/design-additive-manufacturing-ontology-support-manufacturability-analysis)).
4. Treat lessons as a lifecycle of collection, recording, dissemination, and
   application rather than as chat summaries
   ([NASA Lessons Learned](https://www.nasa.gov/learning-resources/for-professionals/appel-lessons-learned/)).

The need for strict scope is empirical, not merely organizational. A systematic
review of 127 material-extrusion parameter studies found inconsistent methods,
setup-specific results, and limited generalizability across machines, materials,
artifacts, and parameters
([Golab, Massey & Moultrie 2022](https://doi.org/10.1016/j.heliyon.2022.e11592)).

## 2. Non-goals

Version 1 does not:

- fine-tune a model or change model weights;
- use a vector database;
- infer universal material constants from local prints;
- automatically modify production skills;
- automatically promote candidates;
- replace raw product evidence with summaries;
- claim certification from local validation;
- upload files to a printer or start a print.

The Markdown and YAML files are the source of truth. A future SQLite or vector
index may accelerate retrieval, but it must be rebuildable from these files.

## 3. Architecture

```text
small procedural skill
        │
        ├── just-in-time knowledge and process references
        ├── scoped validated patterns
        ├── top-ranked relevant experiences
        └── applicable evals and deterministic scripts
                         │
                         ▼
                  design / print / test
                         │
                         ▼
                 immutable project trace
                         │
                         ▼
             reflection + lesson candidate
                         │
             duplicate / conflict analysis
                         │
                         ▼
                targeted eval + evidence
                         │
                         ▼
               promotion review E0–E4
                         │
              targeted + regression pass
                         │
                         ▼
              reference / pattern / skill
```

The repository implementation is:

```text
libraries/3d-learning/
├── 3D-LEARNING-ARCHITECTURE.md
├── VERSION
├── CHANGELOG.md
├── knowledge/
│   ├── processes/
│   ├── materials/
│   ├── printers/
│   ├── nozzles/
│   ├── slicers/
│   ├── dfam/
│   └── components/
├── patterns/
│   ├── mounting/
│   ├── lightweight/
│   ├── airflow/
│   ├── mechanics/
│   └── enclosures/
├── experience/
│   ├── raw/
│   ├── candidates/
│   ├── validated/
│   └── rejected/
├── evals/
│   ├── core/
│   ├── geometry/
│   ├── dfam/
│   ├── interfaces/
│   ├── visual/
│   └── regression/
├── benchmarks/
│   ├── models/
│   └── measurements/
├── schemas/
└── templates/

.agents/skills/3d-skill-maintainer/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/learning_records.py
```

Product-specific raw evidence remains under its owning `products/...` folder.
This prevents a shared library from becoming a hidden runtime dependency of a
product and preserves the repository containment rule.

## 4. Six kinds of knowledge

| Store | Question | Allowed content | Not allowed |
|---|---|---|---|
| Skills | How do I work? | short procedures, gates, routing | material tables, print anecdotes |
| Knowledge | What is known? | sourced facts, machine/profile identity, DfAM references | unsourced local assumptions |
| Patterns | What solution structure has worked? | intent, parameters, failure modes, variants, linked evals | one-off untested geometry |
| Experience | What was observed? | scoped success/failure, evidence, explanation state | universal claims without promotion |
| Evals | What outcome is expected? | inputs, success criteria, graders, fixtures | vague advice with no verdict |
| Benchmarks | What can this process do? | coupon source, exact process, measurements | measurements without method or scope |

Scripts contain deterministic mechanics: schema validation, ID checks, scope
filtering, ranking, mesh inspection, dimensional comparison, and report
generation. They do not decide whether an engineering explanation is true.

Separating reusable patterns from the core procedure also follows the useful
idea of a composable skill library in
[Voyager](https://arxiv.org/abs/2305.16291); storing raw observations separately
from higher-level reflections and retrieving them dynamically parallels the
memory architecture described for
[Generative Agents](https://arxiv.org/abs/2304.03442). These are architectural
analogies only—the engineering claims in this repository still require physical
and deterministic evidence.

## 5. Source-of-truth and provenance rules

Every learning record must link to its source evidence instead of copying an
unverifiable conclusion. Depending on the record this includes:

- product and part revision;
- source commit and artifact hash where practical;
- printer, firmware, slicer, profile name and profile hash;
- exact material manufacturer, product, variant, color, and batch/lot when
  available;
- nozzle diameter, material, geometry, wear state, and hotend;
- orientation, layer height, line width, cooling, speed, volumetric limit, and
  conditioning;
- geometry class and critical parameters;
- measurement instrument, method, resolution, uncertainty, and environment;
- pass/fail criteria, raw result, failure mode, photos, and reports;
- authoring agent/human and review status.

For supplier data, authority is resolved from most exact to least exact:

1. label or datasheet for the exact physical product/batch;
2. exact product/color supplier document contemporaneous with the roll;
3. exact product family document;
4. generic material guidance.

Conflicting sources are recorded; they are not averaged silently. The first
candidate demonstrates this with a SUNLU PLA+ Silver roll labeled 195–220 °C.

## 6. Record lifecycle

### 6.1 Raw trace

The raw trace captures what happened from requirement through final evidence.
It is append-only evidence owned by a product folder. The shared
`experience/raw/` location is reserved for normalized trace manifests that link
to those product artifacts; it must not duplicate large files.

A trace includes the initial requirement, inputs, assumptions, coordinate
frame, design parameters, generated outputs, validation events, user feedback,
print settings, measurements, revisions, and final accepted state.

### 6.2 Candidate

A reflection creates a candidate, never a rule. The candidate separates:

- observation: what changed or was measured;
- explanation: why it may have happened;
- alternatives: other plausible causes;
- applicability: when the explanation should be considered;
- exclusions: where it must not be transferred;
- evidence: how much, of what type, and where it lives;
- evals: how the failure or behavior becomes reproducible.

Candidates live in `experience/candidates/` and are omitted from default
production retrieval. An agent may request them explicitly for experiment
planning, always labeled as unvalidated.

### 6.3 Validated

A validated lesson has passed the gate for its stated maturity level and human
review. Validation is local to the recorded scope. `validated` does not mean
certified, universally safe, or applicable to another printer/material/nozzle.

### 6.4 Rejected or deprecated

Rejected candidates remain searchable as negative knowledge. A rejection must
state whether the cause was false explanation, insufficient evidence,
duplication, unsafe recommendation, supersession, or scope ambiguity. A
previously validated record that no longer applies retains its ID and links to
the replacement.

## 7. Maturity model E0–E4

Maturity describes evidence breadth; confidence describes belief within the
stated scope. They are independent.

| Level | Meaning | Minimum gate |
|---|---|---|
| E0 Observation | observed once | one trace, explicit scope, observation separated from explanation |
| E1 Repeated | repeated under equivalent conditions | at least two same-scope observations and repeat count ≥2 |
| E2 Generalized | repeated on different geometries | E1 plus at least two geometry instances |
| E3 Cross-context | tested across relevant contexts | E2 plus variation in at least two of machine, material, or nozzle dimensions |
| E4 Validated Rule | strong reusable rule | validated explanation, measured evidence, linked eval, targeted pass, regression pass, approved human review |

Additional rules:

- A literature source can strengthen an explanation but does not turn a local
  process result into E3 by itself.
- Multiple prints from one G-code file are repetitions, not multiple
  geometries.
- A nozzle material change is a context change only if the exact nozzle identity
  and test conditions are recorded.
- E4 must state both its trigger and its exclusions.
- Safety-critical claims require the review policy of the applicable design
  skill; E4 is not a substitute for certification.

The validator enforces the measurable parts of these gates. Human engineering
review remains responsible for causal validity and risk.

## 8. Learning loop

```text
DESIGN
  → PRINT / TEST
  → USER FEEDBACK + MEASUREMENTS
  → TRACE
  → REFLECTION
  → LESSON CANDIDATE
  → DUPLICATE / CONFLICT CHECK
  → VALIDATE EXPLANATION
  → ADD TARGETED EVAL
  → PROPOSE REFERENCE / PATTERN / SKILL CHANGE
  → RUN TARGETED + REGRESSION SUITES
  → HUMAN REVIEW
  → RELEASE
```

### Step 1: capture

Link the raw source and preserve the original expected and actual values. For a
user correction, record what the system proposed, what the user corrected, and
what was finally accepted. OpenAI describes this full-path provenance as the
signal that makes production feedback actionable rather than ambiguous.

### Step 2: reflect

Write a short causal hypothesis. List at least one alternative explanation when
the mechanism has not been isolated. Reflection creates reusable language but
does not change model weights, similar to episodic verbal feedback in
[Reflexion](https://arxiv.org/abs/2303.11366). Iterative feedback can improve the
current artifact, but the revised artifact still needs independent validation
([Self-Refine](https://arxiv.org/abs/2303.17651)).

### Step 3: derive an eval

Every actionable correction creates or links an eval in the same phase. The
eval encodes the general failure condition, not an accidental local answer.

Example:

```text
Correction: mounting holes were mirrored.
Bad lesson: holes always belong on the right.
Useful eval: directions tied to a machine must be resolved against an explicit
object coordinate frame and reference view before export.
```

### Step 4: check duplicate and conflict

Search exact metadata first. Compare candidates with the same feature, process,
machine/material/nozzle scope, and decision parameter. Mark:

- `duplicates`: same lesson/evidence;
- `conflicts`: incompatible results in overlapping scope;
- `supersedes`: reviewed replacement;
- `related`: useful but not equivalent.

A conflict blocks promotion until resolved, narrowed, or explicitly accepted by
human review.

### Step 5: validate explanation

Prefer a minimal controlled test that distinguishes the proposed mechanism from
alternatives. Keep all other relevant parameters fixed. Record failures as
evidence rather than deleting them.

### Step 6: promote knowledge

Run `promotion-check`. A passing check is necessary but insufficient. Human
review approves the maturity level and, if needed, a proposed patch to a
reference, pattern, or skill.

### Step 7: regress and release

Run both the targeted eval and the relevant regression suite. Capability evals
show what a system can newly do; regression evals protect what already worked
([Anthropic eval guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).
Version the changed artifact and record reason, evidence IDs, eval IDs, and
results in the changelog.

## 9. Eval model

An eval is a versioned test case with:

- stable ID and category;
- trigger and risk;
- given inputs, fixtures, and scope;
- explicit expected outcome;
- explicit failure conditions;
- grader type: deterministic, visual rubric, physical/manual, or hybrid;
- command and expected exit code where deterministic;
- links to originating lessons and regression suites;
- last run, result, report, and artifact hashes.

### 9.1 Geometry evals

- watertight/manifold;
- no unexpected self-intersections or floating bodies;
- minimum wall and feature thickness;
- bounding box and bed fit;
- critical diameter, spacing, radius, and datum checks;
- body overlap and clearance.

### 9.2 DfAM evals

- unsupported overhang area;
- bridging spans;
- inaccessible or trapped support;
- bed contact and stability;
- horizontal-hole risk;
- trapped volumes;
- support/material/time metrics.

### 9.3 Interface evals

Interfaces use named datums and explicit coordinates:

```text
bolt_center_distance == 42.00 ± tolerance
mounting_side == physical_machine_right
fan_clearance_mm >= 2.0
connector_access == unobstructed
```

### 9.4 Visual evals

Visual checks use fixed cameras, lighting, model revision, and a rubric. They
cover symmetry, continuity, surface artifacts, logo completeness, relief
quality, and comparison to approved references. A render cannot replace
geometry or physical validation.

### 9.5 Physical print evals

- nominal versus measured dimensions and uncertainty;
- fit classification;
- mass and print time;
- support use;
- cycles, deflection, or breaking load;
- surface quality and environmental exposure.

Use deterministic graders where the outcome is numeric or topological and human
review where appearance, touch, or causality is material.

## 10. Benchmark coupons

Standardized coupons make process changes comparable. NIST's AM test artifact
work links measured feature errors to machine/process capabilities and uses
repeat builds for characterization and improvement
([NIST AM test artifact](https://www.nist.gov/publications/additive-manufacturing-test-artifact)).

Initial benchmark families are:

```text
dimensional: xyz, round holes, horizontal holes
fit: clearance comb, shaft/hole, dovetail, snap-fit
dfam: overhang, bridge, thin wall, unsupported hole
structural: ribs, flexures, layer adhesion
surface: curved surface, top surface, ironing
```

Coupon source belongs in `benchmarks/models/`; measurements use the benchmark
schema in `benchmarks/measurements/`. A result without exact coupon revision,
process scope, method, and raw evidence is invalid.

## 11. Parametric design intent

Store more than the final STL. Feature history, named parameters, constraints,
datums, construction method, and critical relationships make a result reusable.
NIST notes that pure shape exchange omits this design intent
([NIST CAD design intent](https://www.nist.gov/publications/standardized-data-exchange-cad-models-design-intent)).

A trace should therefore preserve expressions such as:

```text
wall_thickness_mm = max(3 × extrusion_width_mm, structural_minimum_mm)
```

instead of recording only `wall = 1.8 mm`. A future executable rule may expose
this as a function, but its return value must include recommendation, observed
minimum, confidence, scope, and evidence links. Modular, machine-readable AM
rules are consistent with NIST's work on composable design-rule elements
([NIST modular AM rules](https://www.nist.gov/publications/design-rules-modularity-additive-manufacturing)).

## 12. Just-in-time retrieval

Do not load the full library. Anthropic recommends the smallest high-signal
context and just-in-time retrieval through lightweight identifiers and targeted
queries ([Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

Retrieval has two phases.

### Phase A: mandatory metadata filtering

Filter, when specified, by:

```text
process
machine
material manufacturer/product/variant/color/batch
nozzle diameter/material/geometry/hotend
feature type
orientation
slicer/profile
geometry class
environment
```

A specified filter is fail-closed: a missing or different record value does not
match. This prevents a semantically similar TPU or different-printer experience
from outranking the actual material/process scope.

### Phase B: ranking

Rank surviving records in this order:

1. number and specificity of scope matches;
2. feature match;
3. maturity and evidence level;
4. token/text similarity in version 1;
5. recency as a small tie-breaker.

Return three to five records by default. Validated lessons are included;
candidates require `--include-candidates` and must be labeled. A future
embedding layer may replace token overlap only after metadata filtering.

## 13. Maintainer responsibilities and authority

The `3d-skill-maintainer` is a curator, not the production designer. It receives
requirements, revisions, feedback, validation reports, measurements, failures,
and the accepted artifact. It may produce:

1. lesson candidates;
2. pattern candidates;
3. targeted evals;
4. duplicate/conflict reports;
5. proposed reference/skill patches;
6. promotion-readiness reports.

It may not:

- silently edit a production skill because one print succeeded;
- mark human review as approved;
- move a record to `validated` without an approved promotion;
- discard negative evidence;
- weaken an eval to make a patch pass;
- expand a lesson beyond its evidence scope;
- treat local qualification as certification.

## 14. Skill and knowledge versioning

Use semantic versions for the learning system and individual production skills.
A production change records:

```yaml
change: Added explicit coordinate-frame validation.
reason: Three recurring mounting-orientation failures.
evidence: [EXP-00038, EXP-00094, EXP-00117]
evals: [EVAL-interface-handedness-001]
targeted_result: pass
regression_result: pass
approved_by: human identifier
```

- Patch: wording, metadata, or validator correction without behavior change.
- Minor: new compatible rule, pattern, eval, or workflow gate.
- Major: changed semantics, schema, promotion policy, or incompatible interface.

Every schema carries `schema_version`. Migration scripts must preserve old
records or fail with an actionable error; they must never silently reinterpret
fields.

## 15. Operational commands

Validate the full active store:

```bash
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py validate
```

Audit duplicate IDs, unresolved conflicts, path/state mismatches, and missing
correction evals:

```bash
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py audit
```

Retrieve scoped context:

```bash
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py retrieve \
  --process FFF --material PETG --nozzle 0.6 --feature press-fit --limit 5
```

Check whether a candidate meets a requested maturity gate:

```bash
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py \
  promotion-check libraries/3d-learning/experience/candidates/EXP-00001.yaml \
  --target E1
```

The command reports readiness only. Promotion still requires reviewed edits,
targeted/regression results, a changelog, commit, and push.

## 16. First implemented correction

The repository's first candidate comes from the correction that the exact SUNLU
PLA+ Silver roll is labeled 195–220 °C. The lesson is not “SUNLU PLA+ always
prints at one temperature.” It is:

```text
When exact physical-roll identification conflicts with a broader/current
product-family source, constrain the profile to the exact roll's documented
range and record the conflict. Do not apply a generic nozzle-temperature offset
beyond that ceiling; reduce flow and validate instead.
```

The candidate remains E0 until repeat process evidence exists. Its linked eval
checks that a 195–220 °C roll cannot yield a proposed profile above 220 °C and
that `PLA+`, `High Speed PLA+`, and `PLA+ 2.0` are not conflated.

## 17. Rollout plan

### Stage 1 — implemented now

- Git-backed Markdown/YAML source of truth;
- schemas, templates, maturity gates, audit, retrieval, and promotion check;
- lean maintainer skill;
- correction-derived candidate/eval;
- integration with workspace and functional-design instructions.

### Stage 2 — after sufficient records

- generated SQLite/JSON index;
- metadata filter plus embedding ranking;
- dashboards for conflicts, coverage, and eval status;
- more deterministic CAD/mesh/interface graders.

The index remains disposable and rebuildable.

### Stage 3 — after statistically useful measurements

- controlled analysis of printer/material/nozzle/geometry/slicer interactions;
- uncertainty estimates and predictive functions;
- feed-forward recommendations with evidence ranges;
- periodic calibration drift detection.

NIST's data-driven AM program similarly emphasizes incorporating process,
material, measurement, and prior knowledge into design/process decisions while
managing uncertainty
([NIST data-driven AM decision support](https://www.nist.gov/programs-projects/data-driven-decision-support-additive-manufacturing)).

## 18. Definition of done for a learning phase

A learning phase is complete only when:

- raw evidence is preserved in the owning product/research location;
- each meaningful correction or failure has a scoped candidate or rejection;
- actionable user corrections link to an eval;
- candidates pass schema validation;
- duplicates and conflicts are documented;
- claims do not exceed maturity or confidence;
- targeted and regression results are present for promoted changes;
- production-skill changes, if any, have human approval and version metadata;
- `learning_records.py validate` and `audit` pass;
- unrelated worktree files were not staged;
- the phase was committed and pushed according to `AGENTS.md`.

The intended long-term result is a small core workflow plus many focused,
retrievable artifacts—not one ever-growing 3D design prompt.
