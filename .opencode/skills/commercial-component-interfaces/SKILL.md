---
name: commercial-component-interfaces
description: Use when a commercial CadQuery design needs original bearing seats, shaft bores, heat-set insert holes, screw clearances, or standard-part envelopes without importing third-party CAD.
---

# Commercial Component Interfaces

Use the repository-relative `libraries/commercial-components` package to create
original interface cutters from explicit dimensions. If that package is not
present, report the exact blocker instead of importing from another checkout.
The library is MIT-licensed and contains no embedded standards tables or
third-party CAD.

## Rules

1. Select the actual purchased component first.
2. Obtain its dimensions from a standard or manufacturer drawing that permits
   factual dimensional use; record title, URL, and revision/access date.
3. Supply those dimensions explicitly to the helper. Never invent a nominal
   fit or assume all suppliers are interchangeable.
4. Keep process compensation separate from the nominal interface.
5. Validate assembly, tool access, fit coupon, and physical component.

## Import

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("libraries/commercial-components/src").resolve()))

from commercial_components import ComponentSource, bearing_seat_cutter
```

Read the library README for the API. Use `commercial-cad-provenance` before
adding any downloaded component model instead of an original interface.
