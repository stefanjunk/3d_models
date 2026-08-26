# SubD, free-form deformation, and morph targets

## Subdivision surfaces

A SubD surface uses a sparse control cage and a refinement rule such as Catmull-Clark. It is effective for shoes, vehicle bodies, furniture, ergonomic shells, and other shapes whose broad form matters more than exact per-face dimensions.

### Good SubD practice

- use mostly quads with predictable edge flow;
- place loops along real feature lines, not uniformly everywhere;
- keep poles away from dominant highlights and tight corners;
- use creases only for intentional sharpness;
- preserve symmetry through construction, not manual vertex matching;
- validate the evaluated surface, not only the control cage.

SubD is an aesthetic-envelope representation. Place exact holes, sockets, and mating faces in the functional CAD layer or regenerate them after conversion.

## Free-form deformation (FFD)

FFD embeds geometry in a lattice and moves the lattice's control points. A trivariate Bernstein form is:

\[
P'(s,t,u)=\sum_{i=0}^{l}\sum_{j=0}^{m}\sum_{k=0}^{n}
B_i^l(s)B_j^m(t)B_k^n(u)P_{ijk}.
\]

It is especially useful when a good master already exists.

### Semantic FFD parameters

Map user terms to coordinated cage moves:

- shoe: toe width, waist, heel cup, rocker, toe spring, lip sweep;
- bowl: rim flare, belly fullness, ovality, twist;
- RC body: roof height, cabin position, shoulder width, nose tension, tail taper.

Do not expose every lattice point as a user parameter. Build a smaller semantic parameter map.

### Protected regions

Use one or more of:

- fixed cage points;
- spatial masks/falloffs;
- protected bounding volumes;
- landmark constraints;
- post-deformation reconstruction of exact interfaces.

The supplied `ffd_deform.py` supports fixed boxes with falloff. For production, compare hardpoints before and after and rebuild exact geometry.

## Morph targets / shape keys

Morph targets are ideal when multiple artist-approved masters share identical topology. A variant is

\[
V(p)=V_0+\sum_i \alpha_i(p)(V_i-V_0).
\]

Advantages:

- predictable style families;
- fast evaluation;
- direct art direction;
- easy limits on extreme combinations.

Risks:

- self-intersection between target combinations;
- shrinking wall thickness;
- drift of interfaces;
- poor extrapolation outside the authored range;
- topology lock-in.

Run a parameter-grid regression test and hardpoint/wall checks for all exposed combinations.

## AI/scan masters

Before FFD or morph authoring:

1. preserve the source;
2. establish scale, axes, and landmarks;
3. repair only what is necessary;
4. retopologize to a stable quad cage when SubD/morphs are required;
5. separate visual shell from exact functional parts;
6. store the fitting/deformation transform and residual error.
