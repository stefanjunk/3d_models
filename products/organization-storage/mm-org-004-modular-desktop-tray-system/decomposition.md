# Product decomposition — MM-ORG-004

## Authority map

- Parametric CAD owns every tray shell, wall, floor, rim, receiver boss, socket, connector and coupon.
- `config/model-parameters.json` is the dimensional source of truth.
- The SVG is a visual contract only; it never drives dimensions.
- No organic mesh, purchased component, external model, font, image texture or third-party geometry is included.

## Printed components

1. `tray_precision`: compact 76 × 76 × 28 mm body with small corner radius.
2. `tray_soft`: 112 × 76 × 34 mm body with medium corner radius.
3. `tray_lounge`: 150 × 76 × 40 mm body with large corner radius.
4. `bowtie_link`: common removable underside connector; print two for the three-module reference layout.
5. `interface_coupon`: two short receiver sections plus link, isolated from the long tray prints.

## Interface contract

- Datum: each socket is centered on its host side and starts at the flat underside `z=0`.
- Mating: two opposing socket centerlines are collinear across a nominal 1.0 mm module gap.
- Fit: connector outline is offset by 0.30 mm per side from each socket outline.
- Assembly: invert modules, align sockets, insert connector along +Z, return assembly to the desk.
- Retention: the desk surface is the axial stop; the dovetail heads resist in-plane separation.
- Keep-out: no ribs, labels or cosmetic cuts may enter the receiver boss, socket roof or 4 mm surrounding band.

## Manufacturing split

All components are independent support-conscious FDM prints. Trays print bottom-down. The connector and coupon print on their largest flat faces. The DRAFT 3MF is an inventory arrangement, not an exact sliced manufacturing profile.
