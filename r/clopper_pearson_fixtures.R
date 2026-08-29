# Phase 2, D2.4 -- Clopper-Pearson fixtures from base R.
#
# No estimator code. This records what an outside implementation says, so the
# Python interval can be written against numbers that already existed. R2.2.
#
# WHY base R and not survey. The contract's section 2.3 said Clopper-Pearson has
# "no published table" and would be checked against an independent
# implementation we wrote. There is a better option, and it was missed:
# `stats::binom.test` returns the Clopper-Pearson exact interval, it ships with
# R itself, and it is a different implementation lineage from `survey`. That
# makes it an EXTERNAL witness rather than a second thing by the same author.
#
# THE INDEPENDENCE THAT MATTERS, and it is the reason this fixture is worth
# anything. R reaches the interval by inverting an incomplete beta -- `qbeta`.
# The Python side reaches it by root-finding on the exact binomial tail with
# integer coefficients. Two different arithmetic paths to the same definition.
#
#   lower p_L solves   P(X >= k | n, p_L) = alpha/2
#   upper p_U solves   P(X <= k | n, p_U) = alpha/2
#
# There is no incomplete beta function anywhere in this project, so "checking
# betainc against betainc" cannot happen here by construction.
#
# Anchor: S-1.1 Brown, Cai & DasGupta (2001), DOI 10.1214/ss/1009213286.

suppressPackageStartupMessages(library(jsonlite))

# THE SECOND AXIS, added 2026-08-29.
#
# The first version of this fixture varied n across six orders of magnitude
# and held confidence at exactly 0.95. So "7.1e-11 across 23 cases, n = 1 to
# n = 1,999,514" read as a statement about the estimator when it was a
# statement about the estimator AT ONE CONFIDENCE LEVEL. Nothing in the
# sentence said which dimensions were explored and which were pinned.
#
# F-8 is what made this concrete: `confidence` was unvalidated in every
# interval estimator, and no fixture could have found it, because no fixture
# ever varied it. A parameter no instrument points at.
#
# binom.test takes conf.level, so closing this costs three lines.
CONF_LEVELS <- c(0.90, 0.95, 0.99)
PRIMARY <- 0.95

cases <- list()
add <- function(n, k, note) {
  for (conf in CONF_LEVELS) {
    bt <- binom.test(k, n, conf.level = conf)
    ci <- as.numeric(bt$conf.int)
    cases[[length(cases) + 1]] <<- list(
      n = n, k = k, conf = conf, note = note,
      point = k / n,
      lower = ci[1], upper = ci[2]
    )
  }
}

# Edges first, because they are where interval code goes wrong.
add(1, 0, "n=1, no successes. The smallest thing that must still produce a bound")
add(1, 1, "n=1, all successes")
add(2, 0, "zero successes: lower bound must be exactly 0")
add(2, 2, "all successes: upper bound must be exactly 1")
add(10, 0, "zero out of ten -- the rule-of-three regime")
add(10, 10, "ten out of ten")

# Ordinary interior cases.
for (n in c(10, 20, 40, 100)) {
  for (k in c(1, floor(n / 2), n - 1)) {
    add(n, k, sprintf("interior, n=%d k=%d", n, k))
  }
}

# The regime this tool exists for: rare events at large n.
add(4000, 0, "rare event, no violations found at all")
add(4000, 1, "rare event, a single violation")
add(4000, 8, "rare event, Barnett-scale n at roughly 0.2%")
add(4000, 9, "rare event, one more")
add(1999514, 137, "Civil Comments scale, very low prevalence")

cat("\n")
cat("D2.4 -- Clopper-Pearson fixtures from stats::binom.test\n")
cat("=======================================================\n")
cat(sprintf("  %s\n", R.version.string))
cat(sprintf("  confidence levels: %s\n\n", paste(CONF_LEVELS, collapse = ", ")))
cat(sprintf("  %8s %8s %6s %16s %16s\n", "n", "k", "conf", "lower", "upper"))
for (c in cases) {
  cat(sprintf("  %8d %8d %6.2f %16.12f %16.12f\n", c$n, c$k, c$conf, c$lower, c$upper))
}

fixture <- list(
  what = "Clopper-Pearson exact binomial intervals, from base R",
  deliverable = "D2.4",
  produced_by = "r/clopper_pearson_fixtures.R",
  generated_before_any_estimator = TRUE,
  exact_call = "binom.test(k, n, conf.level = conf)$conf.int, for conf in {0.90, 0.95, 0.99}",
  witness_note = paste(
    "stats::binom.test is base R, a different implementation lineage from",
    "survey. It reaches the interval by inverting an incomplete beta (qbeta).",
    "The Python side root-finds on the exact binomial tail. Two arithmetic",
    "paths, one definition -- which is what makes agreement mean something."
  ),
  defining_property = paste(
    "P(X >= k | n, lower) = alpha/2 and P(X <= k | n, upper) = alpha/2.",
    "This is the definition, not a consequence of it."
  ),
  environment = list(
    image_digest = "sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0",
    r_version = R.version.string,
    cran_snapshot = getOption("repos")[["CRAN"]]
  ),
  standards = list(anchor = "S-1.1 Brown, Cai & DasGupta (2001), DOI 10.1214/ss/1009213286"),
  confidence = PRIMARY,
  confidence_levels = CONF_LEVELS,
  axes = list(
    varied = c("n", "k", "conf"),
    held_fixed = c("none"),
    note = paste(
      "Every agreement figure taken from this fixture must state its axes.",
      "Before 2026-08-29 conf was pinned at 0.95 and the figures did not say so."
    )
  ),
  cases = cases
)

out_dir <- "/fixtures"
if (dir.exists(out_dir)) {
  writeLines(toJSON(fixture, auto_unbox = TRUE, pretty = TRUE, digits = 15),
             file.path(out_dir, "clopper_pearson.json"))
  cat(sprintf("\n  fixture written to %s/clopper_pearson.json\n", out_dir))
} else {
  cat("\n  no /fixtures mount, fixture not written\n")
}

cat(sprintf("\n%d cases. No estimator code was written by this script.\n\n", length(cases)))
