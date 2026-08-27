# MM-ORG-014 Embroidery-floss project palette dock

Parametric desktop dock for 30 individually labelled embroidery-floss cards or drops. Three lanes of ten positions preserve working order while a tapered production slot accepts the declared 0.6, 2.0 and 3.0 mm card classes. A compact three-position coupon reproduces the real receiver geometry before the full dock print.

Build with `python cad/build.py`; run parameter tests with `python -m pytest -q tests/test_parameters.py`.

Digital candidate status: `PASS` through exact Anycubic Slicer Next preflight and autonomous print-candidate approval. The dock and coupon are each one watertight positive-volume component; the two-object 3MF slices in the Kobra 3 Max reference profile without native warnings. See `final-model-result-report.md` and `reports/validation-summary.json`.

Primary files:

- Parametric source: `cad/build.py` plus `config/model-parameters.json`
- Editable masters: `exports/master/*.step`
- Dock STL: `exports/manufacturing/DRAFT-MM-ORG-014-palette-dock-0.1.0-draft.1.stl`
- Fit coupon STL: `exports/coupons/DRAFT-MM-ORG-014-three-card-fit-coupon-0.1.0-draft.1.stl`
- Slicer-ready set: `exports/3mf/DRAFT-MM-ORG-014-palette-dock-and-fit-coupon-0.1.0-draft.1.3mf`
- Preview: `renders/MM-ORG-014-digital-candidate.png`

All outputs remain `DRAFT`. The model stores floss cards only: it is not a needle holder, child product, portable closed case or claim that every commercial card fits without the coupon test.
