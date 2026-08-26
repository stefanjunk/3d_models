# RC car sporty envelope reference

This example separates an immutable mechanical coordinate system from the visible body and a smooth chassis plate.

- Axle axes and chassis mounts are stored as hardpoints.
- The body is a fair section loft driven by longitudinal width and roof profiles.
- The chassis is a separate extruded smooth plan outline.
- Hard features such as bearing seats, suspension towers, motor mounts, wheel arches, clips, and body posts are intentionally left for `functional-3d-design` after the aesthetic envelope is approved.

This is not a complete driveable RC chassis or crash-safe body.

```bash
python generate.py --parameters parameters.yaml --output build --quality print
```
