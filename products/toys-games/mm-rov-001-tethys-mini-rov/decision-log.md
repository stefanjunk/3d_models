# Decision log — MM-ROV-001

## 2026-08-29 — Integration and identity

- Assigned product ID `MM-ROV-001` and portfolio record `PORT-098`.
- Preserved the original zip and exact extracted package; large zip/STL artifacts
  are assigned to Git LFS without rewriting history.
- Identified this as the requested second submarine, distinct from
  `MM-BOAT-003` Flapping Tail Submarine.
- Classified the product as `P2 Digital candidate`: source, 13 reference meshes,
  manifest and tests exist; slicer and physical evidence do not.

## 2026-08-29 — Communication and component-family boundary

- Preserved Ethernet tether control/video as the submerged primary link.
- Rejected direct submerged 2.4 GHz ELRS, Wi-Fi and 5.8 GHz analog FPV as a false
  cross-platform reuse assumption.
- Permitted shared ExpressLRS knowledge or hardware only in an optional buoy
  above the waterline, after the direct-tether baseline is validated.
- Kept Camera Module 3 Wide, three reversible ESCs and 3S power specific to Tethys.
- No imported geometry was changed because requirements and concept approval
  remain pending.
