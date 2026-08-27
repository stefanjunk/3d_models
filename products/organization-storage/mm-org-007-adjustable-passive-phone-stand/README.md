# MM-ORG-007 — Adjustable Passive Phone Stand

Parametric PETG stand with a wide base, hinged backrest/shelf and printed pin. Three base variants isolate shallow, medium and firm detent-pocket profiles for later physical comparison.

This implements research idea `SKU-005` as a DRAFT digital candidate. It contains no charging electronics and has no stability, hinge-life or device-safety claim before physical testing.

Generate the default STEP, STL, coupon, reference assembly and five-object 3MF with:

```bash
python3 cad/build.py
```

The 3MF contains all three alternative bases for inventory and comparison. Print the detent coupon first, then slice only the selected base together with the common backrest and pin. See `PRINT-GUIDE.md` and `tests/physical-test-plan.md` for the deferred physical gate.
