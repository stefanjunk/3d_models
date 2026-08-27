# Experience store

- `raw/`: normalized manifests that link to immutable product traces.
- `candidates/`: unvalidated observations and causal hypotheses.
- `validated/`: human-approved records that meet their E0–E4 gate.
- `rejected/`: preserved negative, duplicate, unsafe, or superseded findings.

Do not move records between states without review. The path and
`lifecycle.state` must agree.
