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

# epiR is the Rogan-Gladen witness. O-8 said there was no library witness; that
# was true of survey and svy, not of the world. Its intervals follow Reiczigel
# et al. (2010) -- S-1.6, the paper matching our assumption that Se and Sp are
# supplied and exact.
#
# What this witness does NOT establish: Jeno Reiczigel is a listed contributor
# to epiR. It is the method author's own implementation of the method author's
# own paper. It confirms we implement the method as its author does. It does not
# independently confirm the method. Barnett Table 2B is a different kind of
# evidence and this is not that.
#
# epiR pulls in `units`, which links against libudunits2 at load time. Without
# it `library(epiR)` fails with a dyn.load error rather than a missing-package
# error, which is a confusing way to find out.
# epiR drags in the spatial stack (sf -> proj, gdal, geos) for functions we
# never call. That is a lot of image for one estimator, and it is the price of
# using the method author's own implementation as the witness rather than a
# reimplementation of our own. Recorded rather than absorbed.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libudunits2-dev libproj-dev libgdal-dev libgeos-dev \
 && rm -rf /var/lib/apt/lists/*
#
# 2.0.92, and that is not a typo for 2.0.96. The snapshot above is frozen at
# 2026-04-23; 2.0.96 was published 2026-08-03, so the snapshot serves 2.0.92.
# Ruled 2026-08-29: pin what the snapshot gives, so the whole witness comes from
# one pin, and record 2.0.96 as current-but-outside. S-1.10.
#
# The assertion is the point. Without it a snapshot bump would move the witness
# silently, which is V-17's shape.
RUN R -q -e 'install.packages("epiR"); \
             stopifnot(as.character(packageVersion("epiR")) == "2.0.92"); \
             cat("epiR", as.character(packageVersion("epiR")), "pinned\n")'

WORKDIR /witness
COPY barnett_table_2b.R /witness/barnett_table_2b.R
COPY stratified_fixtures.R /witness/stratified_fixtures.R
COPY clopper_pearson_fixtures.R /witness/clopper_pearson_fixtures.R
COPY rogan_gladen_fixtures.R /witness/rogan_gladen_fixtures.R

# Default is the anchor. D2.2 is run by naming its script:
#   docker run ... <image> /witness/stratified_fixtures.R
ENTRYPOINT ["Rscript"]
CMD ["/witness/barnett_table_2b.R"]
