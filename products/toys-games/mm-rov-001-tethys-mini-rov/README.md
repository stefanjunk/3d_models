# MM-ROV-001 — Tethys Mini ROV

Portfolio record: `PORT-098`

Current controlled revision: `0.1.0` imported requirements candidate

Lifecycle: `P2 Digital candidate` — parametric Python source, 13 reference STL
meshes, a mesh manifest, software and automated tests exist. Exact slicing,
pressure/leak testing, purchased-part measurement and physical water trials do not.

Independent release-profile audits load all 13 STLs as one-component watertight
meshes. Ten require review for inconsistent face winding/positive-volume
orientation, so the imported files are reference meshes, not release meshes.

The original zip is preserved under `imports/`; its exact contents are extracted
under `legacy-package/`. Large archive and STL artifacts are tracked through Git
LFS. Tethys is the separate remote-controlled submarine requested by the user;
it does not replace the already integrated flapping-tail submarine.

Tethys is a tethered ROV. Underwater control and camera video use Ethernet to the
topside station. ExpressLRS or Wi-Fi may be used only on an optional surface buoy,
not as the submerged primary link.
