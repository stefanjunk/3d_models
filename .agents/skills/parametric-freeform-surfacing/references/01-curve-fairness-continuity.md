# Curve fairness and continuity

## Continuity is necessary but not sufficient

Use geometric continuity terms consistently:

- **G0** — curves or surfaces meet positionally.
- **G1** — tangent directions align; the join has no visible tangent kink.
- **G2** — curvature vectors align to the tolerance supported by the CAD system; highlight flow is normally much calmer.
- **G3** — the rate of curvature change is also controlled; reserve it for dominant premium lines where the tool and evidence justify it.

A single cubic B-spline span can be mathematically smooth and still look poor because curvature oscillates. The target is therefore **fairness**, not only continuity.

## Practical fairness indicators

For an arc-length parameterized curve \(C(s)\), useful energies include:

\[
E_\kappa = \int \kappa(s)^2\,ds
\]

and a stronger variation penalty:

\[
E_v = \int \left(\frac{d\kappa}{ds}\right)^2\,ds.
\]

A fitted design can minimize:

\[
E = w_f E_{fit} + w_\kappa E_\kappa + w_v E_v + w_h E_{hardpoints}.
\]

Do not interpret the smallest possible energy as automatically attractive. End conditions, silhouette intent, packaging space, and product character remain explicit constraints.

## Control-point discipline

- Start with semantic stations, not uniform point density.
- Use roughly four to eight controls for a major 2D silhouette segment before adding more.
- Add controls where a real design event occurs: heel-to-waist transition, ball region, wheel arch, beltline break, bowl rim flare.
- Avoid alternating short/long control polygon segments.
- Avoid multiple controls that make the same tiny local correction.
- Prefer approximation or regularized fitting for scans and AI meshes.
- Preserve end position and tangent when the curve meets a hard interface.

## Curvature graph review

For every dominant guide curve:

1. Resample approximately by arc length.
2. Plot or report signed curvature.
3. Count local extrema above a scale-appropriate noise threshold.
4. Investigate isolated spikes, sign flips, and high-frequency oscillation.
5. Compare parameter variants using the same sampling and scale.

The helper `analyze_curve.py` reports discrete curvature, RMS curvature, total curvature variation, and extrema count. It is a screening tool, not a replacement for a CAD system's exact curvature comb.

## Fairing methods

### Regularized spline/point fairing

Use when the input is noisy but the overall path is correct. The supplied helper solves a discrete least-squares problem that balances point fidelity against second-difference energy. Preserve endpoints when they are interfaces.

### Fourier fairing for closed outlines

Use for periodic outlines such as bowl rims or closed planforms. Retaining only low harmonics removes high-frequency noise while preserving broad lobes. Align the seam only for storage; the mathematics remains periodic.

### Clothoid or curvature-law design

Use where curvature should ramp deliberately, such as a vehicle roofline, shoe side silhouette, or transition from a straight datum. A clothoid has curvature approximately linear in arc length. Log-aesthetic curves provide other controlled curvature laws. These are design primitives, not mandatory replacements for B-splines.

## Visual review

At minimum inspect:

- orthographic silhouettes without perspective;
- reflected-line or zebra analysis where the backend supports it;
- curvature combs on guide curves;
- section cuts through high-curvature regions;
- neutral lighting without texture or material noise.

Smooth shading can hide faceting and does not prove fair geometry.
