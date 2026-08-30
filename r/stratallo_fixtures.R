# D2.16 -- stratallo fixtures. FIXTURE ONLY. No estimator is built from this.
#
# S-1.12. `stratallo` 3.0.1 is inside the pinned CRAN snapshot (2026-04-23), so it
# needs no new pin and no network call the witness image does not already make.
# Found by going to official sources on stratified design, and it is the third
# "no witness exists" claim this project made and got wrong.
#
# WHAT THIS WITNESSES, AND WHAT IT DOES NOT
#
# Two things, and the second is the one that had nothing:
#
#   var_st / var_stsi  -- the stratified variance. Already witnessed by `survey`
#                         (D2.3, worst disagreement 9.5e-15). This is a SECOND
#                         opinion on work already checked.
#
#   round_oric         -- integer rounding of a fractional allocation. This is
#                         the FIRST outside check D-30's largest-remainder rule
#                         has ever had from R. `survey` has no allocator at all
#                         (F-9), and `svy` gave it its first witness of any kind
#                         in D2.9.
#
# THE NARROWING TRAVELS WITH IT, in the same words as epiR's:
#
#   `stratallo` is the algorithm authors' own implementation of their own papers.
#   It confirms we compute what they compute. It does NOT independently confirm
#   the method. That is a different kind of evidence from Barnett Table 2B, which
#   is a published table produced without reference to any implementation.
#
# RNABOX IS NOT ADOPTED. `rnabox` implements box-constrained optimum allocation
# (Wojciak et al., Survey Methodology 2024). It is a better method on the thing it
# optimises and it is deferred on SCOPE, not on witness -- charter NEXT queue.

suppressPackageStartupMessages({
  library(stratallo)
  library(jsonlite)
})

stopifnot(packageVersion("stratallo") == "3.0.1")

# The three Neyman allocations this project ships, as W_h and p_h.
cases <- list(
  list(
    label = "barnett_neyman_4000",
    W = c(0.8, 0.1, 0.05, 0.01, 0.04),
    p = c(0.0005, 0.005, 0.01, 0.05, 0.0025),
    n = 4000
  ),
  list(
    label = "two_stratum_neyman_1000",
    W = c(0.9, 0.1),
    p = c(0.001, 0.20),
    n = 1000
  ),
  list(
    label = "rare_event_neyman_5000",
    W = c(0.95, 0.04, 0.01),
    p = c(0.0002, 0.0060, 0.0090),
    n = 5000
  )
)

FRAME <- 1000000

fixtures <- list()
for (case in cases) {
  N_h <- round(case$W * FRAME)
  S_h <- sqrt(case$p * (1 - case$p))

  # The raw Neyman allocation, as arithmetic rather than as a stratallo call:
  # `rna` solves a constrained problem and would answer a different question.
  # What stratallo witnesses here is the ROUNDING, which is the half with no
  # external check, so the raw input is stated explicitly and only the rounding
  # is handed over.
  raw <- case$n * (N_h * S_h) / sum(N_h * S_h)

  rounded <- stratallo::round_oric(raw)

  # var_stsi(x, N, S) is the stratified-SIMPLE-RANDOM-SAMPLING form: allocation,
  # stratum sizes, stratum standard deviations. `var_st` takes a different
  # parameterisation (x, A, A0) and answers a different question.
  #
  # Whether stratallo's variance includes a finite-population correction is NOT
  # assumed here -- it is recorded and compared on the Python side, because
  # S-2.3 specifies the WITH-REPLACEMENT form and a silent fpc would make the
  # two disagree for a reason that is about the design, not the arithmetic.
  variance <- stratallo::var_stsi(x = rounded, N = N_h, S = S_h)

  fixtures[[length(fixtures) + 1]] <- list(
    label = case$label,
    W_h = case$W,
    p_h = case$p,
    n_total = case$n,
    N_h = N_h,
    raw = raw,
    round_oric = rounded,
    var_stsi = variance
  )

  cat(sprintf(
    "  %-26s round_oric %s  (sums to %d)\n",
    case$label, paste(rounded, collapse = "/"), sum(rounded)
  ))
}

# A rounding sweep, so agreement is a measurement with a stated space rather
# than three cases that happen to line up.
set.seed(20260830)
sweep <- list()
for (i in 1:2000) {
  k <- sample(2:6, 1)
  w <- runif(k, 0.01, 1)
  w <- w / sum(w)
  p <- runif(k, 0.0005, 0.5)
  n <- sample(2 * k:20000, 1)
  N_h <- round(w * FRAME)
  S_h <- sqrt(p * (1 - p))
  raw <- n * (N_h * S_h) / sum(N_h * S_h)
  sweep[[i]] <- list(
    raw = raw,
    n_total = n,
    round_oric = stratallo::round_oric(raw)
  )
}

out <- list(
  what = "stratallo fixtures for D2.16 -- rounding and stratified variance",
  deliverable = "D2.16",
  register = "S-1.12",
  fixture_only = TRUE,
  narrowing = paste(
    "stratallo is the algorithm authors' own implementation of their own",
    "papers. It confirms we compute what they compute. It does NOT",
    "independently confirm the method -- a different kind of evidence from",
    "Barnett Table 2B, which is a published table produced without reference",
    "to any implementation."
  ),
  environment = list(
    # The digest is what makes this reproducible by a stranger, and
    # tests/test_fixtures.py asserts it against the register. Every other
    # fixture in this directory carries it; this one omitted it and the check
    # caught that on its first run, which is what the check is for.
    image_digest = "sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0",
    image_tag_at_pin = "rocker/r-ver:4.5.3",
    r_version = R.version.string,
    stratallo_version = as.character(packageVersion("stratallo")),
    cran_snapshot = "https://p3m.dev/cran/__linux__/noble/2026-04-23"
  ),
  # `exact_call`, not a name of my own: the fixture check reads this key and a
  # near-miss spelling would have been a fixture whose provenance no instrument
  # could see.
  exact_call = paste(
    "stratallo::round_oric(raw)  and",
    "stratallo::var_stsi(x = rounded, N = N_h, S = S_h)"
  ),
  frame_total = FRAME,
  sweep_space = paste(
    "2000 designs, seed 20260830: 2-6 strata, weights ~ U(0.01, 1) normalised,",
    "p ~ U(0.0005, 0.5), n ~ U(2k, 20000)."
  ),
  fixtures = fixtures,
  sweep = sweep
)

write(toJSON(out, auto_unbox = TRUE, digits = 15, pretty = TRUE),
      file = "/fixtures/stratallo.json")
cat("wrote r/fixtures/stratallo.json\n")
