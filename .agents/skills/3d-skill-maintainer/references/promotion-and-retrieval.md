# Promotion and retrieval

## Promotion gates

- E0: at least one observation with explicit scope.
- E1: at least two observations and two equivalent-scope repetitions.
- E2: E1 plus at least two geometry instances.
- E3: E2 plus variation in at least two of machine, material, or nozzle.
- E4: E3 plus measured evidence, validated explanation, linked eval, targeted
  pass, regression pass, and approved human review.

A validated lifecycle state always needs approved human review. Unresolved
conflicts block validation. A passing script report cannot approve causal
reasoning.

## Retrieval order

1. Hard-filter requested process, machine, material, nozzle, feature, and tag.
2. Rank exact scope coverage.
3. Rank feature match.
4. Rank maturity/evidence.
5. Rank token overlap for the free-text query.
6. Use recency only as a small tie-breaker.

Candidates are excluded by default. A record with a missing value does not match
an explicitly requested filter. This fail-closed behavior prevents a similar but
wrong material/printer lesson from entering working context.

## Durable-change routing

- Change a skill only for stable procedure.
- Change knowledge for sourced facts.
- Add a pattern for a reusable parametric solution with evidence and evals.
- Keep an experience when transfer remains narrow or uncertain.
- Add an eval whenever expected behavior becomes testable.
- Put numeric/topological logic in a script rather than repeating prose.
