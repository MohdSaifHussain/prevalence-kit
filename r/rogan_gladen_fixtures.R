# Phase 2, D2.5 -- Rogan-Gladen fixtures from epiR::epi.prev().
#
# No estimator code. This records what the witness says, so the Python
# correction can be written against numbers that already existed. R2.2.
#
# THE WITNESS, AND WHAT IT DOES NOT ESTABLISH. O-8 said Rogan-Gladen has no
# library witness. That was true of survey and svy, not of the world. epiR
# implements it, and its intervals follow Reiczigel et al. (2010) -- S-1.6, the
# paper matching our assumption that Se and Sp are supplied and exact (D-31).
#
# But Jeno Reiczigel is a listed CONTRIBUTOR to epiR. So this is the method
# author's own implementation of the method author's own paper. It confirms we
# implement the method as its author does. It does NOT independently confirm
# the method. Barnett Table 2B is a published table computed without reference
# to any implementation; this is not that.
#
# VERSION. epiR 2.0.92, which is what the frozen 2026-04-23 snapshot serves.
# 2.0.96 is current on CRAN and outside the snapshot. The 2.0.96 manual
# documents a `tp.method` argument that 2.0.92 does not have. The witness's
# documentation is not the witness -- only the pinned build is. C-25.
#
# WHAT THIS FIXTURE RECORDS THAT A PLAIN FIXTURE WOULD NOT. For every failing
# case it records BOTH what epiR does and what prevalence-kit will do. Two tools
# meeting the same input and behaving differently, both deliberately, with the
# difference written down. That pairing is the evidence for our disclosure, and
# it is more useful than either behaviour alone.

suppressPackageStartupMessages({
  library(epiR)
  library(jsonlite)
})

stopifnot(as.character(packageVersion("epiR")) == "2.0.92")
# THE SECOND AXIS, added 2026-08-29.
#
# This fixture varied pos, tested, se and sp, and held conf.level at 0.95. So
# every agreement figure taken from it described the estimator at one confidence
# level while reading as a statement about the estimator.
#
# F-8 made it concrete: `confidence` was unvalidated in every interval
# estimator, and no fixture could have caught it, because none varied it.
#
# epi.prev takes conf.level, so closing this costs a loop.
CONF_LEVELS <- c(0.90, 0.95, 0.99)
PRIMARY <- 0.95

cases <- list()

add <- function(label, pos, tested, se, sp, ours, note) {
  for (conf in CONF_LEVELS) {
    warned <- character(0)
    r <- withCallingHandlers(
      epi.prev(pos = pos, tested = tested, se = se, sp = sp,
               method = "c-p", units = 1, conf.level = conf),
      warning = function(w) {
        warned <<- c(warned, conditionMessage(w))
        invokeRestart("muffleWarning")
      }
    )

    # The Rogan-Gladen denominator, recorded so a reader can see why a case
    # fails without recomputing it.
    denominator <- se + sp - 1
    ap <- pos / tested

    cases[[length(cases) + 1]] <<- list(
      label = label, note = note, conf = conf,
      pos = pos, tested = tested, se = se, sp = sp,
      apparent = ap,
      denominator = denominator,
      ap_est = r$ap$est, ap_lower = r$ap$lower, ap_upper = r$ap$upper,
      tp_est = r$tp$est, tp_lower = r$tp$lower, tp_upper = r$tp$upper,
      # An interval whose lower bound exceeds its upper bound is not an
      # interval. Recorded as data rather than described, because it is the
      # argument.
      tp_interval_inverted = isTRUE(r$tp$lower > r$tp$upper),
      epiR_warned = length(warned) > 0,
      epiR_warning = if (length(warned)) warned else NULL,
      prevalence_kit = ours
    )
  }
}

cat("\n")
cat("D2.5 -- Rogan-Gladen fixtures from epiR::epi.prev()\n")
cat("===================================================\n")
cat(sprintf("  %s\n", R.version.string))
cat(sprintf("  epiR %s (pinned; 2.0.96 is current on CRAN, outside the snapshot)\n\n",
            as.character(packageVersion("epiR"))))

# ---------------------------------------------------------------- well defined
add("ordinary", 45, 150, 0.96, 0.89, "accept",
    "epiR's own worked example 1: brucellosis screening, 45 of 150 positive.")
add("rare_event", 8, 4000, 0.90, 0.999, "accept",
    paste("The regime this tool exists for. AP 0.2% against 1 - Sp = 0.1%, so the",
          "correction is defined. Specificity has to be this high for a rare-event",
          "measurement to survive it, which is the point below."))
add("perfect_test", 8, 4000, 1.00, 1.00, "accept",
    "A perfect test. The correction is the identity and must not disturb anything.")
add("zero_positives_perfect_sp", 0, 4000, 0.90, 1.00, "accept",
    paste("NO VIOLATIONS FOUND, and a specificity of 1 makes that meaningful.",
          "Point estimate 0 with a real upper bound. The contract once called",
          "this 'no information' and would have refused it. It is the product."))
add("all_positive_perfect_se", 4000, 4000, 1.00, 0.99, "accept",
    "The mirror case at the top end. Well defined, must not refuse.")

# -------------------------------------------- out of range: plan vs the sample
add("below_one_minus_sp", 6, 151, 0.964, 0.927, "refuse CORRECTION_OUT_OF_RANGE",
    paste("epiR's own worked example 2, and a PUBLISHED failure case.",
          "AP 3.97% sits below 1 - Sp = 7.3%, so the corrected estimate is",
          "negative. epiR warns and returns it; we refuse."))
add("fpr_exceeds_prevalence", 8, 4000, 0.90, 0.99, "refuse CORRECTION_OUT_OF_RANGE",
    paste("THE CENTRAL DIFFICULTY OF RARE-EVENT MEASUREMENT, and it is why this",
          "case is here by name. Apparent prevalence is 0.2%. The classifier's",
          "false-positive rate, 1 - Sp, is 1%. The test would produce five times",
          "more apparent positives from clean content alone than were observed,",
          "so the stated Sp and the sample cannot both be right and the corrected",
          "estimate is negative.",
          "A 99% specificity sounds excellent and is useless at 0.2% prevalence.",
          "This case was first written into this fixture labelled 'accept', with a",
          "note claiming AP sat comfortably above 1 - Sp. It does not: 0.2% is",
          "below 1%. The witness warned and the arithmetic disagreed with the",
          "note, which is why fixtures come before estimators."))
add("zero_positives_imperfect_sp", 0, 4000, 0.90, 0.99, "refuse CORRECTION_OUT_OF_RANGE",
    paste("Zero positives with an imperfect test. The false-positive rate alone",
          "would produce about 1% apparent prevalence, so observing 0% means the",
          "sample disagrees with the stated Sp. Two artifacts that each look",
          "fine -- D-22's fourth case."))
add("above_se", 4000, 4000, 0.90, 0.99, "refuse CORRECTION_OUT_OF_RANGE",
    "Apparent prevalence above the stated sensitivity. Corrected estimate exceeds 1.")

# ------------------------------------------ undefined: the Se/Sp pair itself
add("denominator_zero", 40, 1000, 0.60, 0.40, "refuse CORRECTION_UNDEFINED",
    paste("Se + Sp = 1 exactly. The denominator vanishes and epiR returns -Inf.",
          "Nothing to print."))
add("denominator_negative", 40, 1000, 0.60, 0.30, "refuse CORRECTION_UNDEFINED",
    paste("Se + Sp < 1. epiR returns a point estimate AND AN INVERTED INTERVAL --",
          "lower above upper. That is the argument for refusing: not a policy",
          "choice over a working alternative, but declining to print something",
          "that is not an interval."))

# ------------------------------------------------------------------- report
cat(sprintf("  %-28s %9s %11s %12s  %s\n",
            "case", "AP", "Se+Sp-1", "epiR tp", "prevalence-kit"))
for (c in cases) {
  mark <- if (c$tp_interval_inverted) " [INVERTED]" else if (c$epiR_warned) " [warned]" else ""
  cat(sprintf("  %-28s %9.6f %11.3f %12.6f  %s%s\n",
              c$label, c$apparent, c$denominator, c$tp_est, c$prevalence_kit, mark))
}

accepted <- sum(vapply(cases, function(c) c$prevalence_kit == "accept", logical(1)))
inverted <- sum(vapply(cases, function(c) isTRUE(c$tp_interval_inverted), logical(1)))
cat(sprintf("\n  %d cases: %d we accept, %d we refuse. %d epiR intervals are inverted.\n",
            length(cases), accepted, length(cases) - accepted, inverted))

fixture <- list(
  what = "Rogan-Gladen corrected prevalence, from epiR::epi.prev()",
  deliverable = "D2.5",
  produced_by = "r/rogan_gladen_fixtures.R",
  generated_before_any_estimator = TRUE,
  exact_call = "epi.prev(pos, tested, se, sp, method = \"c-p\", units = 1, conf.level = conf), for conf in {0.90, 0.95, 0.99}",
  witness_note = paste(
    "epiR implements Rogan-Gladen; its intervals follow Reiczigel et al. (2010),",
    "S-1.6, which assumes Se and Sp are known -- our assumption, D-31.",
    "Jeno Reiczigel is a listed contributor to epiR, so this is the method",
    "author's own implementation of the method author's own paper. It confirms",
    "we implement the method as its author does. It does not independently",
    "confirm the method."
  ),
  version_note = paste(
    "epiR 2.0.92, what the frozen 2026-04-23 snapshot serves. 2.0.96 is current",
    "on CRAN and outside the snapshot, and its manual documents a tp.method",
    "argument 2.0.92 does not have. The witness's documentation is not the",
    "witness; only the pinned build is. C-25."
  ),
  pairing_note = paste(
    "Every case records what epiR did and what prevalence-kit does. Where they",
    "differ, both behaviours are deliberate and the difference is the evidence",
    "for our disclosure."
  ),
  disclosure = paste(
    "Where we refuse, this version refuses. A published 2026 method -- Kopacka",
    "and Fuchs, Prev. Vet. Med. 253, DOI 10.1016/j.prevetmed.2026.106891 --",
    "addresses these cases and is not implemented here. Cited as published work,",
    "not as a package feature: our pinned epiR does not implement it either."
  ),
  environment = list(
    image_digest = "sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0",
    r_version = R.version.string,
    epiR_version = as.character(packageVersion("epiR")),
    cran_snapshot = getOption("repos")[["CRAN"]]
  ),
  standards = list(
    estimator = "S-1.4 Rogan & Gladen (1978), DOI 10.1093/oxfordjournals.aje.a112510",
    interval = "S-1.6 Reiczigel, Foldi & Ozsvari (2010), DOI 10.1017/s0950268810000385",
    witness = "S-1.10 epiR 2.0.92",
    not_implemented = "S-1.5 Lang & Reiczigel (2014); S-1.11 Kopacka & Fuchs (2026)"
  ),
  confidence = PRIMARY,
  confidence_levels = CONF_LEVELS,
  axes = list(
    varied = c("pos", "tested", "se", "sp", "conf"),
    held_fixed = c("method = c-p"),
    note = paste(
      "Every agreement figure taken from this fixture must state its axes.",
      "Before 2026-08-29 conf was pinned at 0.95 and the figures did not say so.",
      "method stays c-p: Q7 ships no other corrected interval, so no other is witnessed."
    )
  ),
  cases = cases
)

out_dir <- "/fixtures"
if (dir.exists(out_dir)) {
  writeLines(toJSON(fixture, auto_unbox = TRUE, pretty = TRUE, digits = 15),
             file.path(out_dir, "rogan_gladen.json"))
  cat(sprintf("\n  fixture written to %s/rogan_gladen.json\n", out_dir))
} else {
  cat("\n  no /fixtures mount, fixture not written\n")
}

cat("\nNo estimator code was written by this script.\n\n")
