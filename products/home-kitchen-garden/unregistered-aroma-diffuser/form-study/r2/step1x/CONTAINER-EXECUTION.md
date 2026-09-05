# Local client execution and provenance

No service rebuild, package installation or second geometry job was used.
Host probe/status succeeded, but generate refused before submission because
host Python lacks pinned gradio_client 1.4.2. The existing serving container
421a6f15f4d1 already contains that exact client.

The unmodified skill client and input evidence were copied into the unique
container directory /tmp/fluent-r2-client.q848ud. The first shallow script
location failed in argparse because default_repo() indexes parents[5].
No job was submitted by that failed invocation. Keeping the normal
repo/.agents/skills/step1x-image-to-3d/scripts nesting resolved it without
editing shared tooling. This portability issue is a candidate main-only
dependency, not fixed on the product branch.

Exactly one successful request used the nested original client against
127.0.0.1:7861, with the parameters in run-001/step1x-run.json. The run folder
was copied byte-for-byte back into this product. Original absolute paths in
the immutable run record therefore name container paths:

- /tmp/fluent-r2-client.q848ud/run-001 -> this directory's run-001
- /tmp/fluent-r2-client.q848ud/runtime.json -> runtime.json

The run record's automatic served_by_fork probe points to a non-existent
container-side Git checkout. Do not mistake it for source attestation.
The separately captured, SHA-256-bound runtime-profile.json records the
host source checkout and actual container/image/model inventory. Source is
clean commit 4b6da92a56acb3a135b0493703470995c00c5e91. A read-only
git merge-base --is-ancestor f00dd46 4b6da92 returned 0.
This chain is retained for review, not described as commercial clearance.

Input R1 failed the alpha requirement (painted checkerboard, RGB) and was
rejected. Input R2 is opaque white, visually checked and accepted with
recorded narrower-than-requested margins. The service's pinned CPU rembg
path was used. Prompts, both candidate images and the raw output survive.
