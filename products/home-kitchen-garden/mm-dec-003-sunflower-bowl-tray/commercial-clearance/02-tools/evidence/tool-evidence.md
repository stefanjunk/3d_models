# Tool evidence — MM-DEC-003 v0.2.0

- OpenAI image generation: the source PNG contains C2PA credentials for `gpt-image 2.0`; current account plan and operative terms snapshot are not archived, so the tool gate remains WARN.
- Step1X-3D: owned local geometry-only fork commit `4b6da92a56acb3a135b0493703470995c00c5e91`, clean at runtime. Upstream code and weights declare Apache-2.0. The exact runtime profile and run record are archived under this clearance workspace. Dependency and training-data review remains open.
- rembg/U2Net: rembg 2.0.65 executed locally because the source PNG was opaque. The exact ONNX asset hash is in the runtime profile; model-licence evidence still needs packaging review.
- Engineering mesh toolchain: NumPy 2.5.2, SciPy 1.18.1, Trimesh 5.1.0, Rtree 1.4.1, and Manifold3D 3.2.1. No library binary is embedded in the STL or G-code. If source scripts are sold, applicable notices and licence texts must be included.
- Blender 5.2.0 LTS produced diagnostic renders only.
- Anycubic Slicer Next 1.3.9.4 produced local G-code only through the repository adapter. No printer upload or print start occurred.

This record is an engineering evidence index, not a legal opinion.
