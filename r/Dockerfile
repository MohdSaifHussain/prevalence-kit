# The R witness. Phase 2 D2.1.
#
# Pinned by DIGEST, not by tag. `rocker/r-ver:4.5` and `:4.5.3` resolve to the
# same image today; `4.5` is a moving pointer and will not tomorrow. A witness
# meant to be reproducible by a stranger cannot rest on something that moves.
# Phase 2 contract R2.6, decision D-26, register S-2.1a.
#
# The base image also pins its CRAN mirror to a frozen snapshot
# (p3m.dev/cran/__linux__/noble/2026-04-23), so `install.packages` is
# deterministic: it serves survey 4.5, which is what S-2.1 pins.
FROM rocker/r-ver@sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0

# jsonlite writes the fixture. survey is the witness itself.
RUN R -q -e 'install.packages(c("survey", "jsonlite")); \
             stopifnot(as.character(packageVersion("survey")) == "4.5")'

WORKDIR /witness
COPY barnett_table_2b.R /witness/barnett_table_2b.R
COPY stratified_fixtures.R /witness/stratified_fixtures.R
COPY clopper_pearson_fixtures.R /witness/clopper_pearson_fixtures.R

# Default is the anchor. D2.2 is run by naming its script:
#   docker run ... <image> /witness/stratified_fixtures.R
ENTRYPOINT ["Rscript"]
CMD ["/witness/barnett_table_2b.R"]
