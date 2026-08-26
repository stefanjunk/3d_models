# Interface contracts and parametric counterparts

## Contents

1. [Make the interface a first-class artifact](#1-make-the-interface-a-first-class-artifact)
2. [Use coordinate-frame discipline](#2-use-coordinate-frame-discipline)
3. [Assign single ownership](#3-assign-single-ownership)
4. [Record the complete contract](#4-record-the-complete-contract)
5. [Separate allowance terms](#5-separate-allowance-terms)
6. [Create an interface kit](#6-create-an-interface-kit)
7. [Design parametric counterparts](#7-design-parametric-counterparts)
8. [Choose seam and retention patterns](#8-choose-seam-and-retention-patterns)
9. [Handle curved and flexible interfaces](#9-handle-curved-and-flexible-interfaces)
10. [Handle fused and multi-material bodies](#10-handle-fused-and-multi-material-bodies)
11. [Verify the contract](#11-verify-the-contract)

## 1. Make the interface a first-class artifact

An interface is more than the contact surface. It includes:

- geometric datums and permitted transforms;
- contact, clearance, overlap, and keep-out volumes;
- transmitted load, motion, air/fluid, light, heat, or electrical connection;
- assembly direction, lead-in, tool/finger access, and removal path;
- material/process pairing and surface condition;
- inspection method and acceptance limit;
- revision owner.

Create the interface before high-detail organic modeling. If a design cannot express its interfaces without the final ornament, the architecture is not ready.

## 2. Use coordinate-frame discipline

### 2.1 Global frame

Define:

- right-handed axes and units;
- origin tied to a stable functional datum, not a decorative extremum;
- forward/up/right meanings;
- master assembly envelope;
- transform convention: row/column order and whether transforms map source-to-project or project-to-source.

Use millimetres for printable geometry unless the project explicitly requires otherwise. STL has no reliable unit field; record scale outside the file.

### 2.2 Local interface frame

For every interface define:

- origin on the nominal seat/axis/plane;
- `+Z` or another named normal/assembly direction;
- in-plane orientation preventing accidental 180° rotation;
- three or more non-collinear landmarks when surface registration is needed;
- a saved 4×4 rigid transform.

Avoid bounding-box alignment as the final method. Symmetry and decorative mass can make PCA/bounds choose the wrong orientation.

### 2.3 Stable landmarks

Prefer, in order:

1. holes, pins, axes, or planar datums from the parametric core;
2. deliberately added registration bosses/notches in the seam band;
3. fitted cylinders/planes or section centroids;
4. visible organic landmarks that are repeatable across candidates;
5. PCA or bounding box only as an initial guess.

## 3. Assign single ownership

Each nominal interface dimension has one owner. Common ownership policy:

- parametric core owns mounting, fit, motion, seals, walls, assembly access, and keep-outs;
- organic master owns visible silhouette and surface detail outside the seam/edit band;
- manufacturing profile owns measured process compensation;
- assembly plan owns joining method and order.

The non-owner receives derived bodies or parameters. Do not independently type the same width/radius into two source files.

If two components must vary independently, place the shared contract in a third parametric skeleton/master and derive both sides from it.

## 4. Record the complete contract

At minimum include:

```text
interface_id
component_a / component_b
nominal_owner
local_frame and saved transform
interface type and nominal geometry
assembly direction and allowable degrees of freedom
load/motion/environment
joining/retention method
lead-in and anti-rotation
seam/edit band
protected regions and keep-outs
minimum wall/ligament/edge distance
nominal tolerance
process compensation
motion clearance
adhesive gap
Boolean overlap or separation policy
registration uncertainty
inspection and physical coupon
```

Name dimensions as per-side, radial, diametral, or total. Do not write only `clearance = 0.3 mm`.

## 5. Separate allowance terms

Keep these independent:

- `C_function`: clearance required for intended movement/insertion;
- `C_process`: measured compensation for printer/material/orientation/profile;
- `C_assembly`: additional allowance for insertion angle or inaccessible alignment;
- `G_adhesive`: bond-line gap, including adhesive viscosity and surface texture;
- `O_boolean`: intentional solid overlap for a fused Boolean;
- `U_registration`: expected mesh placement/interface uncertainty;
- `E_solver`: geometric/Boolean numerical tolerance;
- `R_shell`: material reserve between interface operation and protected exterior.

Do not add every term automatically. Define the error model and signs. For a worst-case sliding fit, a conservative per-side modeled clearance may be:

```text
C_model = C_function + C_process + U_registration + C_assembly
```

For a bonded fixed insert, `G_adhesive` may replace motion clearance. For a fused mesh Boolean, use overlap rather than a positive gap.

Calibrate `C_process` with the real machine, nozzle, material, orientation, profile, and feature type. Holes, external pegs, vertical slots, and horizontal interfaces can have different errors.

### Protected-wall reserve

For a cutter or socket near a visible shell, require along critical samples:

```text
distance_to_exterior >= minimum_wall + registration_uncertainty + solver_margin
```

Add process deviation where the physical wall, not only CAD geometry, is safety-critical. Validate sections around the whole interface, not only a nearest point.

## 6. Create an interface kit

Export a small, versioned set from the parametric authority:

- `datum`: axes, origin markers, or reference planes;
- `target-envelope`: maximum organic occupancy;
- `keepout`: forbidden functional/swept volume;
- `trim-body`: cuts sacrificial organic excess to the nominal seam;
- `seat/backer`: exact parametric body attached to the product;
- `clearance-body`: pocket/cutter including selected allowance;
- `union-overlap-body`: positive-volume bridge for a fused route;
- `coupon-body`: reduced interface test geometry.

Export STEP/BRep for exact CAD reuse and a deliberately tessellated mesh for Blender/mesh tools. Include the same frame and units in every export. Keep helper bodies clearly named so they are not mistaken for printable product bodies.

When the parametric design changes, regenerate the kit rather than editing organic parts manually to match stale geometry.

## 7. Design parametric counterparts

### 7.1 Organic ornament on a structural body

Build:

1. structural body and protected load path;
2. shallow seat or bounded attachment patch;
3. backer that matches the product surface;
4. key/dowel/shoulder for location and anti-rotation;
5. optional adhesive channel, magnet pocket, screw boss, or clip;
6. generous load-spreading transition outside the visible seam;
7. trim body extending through the sacrificial root.

The organic mesh is trimmed and united to the backer, or printed separately and attached. Do not sculpt the socket into the AI mesh.

### 7.2 Organic shell over a core

Let the core own:

- inner clearance and functional envelope;
- mount points and load paths;
- minimum wall and service openings;
- alignment stops and assembly direction.

Create an exterior occupancy envelope for the shell and an interior clearance cutter derived from the core. Use discrete pads/ribs or a controlled offset rather than trusting random organic contact everywhere.

### 7.3 Organic handle/knob with engineered stem

Make the stem, axle, thread, insert pocket, anti-rotation flat, and stress fillet parametric. Extend the stem into the organic volume with positive overlap and a gradual transition. Keep the visible handle root thick enough after trimming.

### 7.4 Relief/inlay panel

Let the parametric part own:

- substrate curvature and thickness;
- boundary and no-detail margin;
- pocket depth, floor thickness, and draft/lead-in;
- panel locating features and removal access.

Let the organic/relief source own only the visible field. Clip it with the panel boundary and create a watertight back from the authoritative substrate.

### 7.5 Functional opening through ornament

Model the opening and its clearance/swept volume parametrically. Generate ornament around a keep-out envelope or subtract the opening after registration. Reinforce the edge parametrically. Never depend on an AI-generated hole for final size.

## 8. Choose seam and retention patterns

### Seam location

Prefer seams that are:

- hidden by an existing ridge, band, scale, feather, clothing line, bezel, or sidewall;
- wide enough for a flange/backer;
- outside peak bending and impact zones;
- accessible for assembly and inspection;
- printable without trapped support;
- replaceable without destroying the product.

Avoid seams at narrow necks, sharp concave valleys, exact tangent contacts, and areas where both sides vary unpredictably.

### Retention patterns

| Need | Useful pattern | Notes |
|---|---|---|
| location only | two pins plus one plane/shoulder | constrain without overconstraint |
| anti-rotation | D-profile, asymmetric key, spaced pins | make wrong assembly impossible |
| adhesive | shoulder plus controlled bond gap/channel | avoid adhesive as the only datum |
| replaceable color panel | dovetail/slide plus end stop | validate orientation-specific fit |
| hidden fastener | screw/magnet from service side | preserve tool and finger access |
| fused single body | intersecting backer/root volume | avoid coplanar/tangent union |
| flexible skin | continuous groove, beads, tabs | account for stretch and creep |

Use lead-in chamfers and end stops. A friction fit without a positive datum can migrate or seat inconsistently.

## 9. Handle curved and flexible interfaces

### Curved rigid seat

Represent the seat with a parametric surface or sampled patch tied to the project frame. Define:

- patch boundary;
- normal direction;
- maximum curvature and permitted distortion;
- backer thickness and edge feathering;
- registration landmarks distributed across the patch.

Do not flatten and re-bend without checking arc length and feature distortion.

### Flexible TPU/textile interface

Separate free-state and installed-state geometry. Record expected strain and assembly path. Use slots, lacing holes, stitch/adhesive flanges, or compliant keys as parametric geometry. Keep brittle decorative materials away from high-strain lines.

For a flexible organic shell, verify contact pressure, buckling, tear initiation at holes, and creep physically. A visually coincident CAD assembly does not prove the installed flexible shape.

## 10. Handle fused and multi-material bodies

### Fused one-material export

Require intentional positive overlap larger than the numerical/tessellation uncertainty but smaller than the protected detail/seam budget. Union at the final manufacturing stage and retain separate sources.

Never rely on exactly coplanar or tangent faces. They produce solver ambiguity, slivers, non-manifold edges, or disconnected shells.

### Separate multi-material/color bodies

Make each body closed and named. Decide whether the slicer expects coincident shared boundaries, small intentional overlap, or non-overlapping solids; verify in the selected 3MF/slicer workflow. Do not assume viewport color becomes a filament assignment.

For assembled materials, account for differential shrinkage, stiffness, temperature, moisture, and adhesive compatibility.

## 11. Verify the contract

Before full geometry integration:

- solve or place the proxy assembly from the recorded frames;
- display datums, seats, keep-outs, and swept volumes together;
- section every critical interface in at least two directions;
- check assembly direction, tool/finger access, and removal path;
- measure wall/ligament around the full boundary;
- print a reduced interface coupon;
- record the winning process compensation without overwriting nominal geometry.

After organic integration:

- compare the registered mesh to target envelope and landmarks;
- verify no high-value detail was trimmed outside the seam band;
- check overlap/gap and component count after export round-trip;
- inspect slicer paths through the seam and retention features;
- test the actual joining process and revise the parametric allowance.

Version interface bodies and transforms together. A component registered against interface revision A must not be silently assembled with revision B.
