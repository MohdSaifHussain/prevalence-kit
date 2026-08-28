#!/usr/bin/env bash
# Run the R witness. Phase 2 exit check F1.
#
#   bash r/run-witness.sh
#
# Expected: reproduces Barnett Table 2B -- 2098 / 828 / 584 / 256 / 234,
# VVR 0.20%, SD 0.054 pp -- and exits 0.
#
# It builds from a digest-pinned base image, so the first run downloads the
# image and installs survey. Later runs use the layer cache and take seconds.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
image="prevalence-kit-witness:d2.1"

# F16: the base image digest must match the register.
pinned="sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0"
if ! grep -q "$pinned" "$here/Dockerfile"; then
  echo "REFUSED: r/Dockerfile does not pin the digest recorded in docs/STANDARDS.md S-2.1a." >&2
  exit 2
fi
if ! grep -q "$pinned" "$here/../docs/STANDARDS.md"; then
  echo "REFUSED: docs/STANDARDS.md S-2.1a does not carry the digest r/Dockerfile uses." >&2
  exit 2
fi
echo "digest check: r/Dockerfile and docs/STANDARDS.md S-2.1a agree"
echo "  $pinned"
echo

docker build -q -t "$image" "$here" > /dev/null
mkdir -p "$here/fixtures"
exec docker run --rm -v "$(cd "$here/fixtures" && pwd -W 2>/dev/null || pwd):/fixtures" "$image"
