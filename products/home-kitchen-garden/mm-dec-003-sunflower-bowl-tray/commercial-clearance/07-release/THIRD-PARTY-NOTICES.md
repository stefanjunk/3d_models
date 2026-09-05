# Third-Party Notices — draft evidence index

Product: MM-DEC-003 Sunflower Bowl / Tray

Candidate: 0.2.0

Prepared: 2026-09-05

Status: incomplete; commercial release blocked

No third-party CAD, stock model, font, logo, texture, purchased component or Hunyuan-generated legacy mesh is included in the v0.2.0 digital candidate.

## Generative and engineering tools

- **Step1X-3D** — stepfun-ai. Upstream code and model card declare Apache License 2.0. Sources: <https://github.com/stepfun-ai/Step1X-3D> and <https://huggingface.co/stepfun-ai/Step1X-3D>. Used only for untextured geometry generation. Retain applicable Apache copyright, licence and NOTICE material if covered code or model material is redistributed. The generated STL does not itself include the Step1X software.
- **rembg/U2Net** — used locally for foreground isolation because the image source lacked useful alpha. Exact runtime and ONNX hashes are retained. Complete model-licence evidence must be archived before any release that relies on this chain.
- **NumPy, SciPy, Trimesh, Rtree and Manifold3D** — used by product scripts for mesh processing and validation. They are not embedded in the STL or G-code. If scripts are distributed, include their applicable BSD, MIT and Apache notices and exact licence texts after package-level verification.
- **Blender 5.2.0 LTS** — GPL-2.0-or-later application used for diagnostic renders. No Blender binary or source is included.
- **Anycubic Slicer Next 1.3.9.4** — AGPL-3.0-only application used for local G-code export. The slicer binary is not part of the product package. G-code is machine/profile-specific manufacturing output and carries no endorsement by Anycubic.
- **OpenAI services** — generated the reference image and assisted engineering/documentation. Governing account terms have not been archived and remain a release blocker. OpenAI names and marks are used only factually; no endorsement is implied.

## Excluded legacy materials

The prior `1.stl`, `2.stl`, legacy 3MF, procedural archive and all external model archives are excluded. No Tencent Hunyuan notice is applied to the new candidate because no Hunyuan material is used in it; the suspected old chain is separately blocked and retained only as project history.

## Contact and completion

The seller contact is not yet assigned. Before release, replace this draft with a package-specific notice file containing every required copyright notice, full licence text or durable source offer for the exact distributed files.
