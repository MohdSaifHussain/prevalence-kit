# prevalence-kit, containerised so it can be run without a Python installation.
#
# D3.12, ruled at Q30 / D-56: THIS IMAGE SHIPS THE TOOL ALONE. The R witness is
# a separate concern with a separate audience -- `r/Dockerfile` builds it, and
# `.github/workflows/witness.yml` rebuilds it on demand and requires every
# fixture to regenerate byte-identically. Coupling a large R image to every
# operator who only wants to measure something would make the common case pay
# for the rare one.
#
# The base is pinned BY DIGEST, not by tag, for the reason S-2.1a already gives
# about the witness image: a tag moves, a digest does not. Resolved 2026-08-31
# with `docker buildx imagetools inspect python:3.14-slim`.
#
#   docker.io/library/python:3.14-slim
#   sha256:cae66f2ef0ec51a9891263eeee7f987dacf0a9879e8aa9353d5606e0530619a5
#
# 3.14 is the development line this project targets; CI proves the 3.12 floor
# on every push (D-10). The image is not the gate -- it is how a stranger runs
# the tool.

FROM python@sha256:cae66f2ef0ec51a9891263eeee7f987dacf0a9879e8aa9353d5606e0530619a5

LABEL org.opencontainers.image.title="prevalence-kit" \
      org.opencontainers.image.description="Audit-grade prevalence measurement for Trust & Safety. Sealed evidence, tamper-evident record, refusals with named reasons." \
      org.opencontainers.image.source="https://github.com/MohdSaifHussain/prevalence-kit" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.base.name="docker.io/library/python:3.14-slim" \
      org.opencontainers.image.base.digest="sha256:cae66f2ef0ec51a9891263eeee7f987dacf0a9879e8aa9353d5606e0530619a5"

# Deterministic, quiet, and no stale bytecode written into the layer.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /src

# Dependencies first, hash-locked, in their own layer so a source change does
# not re-resolve them. `--require-hashes` makes pip refuse anything whose
# artifact does not match the recorded digest -- charter 5.1's first clause,
# and D-57. Copying constraints.txt alone keeps this layer cached.
COPY constraints.txt ./
RUN python -m pip install --require-hashes --no-deps -r constraints.txt

# Now the package itself. --no-deps because the line above already installed
# every dependency at a pinned hash; without it, pip would be free to resolve
# something else and the lock would be decorative.
COPY pyproject.toml README.md LICENSE NOTICE ./
COPY src/ ./src/
RUN python -m pip install --no-deps .

# What an operator needs in the image, and nothing else. The examples are here
# so that `prevalence-kit` can be run against something real the moment the
# container starts -- the SOP's first command depends on it.
COPY examples/ /opt/prevalence-kit/examples/

# A non-root user, and a work directory it owns. Runs that write a ledger, a
# sealing key and sealed content must not need root to do it.
RUN useradd --create-home --uid 10001 measurer \
    && mkdir -p /work \
    && chown -R measurer:measurer /work /opt/prevalence-kit
USER measurer
WORKDIR /work

# The sealing key is written into the run directory. /work is the mount point:
#   docker run --rm -v "$PWD:/work" ghcr.io/mohdsaifhussain/prevalence-kit ...
# Nothing here writes outside it.
VOLUME ["/work"]

# A build that succeeds and a tool that runs are different claims (R3.12), so
# the image checks itself: this fails the build if the entry point is not
# importable and callable.
RUN prevalence-kit --version

ENTRYPOINT ["prevalence-kit"]
CMD ["--help"]
