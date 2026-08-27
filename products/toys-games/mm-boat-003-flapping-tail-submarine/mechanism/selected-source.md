# Selected and rejected library sources

## Adopted: 002 offset-pin-hinge-standard

Source:
`../vendor/fdm-mechanics-library-v1.0.0/samples/01_rotation_1d/002-offset-pin-hinge-standard/`

- Reused principle: removable vertical pin, one controlled rotational axis.
- Reused interface: 4.0 mm pin, 0.25 mm per-side clearance.
- Exact compatibility: matches `hinge_pin_d=4.0` and
  `hinge_clearance=0.25` in `submarine/config.py`.
- Geometry policy: do not import the flat hinge leaves. The U-boat lugs remain
  native CadQuery bodies because they close the individual flotation cells and
  own the fish-envelope seam.
- Evidence: library sample digital validation PASS; no physical print record.
- Calibration: print sample 002 `print_plate.stl` unchanged before a release
  print, then verify the product-specific hinge coupon.

## Adopted: 078 bayonet-quarter-turn-030

Source:
`../vendor/fdm-mechanics-library-v1.0.0/samples/06_reusable_closures/078-bayonet-quarter-turn-030/`

- Reused principle: axial insertion channels followed by a short locking turn.
- Reused parameter: 0.30 mm standard running clearance for PETG/0.4 mm nozzle.
- Geometry policy: do not scale the 18 mm sample STL. The 39.2 mm capsule bore,
  O-ring gland, grip tabs and hinge keep-out remain exact native CadQuery
  geometry. The O-ring groove depth is compensated independently.
- Evidence: library sample digital validation PASS; no physical sealing,
  vibration or underwater-cycle record.

## Rejected: 109 split-shaft-coupler-d4

Source:
`../vendor/fdm-mechanics-library-v1.0.0/samples/08_drives_and_components/109-split-shaft-coupler-d4/`

- Sample envelope per half: about 32 x 24 x 6 mm; requires two M3 screws/nuts.
- Sample joins equal 4 mm shafts. The product needs 3.0 mm motor shaft to
  4.5 mm sleeve and has a much smaller flooded-tail keep-out.
- Result: direct reuse rejected. It adds drag, mass and hardware and cannot be
  uniformly scaled without invalidating bores and fastener pockets.

## Rejected: 105-108 rotary-detent-indexer

- A wet printed flexure would add debris sensitivity, creep and cyclic failure.
- O-ring friction already gives axial preload and rotational resistance.
- Reconsider only if physical vibration tests show unintended cap rotation.

## Purchased components, not library geometry

N20 motor, metal motor shaft, AAA cells/contacts, reed switch, magnet, O-rings,
wire, grease and ballast remain purchased components. Their supplier-specific
dimensions still need local receiving inspection before production release.
