# 3D Learning Library

This is the repository-wide source of truth for evidence-gated learning from 3D
design, FFF/FDM printing, validation, and user feedback. It keeps procedural
skills small while making scoped knowledge, patterns, observations, evals, and
benchmark measurements retrievable on demand.

Read [3D-LEARNING-ARCHITECTURE.md](3D-LEARNING-ARCHITECTURE.md) for the complete
architecture, schemas, maturity model, promotion policy, retrieval order,
workflow, examples, and governance.

Quick validation:

```bash
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py validate
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py audit
```

Scoped retrieval example:

```bash
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py retrieve \
  --process FFF \
  --machine "Anycubic Kobra 3 Max" \
  --material "SUNLU PLA+ Silver" \
  --feature filament-profile \
  --query "temperature label authority" \
  --include-candidates
```

Candidate records are never production rules. Promotion remains a reviewed,
eval-backed operation.
