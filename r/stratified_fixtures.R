# Phase 2, D2.2 -- survey fixtures for stratified estimation and Neyman allocation.
#
# This script writes NO estimator. It records what R survey says, so that the
# Python estimators in D2.3 can be written against numbers that already existed.
#
# THE CALL DOES NOT DRIFT. D2.1 validated exactly one invocation against
# Barnett's published Table 2B:
#
#   svydesign(ids = ~1, strata = ~stratum, weights = ~w, data = <sample>)
#
# with no fpc, which is what makes it the with-replacement form S-2.3
# specifies. Every fixture below uses that call and nothing else. If a later
# deliverable needs a different design -- an fpc, a different variance form,
# clusters -- Barnett does not cover it, and it needs its own anchor recorded
# before it generates anything. The anchor covers the call it tested and no
# other. Director's condition, 2026-08-29.
#
# Neyman allocation is arithmetic, not a survey function: survey has no
# allocator. The allocation half is the same formula D2.1 reproduced against
# Barnett, so it is anchored by that reproduction rather than by survey.

suppressPackageStartupMessages({
  library(survey)
  library(jsonlite)
})

# --------------------------------------------------------------------------
# The one validated call, in one place, so it cannot drift between fixtures.
# --------------------------------------------------------------------------
VALIDATED_CALL <- "svydesign(ids = ~1, strata = ~stratum, weights = ~w, data = sample_rows)"

stratified_design <- function(sample_rows) {
  svydesign(ids = ~1, strata = ~stratum, weights = ~w, data = sample_rows)
}

# Build a sample: n_h units in stratum h, k_h of them positive, weights summing
# to the stratum's population share W_h so svymean returns sum(W_h * p_hat_h).
build_sample <- function(names, W, n, k) {
  stopifnot(length(names) == length(W), length(W) == length(n), length(n) == length(k))
  stopifnot(all(k >= 0), all(k <= n), all(n >= 1))
  do.call(rbind, lapply(seq_along(names), function(h) {
    data.frame(
      stratum = names[h],
      y = c(rep(1L, k[h]), rep(0L, n[h] - k[h])),
      w = W[h] / n[h],
      stringsAsFactors = FALSE
    )
  }))
}

# Neyman (optimal) allocation. S-1.2 Neyman (1934), S-1.3 Cochran 3rd ed.
# The formula D2.1 reproduced against Barnett Table 2B.
neyman <- function(W, p, n_total) {
  S_h <- sqrt(p * (1 - p))
  raw <- n_total * (W * S_h) / sum(W * S_h)
  list(raw = raw, allocation = round(raw))
}

# Proportional allocation, for the contrast the estimator will need to make.
proportional <- function(W, n_total) {
  raw <- n_total * W / sum(W)
  list(raw = raw, allocation = round(raw))
}

estimate <- function(label, note, names, W, n, k) {
  sample_rows <- build_sample(names, W, n, k)
  design <- stratified_design(sample_rows)
  est <- svymean(~y, design)
  ci <- confint(est, level = 0.95)

  cat(sprintf("  %-26s n=%-6d estimate=%.12f  se=%.12f\n",
              label, sum(n), as.numeric(coef(est)), as.numeric(SE(est))))

  list(
    label = label,
    note = note,
    call = VALIDATED_CALL,
    strata = names,
    W_h = W,
    n_h = n,
    k_h = k,
    p_hat_h = k / n,
    n_total = sum(n),
    estimate = as.numeric(coef(est)),
    se = as.numeric(SE(est)),
    ci_lower_95 = as.numeric(ci[1]),
    ci_upper_95 = as.numeric(ci[2]),
    df = as.numeric(degf(design))
  )
}

cat("\n")
cat("D2.2 -- survey fixtures for stratified estimation\n")
cat("=================================================\n")
cat(sprintf("  %s\n", R.version.string))
cat(sprintf("  survey %s\n", as.character(packageVersion("survey"))))
cat(sprintf("  call:  %s\n\n", VALIDATED_CALL))

# --------------------------------------------------------------------------
# Allocation fixtures. Arithmetic, anchored by D2.1's Barnett reproduction.
# --------------------------------------------------------------------------
cat("Allocation\n")
cat("----------\n")

barnett_W <- c(0.80, 0.10, 0.05, 0.01, 0.04)
barnett_p <- c(0.0005, 0.0050, 0.0100, 0.0500, 0.0025)
barnett_names <- c("lowest_risk", "low_risk", "middle_risk", "high_risk", "no_score")

allocations <- list(
  list(
    label = "barnett_neyman_4000",
    note = paste("The D2.1 anchor, carried forward as an allocation fixture.",
                 "Reproduces Barnett Table 2B exactly."),
    method = "neyman",
    strata = barnett_names, W_h = barnett_W, p_h = barnett_p, n_total = 4000,
    result = neyman(barnett_W, barnett_p, 4000)
  ),
  list(
    label = "barnett_proportional_4000",
    note = paste("Same frame, proportional allocation. The contrast that shows",
                 "what Neyman buys: it moves sample into the high-variance strata."),
    method = "proportional",
    strata = barnett_names, W_h = barnett_W, p_h = barnett_p, n_total = 4000,
    result = proportional(barnett_W, 4000)
  ),
  list(
    label = "two_stratum_neyman_1000",
    note = "The smallest case worth pinning. Hand-checkable.",
    method = "neyman",
    strata = c("low", "high"), W_h = c(0.9, 0.1), p_h = c(0.001, 0.20), n_total = 1000,
    result = neyman(c(0.9, 0.1), c(0.001, 0.20), 1000)
  ),
  list(
    label = "rare_event_neyman_5000",
    note = paste("The regime this tool exists for. Every stratum rate below 1%,",
                 "which is where the interval choice in S-1.1 matters most."),
    method = "neyman",
    strata = c("bulk", "flagged", "appealed"),
    W_h = c(0.95, 0.04, 0.01), p_h = c(0.0002, 0.0060, 0.0090), n_total = 5000,
    result = neyman(c(0.95, 0.04, 0.01), c(0.0002, 0.0060, 0.0090), 5000)
  )
)

for (a in allocations) {
  total <- sum(a$result$allocation)
  drift <- total - a$n_total
  flag <- if (drift == 0) "" else sprintf("   <<< %+d against n", drift)
  cat(sprintf("  %-28s %-13s %s  (sum %d)%s\n",
              a$label, a$method,
              paste(a$result$allocation, collapse = "/"),
              total, flag))
}

# Rounding a proportional split does not have to land on n, and here it does
# not. Barnett's case happens to; `rare_event_neyman_5000` is one short.
#
# Surfaced rather than absorbed, because it is a decision the estimator cannot
# make on its own: hand the remainder to one stratum (which one?), refuse, or
# report the sample as the size it actually is. Each answer changes a
# pre-registered design after the operator wrote it, which is V-1's class.
# Numbered question for the director. No code until it is ruled.
drifting <- Filter(function(a) sum(a$result$allocation) != a$n_total, allocations)
if (length(drifting) > 0) {
  cat("\n  ROUNDING DOES NOT ALWAYS SUM TO n:\n")
  for (a in drifting) {
    cat(sprintf("    %-28s asked for %d, allocation sums to %d\n",
                a$label, a$n_total, sum(a$result$allocation)))
    cat(sprintf("      raw: %s\n", paste(sprintf("%.4f", a$result$raw), collapse = " / ")))
  }
  cat("  Unruled. See the fixture's `open_question` field.\n")
}

# Q2's floor, recorded as data rather than as prose. A stratum allocated fewer
# than 2 units has zero within-stratum degrees of freedom, so its variance
# contribution is undefined. ALLOCATION_TOO_THIN refuses on this.
thin_W <- c(0.98, 0.02)
thin_p <- c(0.05, 0.0001)
thin <- neyman(thin_W, thin_p, 300)
cat(sprintf("\n  Q2 floor case: %s -> stratum 2 gets %d unit(s)\n",
            paste(sprintf("%.3f", thin$raw), collapse = " / "),
            thin$allocation[2]))
cat("  A stratum with fewer than 2 units has no within-stratum variance.\n")
cat("  ALLOCATION_TOO_THIN refuses at sample time. This is the fixture for it.\n")

# --------------------------------------------------------------------------
# Estimation fixtures. All through the one validated call.
# --------------------------------------------------------------------------
cat("\n")
cat("Estimation\n")
cat("----------\n")

estimates <- list(
  estimate(
    "barnett_design",
    "Barnett's allocation, with the nearest whole number of positives to each rate.",
    barnett_names, barnett_W,
    n = as.integer(allocations[[1]]$result$allocation),
    k = as.integer(round(barnett_p * allocations[[1]]$result$allocation))
  ),
  estimate(
    "two_stratum_balanced",
    "Small and hand-checkable. Both strata well inside the interval's comfort zone.",
    c("low", "high"), c(0.9, 0.1),
    n = c(500L, 500L), k = c(25L, 100L)
  ),
  estimate(
    "rare_event",
    "Low prevalence throughout -- the regime the intervals were chosen for.",
    c("bulk", "flagged", "appealed"), c(0.95, 0.04, 0.01),
    n = c(3000L, 1500L, 500L), k = c(3L, 12L, 7L)
  ),
  estimate(
    "one_stratum_zero_positives",
    paste("A stratum with no positives at all. Its within-stratum variance is",
          "zero, so it contributes nothing to the SE -- which is correct and",
          "surprising, and is why this is pinned."),
    c("clean", "dirty"), c(0.7, 0.3),
    n = c(400L, 200L), k = c(0L, 18L)
  ),
  estimate(
    "minimum_viable_stratum",
    paste("Two units in one stratum -- exactly Q2's floor. One unit would leave",
          "its variance undefined; two is the smallest that works."),
    c("bulk", "tiny"), c(0.99, 0.01),
    n = c(998L, 2L), k = c(40L, 1L)
  )
)

# --------------------------------------------------------------------------
# Write the fixture.
# --------------------------------------------------------------------------
fixture <- list(
  what = "R survey fixtures for stratified estimation and Neyman allocation",
  deliverable = "D2.2",
  produced_by = "r/stratified_fixtures.R",
  generated_before_any_estimator = TRUE,
  ordering_note = paste("R2.2: every estimator in D2.3 is written against these",
                        "numbers, which existed first. A test cannot agree with an",
                        "implementation for the same wrong reason when the expected",
                        "value predates the implementation."),
  validated_call = VALIDATED_CALL,
  call_provenance = paste("This exact call was validated against Barnett Table 2B in",
                          "D2.1 (r/barnett_table_2b.R). No fixture here uses any other",
                          "design. A different design is not covered by that anchor."),
  environment = list(
    image_digest = "sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0",
    r_version = R.version.string,
    survey_version = as.character(packageVersion("survey")),
    cran_snapshot = getOption("repos")[["CRAN"]]
  ),
  standards = list(
    allocation = "S-1.2 Neyman (1934); S-1.3 Cochran 3rd ed.; reproduction anchor S-2.3",
    variance = "with replacement, no finite-population correction (S-2.3)",
    estimation = "S-2.1 R survey 4.5"
  ),
  open_question = list(
    id = "Q4 (proposed)",
    title = "Rounded Neyman allocation does not always sum to n",
    found_by = "D2.2 fixture generation, 2026-08-29",
    evidence = paste("rare_event_neyman_5000: raw 3844.9/883.9/270.2 rounds to",
                     "3845/884/270, which sums to 4999 against a requested 5000.",
                     "Barnett's case sums exactly, so D2.1 did not surface this."),
    why_it_needs_a_ruling = paste("The estimator cannot decide alone. Handing the",
                                  "remainder to a stratum changes a pre-registered",
                                  "design after the operator wrote it, which is V-1's",
                                  "class. Refusing costs an operator a usable plan over",
                                  "one unit. Reporting the sample at its true size is",
                                  "honest but silently delivers less than was asked."),
    status = "UNRULED -- no code until the director rules"
  ),
  allocation_fixtures = allocations,
  q2_floor_case = list(
    note = paste("Neyman allocates fewer than 2 units to stratum 2. Zero",
                 "within-stratum degrees of freedom, so its variance contribution",
                 "is undefined. ALLOCATION_TOO_THIN refuses here."),
    W_h = thin_W, p_h = thin_p, n_total = 300,
    raw = thin$raw, allocation = thin$allocation
  ),
  estimation_fixtures = estimates
)

out_dir <- "/fixtures"
if (dir.exists(out_dir)) {
  writeLines(toJSON(fixture, auto_unbox = TRUE, pretty = TRUE, digits = 15),
             file.path(out_dir, "stratified.json"))
  cat(sprintf("\n  fixture written to %s/stratified.json\n", out_dir))
} else {
  cat("\n  no /fixtures mount, fixture not written\n")
}

cat("\n")
cat(sprintf("%d allocation fixtures, %d estimation fixtures, one validated call.\n",
            length(allocations), length(estimates)))
cat("No estimator code was written by this script.\n\n")
