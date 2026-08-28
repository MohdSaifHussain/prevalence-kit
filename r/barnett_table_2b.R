# Phase 2, D2.1 -- the R witness, proving itself before it witnesses anything.
#
# This script writes NO estimator. It reproduces a published table.
#
# Why this comes first (Phase 2 contract, section 2.2). Every fixture in this
# phase will be produced by an svydesign() call that the builder wrote. A wrong
# call -- wrong weights, wrong strata, an fpc that should not be there --
# produces a wrong fixture, and a correct estimator then reproduces it
# faithfully while the whole suite stays green. The witness is external. The
# invocation of the witness is not.
#
# So before survey witnesses anything, survey has to reproduce a number nobody
# in this project produced: Arnold Barnett's Table 2B.
#
#   Barnett, A. "YouTube's Violative View Rate Methodology: A Statistical
#   Assessment." MIT, September 2021. Register S-2.3.
#   Commissioned and funded by Google. Expert review, not independent peer
#   review. That caveat travels with every citation of it.
#
# Two separate things are checked here, and they prove different things:
#
#   Block A  Barnett's Table 2B, recomputed from his Table 2A in base R.
#            Proves the SPECIFICATION in S-2.3 is right.
#
#   Block B  The survey call, checked against the closed-form with-replacement
#            stratified variance on identical inputs.
#            Proves the CALL is right -- weights, strata, and no fpc.
#
# Exit 0 only if every check passes.

suppressPackageStartupMessages({
  library(survey)
  library(jsonlite)
})

pass_all <- TRUE

check <- function(label, ok, got, want) {
  status <- if (ok) "PASS" else "FAIL"
  if (!ok) pass_all <<- FALSE
  cat(sprintf("  [%s] %-46s got %-22s want %s\n", status, label, got, want))
  # invisible(): at top level R auto-prints a returned value, which put a
  # stray "[1] TRUE" after every line of the report.
  invisible(ok)
}

# --------------------------------------------------------------------------
# Barnett Table 2A -- the published input. Transcribed, not computed.
# --------------------------------------------------------------------------
strata <- data.frame(
  name = c("Lowest Risk", "Low Risk", "Middle Risk", "High Risk", "No score available"),
  W    = c(0.80,          0.10,       0.05,          0.01,        0.04),
  p    = c(0.0005,        0.0050,     0.0100,        0.0500,      0.0025),
  stringsAsFactors = FALSE
)
n_total <- 4000

# Barnett Table 2B -- the published output we must land on.
published_allocation <- c(2098, 828, 584, 256, 234)
published_vvr_pct    <- 0.20
published_sd_pp      <- 0.054

cat("\n")
cat("R witness -- Barnett Table 2B reproduction\n")
cat("==========================================\n")
cat(sprintf("  %s\n", R.version.string))
cat(sprintf("  survey %s   jsonlite %s\n",
            as.character(packageVersion("survey")),
            as.character(packageVersion("jsonlite"))))
cat("\n")

# --------------------------------------------------------------------------
# BLOCK A -- reproduce Table 2B from Table 2A. Base R. No survey.
# --------------------------------------------------------------------------
cat("Block A -- Barnett Table 2B from Table 2A (base R)\n")
cat("--------------------------------------------------\n")

# Neyman (optimal) allocation with the proportion standard deviation.
# S-2.3 pins this as a specification, reached by reproduction rather than by
# intention: n_h proportional to W_h * sqrt(p_h(1-p_h)).
S_h <- sqrt(strata$p * (1 - strata$p))
raw <- n_total * (strata$W * S_h) / sum(strata$W * S_h)
allocation <- round(raw)

# Ordinary rounding, and no tie-breaking rule is involved. An earlier draft of
# this comment claimed stratum 1 lands on exactly 2098.5 and that R's
# half-to-even rule is what produces Barnett's 2098. That is wrong: the raw
# value is 2098.4952, just under the midpoint, so it rounds down whatever the
# tie rule. The claim came from reading "2098.50" in a two-decimal table and
# inventing a mechanism to explain it. The printed raw values below are there so
# nobody has to take this paragraph's word for it.
#
# Worth knowing anyway: stratum 1 sits 0.005 from the midpoint. A different
# arithmetic path could tip it to 2099 and make the total 4001.
# Four decimals, not two. At two decimals stratum 1 prints as "2098.50", which
# reads as an exact midpoint and is what produced the wrong comment above.
cat(sprintf("  raw allocations: %s\n", paste(sprintf("%.4f", raw), collapse = " / ")))

check("allocations match Table 2B",
      identical(as.numeric(allocation), as.numeric(published_allocation)),
      paste(allocation, collapse = "/"),
      paste(published_allocation, collapse = "/"))

check("allocations sum to n",
      sum(allocation) == n_total,
      sum(allocation), n_total)

# Population VVR: the weighted mean of the stratum rates.
vvr <- sum(strata$W * strata$p)
check("population VVR (%)",
      isTRUE(all.equal(round(vvr * 100, 4), published_vvr_pct, tolerance = 1e-9)),
      sprintf("%.4f%%", vvr * 100),
      sprintf("%.2f%%", published_vvr_pct))

# Expected SD of the estimate. With replacement, NO finite-population
# correction -- that is what reproduces 0.054 pp, and it is the half of the
# specification most easily got wrong.
var_expected <- sum(strata$W^2 * strata$p * (1 - strata$p) / allocation)
sd_pp <- sqrt(var_expected) * 100

check("expected SD (pp), rounded as published",
      isTRUE(all.equal(round(sd_pp, 3), published_sd_pp, tolerance = 1e-9)),
      sprintf("%.4f pp", sd_pp),
      sprintf("%.3f pp", published_sd_pp))

# --------------------------------------------------------------------------
# BLOCK B -- the survey call, checked against the closed form.
# --------------------------------------------------------------------------
cat("\n")
cat("Block B -- the svydesign() call, against the closed form\n")
cat("--------------------------------------------------------\n")

# A sample of exactly the allocated size, with the nearest whole number of
# positives to each stratum's rate. Integer counts, so p_hat is not identical
# to Barnett's p -- that difference is reported below rather than hidden.
positives <- round(strata$p * allocation)

sample_rows <- do.call(rbind, lapply(seq_len(nrow(strata)), function(h) {
  n_h <- allocation[h]
  data.frame(
    stratum = strata$name[h],
    y       = c(rep(1L, positives[h]), rep(0L, n_h - positives[h])),
    # Weight so each stratum's weights total its population share W_h. The
    # weights then sum to 1 and svymean returns sum(W_h * p_hat_h).
    w       = strata$W[h] / n_h,
    stringsAsFactors = FALSE
  )
}))

# THE CALL. This exact line is what the rest of Phase 2 will trust.
# ids = ~1        : one stage, units drawn independently
# strata = ~stratum
# weights = ~w    : known stratum shares
# no fpc          : with replacement, matching S-2.3's specification
design <- svydesign(ids = ~1, strata = ~stratum, weights = ~w, data = sample_rows)
est <- svymean(~y, design)

survey_mean <- as.numeric(coef(est))
survey_se <- as.numeric(SE(est))

# The closed form, on the SAME inputs survey saw. s_h^2 uses the (n_h - 1)
# denominator, because that is the sample variance survey computes.
p_hat <- positives / allocation
s2_h <- (allocation / (allocation - 1)) * p_hat * (1 - p_hat)
closed_form_se <- sqrt(sum(strata$W^2 * s2_h / allocation))

cat(sprintf("  survey mean      %.12f\n", survey_mean))
cat(sprintf("  survey SE        %.12f\n", survey_se))
cat(sprintf("  closed-form SE   %.12f\n", closed_form_se))

# R2.3: agreement to at least 4 significant digits, or the build is red.
rel_diff <- abs(survey_se - closed_form_se) / closed_form_se
check("survey SE vs closed form (R2.3, >= 4 sig digits)",
      rel_diff < 1e-4,
      sprintf("rel diff %.3e", rel_diff),
      "< 1e-04")

check("survey mean vs sum(W_h * p_hat_h)",
      abs(survey_mean - sum(strata$W * p_hat)) < 1e-12,
      sprintf("%.12f", survey_mean),
      sprintf("%.12f", sum(strata$W * p_hat)))

# Reported, not hidden: the sample uses integer positive counts, so its SE is
# not Barnett's expected SD. Barnett's uses the true p_h. This is a difference
# in the input, not a disagreement between the two calculations.
cat(sprintf("\n  For contrast, not as a check:\n"))
cat(sprintf("    Barnett expected SD (true p_h)   %.4f pp\n", sd_pp))
cat(sprintf("    this sample's SE (integer counts) %.4f pp\n", survey_se * 100))
cat("    They differ because round(p_h * n_h) is not p_h * n_h.\n")
cat("    Block A is the anchor. Block B checks the call.\n")

# --------------------------------------------------------------------------
# The fixture. O-3: version and exact call recorded beside every fixture.
# --------------------------------------------------------------------------
fixture <- list(
  what = "Barnett Table 2B reproduction, and the svydesign() call it validates",
  deliverable = "D2.1",
  produced_by = "r/barnett_table_2b.R",
  environment = list(
    image_digest = "sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0",
    image_tag_at_pin = "rocker/r-ver:4.5.3",
    r_version = R.version.string,
    survey_version = as.character(packageVersion("survey")),
    cran_snapshot = getOption("repos")[["CRAN"]]
  ),
  exact_call = "svydesign(ids = ~1, strata = ~stratum, weights = ~w, data = sample_rows)",
  source = list(
    citation = paste("Barnett, A. YouTube's Violative View Rate Methodology:",
                     "A Statistical Assessment. MIT, September 2021."),
    register = "S-2.3",
    provenance_caveat = "Commissioned and funded by Google. Expert review, not peer review."
  ),
  table_2a_input = list(
    stratum = strata$name,
    W_h = strata$W,
    p_h = strata$p,
    n_total = n_total
  ),
  table_2b_published = list(
    allocation = published_allocation,
    vvr_pct = published_vvr_pct,
    expected_sd_pp = published_sd_pp
  ),
  table_2b_reproduced = list(
    allocation_raw = raw,
    allocation = as.numeric(allocation),
    vvr_pct = vvr * 100,
    expected_sd_pp = sd_pp,
    rounding_note = paste("Ordinary rounding; no tie-break is involved. Stratum 1's raw",
                          "value is 2098.4952, just under the midpoint, so it rounds to",
                          "2098 under any tie rule. It sits 0.005 from the midpoint, so a",
                          "different arithmetic path could tip it to 2099 and the total to",
                          "4001.")
  ),
  survey_call_check = list(
    positives = as.numeric(positives),
    p_hat = p_hat,
    survey_mean = survey_mean,
    survey_se = survey_se,
    closed_form_se = closed_form_se,
    relative_difference = rel_diff,
    variance_form = "with replacement, no finite-population correction"
  ),
  all_checks_passed = pass_all
)

out_dir <- "/fixtures"
if (dir.exists(out_dir)) {
  writeLines(toJSON(fixture, auto_unbox = TRUE, pretty = TRUE, digits = 15),
             file.path(out_dir, "barnett_table_2b.json"))
  cat(sprintf("\n  fixture written to %s/barnett_table_2b.json\n", out_dir))
} else {
  cat("\n  no /fixtures mount, fixture not written\n")
}

cat("\n")
if (pass_all) {
  cat("ALL CHECKS PASSED. The R witness reproduces Barnett Table 2B.\n")
  cat("The svydesign() call above may now be trusted as a witness.\n\n")
  quit(status = 0)
} else {
  cat("FAILED. The witness does not reproduce the published table.\n")
  cat("Nothing in Phase 2 may use this call until it does.\n\n")
  quit(status = 1)
}
