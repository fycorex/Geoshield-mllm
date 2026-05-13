# Manifests

Manifests are frozen, lightweight tables that define exactly which images are included in a run. They store stable ids, source references, ground-truth coordinates, optional administrative metadata, tags, checksums, and notes.

Sampling must be deterministic and seed-controlled. Once a manifest is used for evaluation, do not mutate it in place; create a new manifest version if corrections are needed.

Manifest files belong in git because they are lightweight and required for reproducibility. Image files referenced by manifests belong in Drive or ignored local artifact directories.

