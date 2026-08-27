# Optimization plan and comparison

## Frozen baseline

- Model identity: conservative shell candidate A, generated from the same `0.1.0-draft.1` source.
- Geometry: 3.0 mm walls, 3.0 mm floors, unchanged reinforced receivers and connector.
- Process hypothesis: 0.4 mm nozzle, 0.45 mm line width, 0.20 mm layer height, PLA, bottom-down.
- Exact slicer/version/profile/time/support metrics: `NOT_RUN` because no supported slicer CLI or destination profile is installed.

## Protected regions

The floor containment skin, top hand rim, four receiver bosses, socket roofs, connector datum, desk-contact plane, interface keep-outs and 1.0 mm receiver-face gap are immutable across candidates.

## Candidates

| Candidate | Lever | Status |
|---|---|---|
| A | Process-only reference on conservative 3.0/3.0 mm shell | retained baseline; not sliced |
| B | Separate 2.4 mm ordinary walls/floor with local receiver reinforcement | selected digital geometry |
| C | B plus 0.6 mm nozzle process hypothesis | not selected without exact slicing |

Candidate B reduces analytic CAD volume by about 18.2% against A while keeping every protected region. This is not a deposited-material or print-time claim. The socket roof's maximum nominal bridge span is 14.6 mm; a process-matched coupon remains mandatory.
