# Phase 2 -- coverage of the three candidate intervals, from R.
#
# WHY THIS EXISTS. C-30(c) was wrong three times because it asserted WHERE a
# derived property (width) holds. The root cause was asserting a region at all.
# Coverage has a definition, so it can be asserted instead of described.
#
# WHY IN R. Jeffreys needs Beta quantiles. `stats::qbeta` has them; this project
# deliberately has no incomplete beta anywhere in its own source, because that
# absence is what makes D2.4's Clopper-Pearson check independent. Computing
# Jeffreys here keeps that true and makes these numbers witness-produced rather
# than ours.
#
# THE INSTRUMENT PROVES ITSELF FIRST. D2.1's rule: a witness is validated before
# it witnesses anything. Block A reproduces three published limits from S-1.1
# (Brown, Cai & DasGupta 2001, full text read 2026-08-29). Only if those match
# does Block B's Jeffreys comparison mean anything.
#
# Anchor: S-1.1, DOI 10.1214/ss/1009213286.

suppressPackageStartupMessages(library(jsonlite))

# ---------------------------------------------------------------- the intervals

wilson_ci <- function(k, n, conf) {
  kappa <- qnorm(1 - (1 - conf) / 2)
  phat <- k / n
  centre <- (phat + kappa^2 / (2 * n)) / (1 + kappa^2 / n)
  half <- (kappa * sqrt(n) / (n + kappa^2)) * sqrt(phat * (1 - phat) + kappa^2 / (4 * n))
  c(max(0, centre - half), min(1, centre + half))
}

clopper_pearson_ci <- function(k, n, conf) {
  as.numeric(binom.test(k, n, conf.level = conf)$conf.int)
}

# S-1.1 section 3.1.3, equations (6)-(8). Equal-tailed Jeffreys, with the
# endpoint exceptions the paper specifies: LJ(0) = 0 and UJ(n) = 1.
jeffreys_ci <- function(k, n, conf) {
  a <- (1 - conf) / 2
  lower <- if (k == 0) 0 else qbeta(a, k + 0.5, n - k + 0.5)
  upper <- if (k == n) 1 else qbeta(1 - a, k + 0.5, n - k + 0.5)
  c(lower, upper)
}

# Exact coverage: sum the binomial pmf over every k whose interval contains p.
# No simulation.
coverage <- function(ci_fn, n, p, conf) {
  bounds <- lapply(0:n, function(k) ci_fn(k, n, conf))
  total <- 0
  for (k in 0:n) {
    b <- bounds[[k + 1]]
    if (b[1] <= p && p <= b[2]) total <- total + dbinom(k, n, p)
  }
  total
}

cat("\n")
cat("Coverage of Wilson, Clopper-Pearson and Jeffreys\n")
cat("=================================================\n")
cat(sprintf("  %s\n\n", R.version.string))

# --------------------------------------------- Block A: validate the instrument

cat("Block A -- reproduce S-1.1's published limits before trusting anything else\n")
cat("---------------------------------------------------------------------------\n")

checks <- list()
add_check <- function(label, got, want, tol) {
  ok <- abs(got - want) < tol
  checks[[length(checks) + 1]] <<- list(label = label, got = got, want = want, passed = ok)
  cat(sprintf("  [%s] %-52s got %.4f  want %.3f\n",
              if (ok) "PASS" else "FAIL", label, got, want))
  ok
}

# S-1.1 section 4.1.1: Wilson at p = 0.1765/n, 95%, limit 0.838.
add_check("S-1.1 4.1.1  Wilson p=0.1765/n conf=0.95",
          coverage(wilson_ci, 2000, 0.1765 / 2000, 0.95), 0.838, 5e-4)
# S-1.1 section 4.1.1: Wilson at p = 0.1174/n, 99%, limit 0.889.
add_check("S-1.1 4.1.1  Wilson p=0.1174/n conf=0.99",
          coverage(wilson_ci, 2000, 0.1174 / 2000, 0.99), 0.889, 5e-4)

# S-1.1 section 3.2: Wilson lim inf over gamma >= 1 at 95% is 0.92.
worst_wilson <- 1
for (g in seq(1, 11, by = 0.05)) {
  worst_wilson <- min(worst_wilson, coverage(wilson_ci, 1000, g / 1000, 0.95))
}
add_check("S-1.1 3.2    Wilson lim inf, gamma>=1, conf=0.95", worst_wilson, 0.920, 2e-3)

if (!all(vapply(checks, function(c) c$passed, logical(1)))) {
  stop("Block A failed: this script does not reproduce S-1.1, so Block B means nothing.")
}
cat("\n  Instrument validated. Block B may be trusted.\n\n")

# ------------------------------------------- Block B: the three-way comparison

cat("Block B -- the rare-event regime this tool exists for\n")
cat("------------------------------------------------------\n")
cat("  Worst coverage over p = gamma/n, gamma in [0.5, 15] STEP 0.25, vs nominal.\n")
cat("  A worst-over-a-grid figure is a property of the grid. A finer grid can only\n")
cat("  find a lower minimum, so these are UPPER BOUNDS on the worst case, not it.\n")
cat("  At step 0.05 the director measured 0.9537 where step 0.25 reports 0.9540.\n\n")

methods <- list(wilson = wilson_ci, clopper_pearson = clopper_pearson_ci, jeffreys = jeffreys_ci)
rows <- list()

cat(sprintf("  %6s %6s %12s %12s %12s\n", "n", "conf", "wilson", "clopper", "jeffreys"))
for (n in c(100, 500, 1000)) {
  for (conf in c(0.90, 0.95, 0.99)) {
    worst <- list()
    for (m in names(methods)) {
      w <- 1
      argmin <- NA
      for (g in seq(0.5, 15, by = 0.25)) {
        cov <- coverage(methods[[m]], n, g / n, conf)
        if (cov < w) { w <- cov; argmin <- g / n }
      }
      worst[[m]] <- list(coverage = w, at_p = argmin)
    }
    cat(sprintf("  %6d %6.2f %12.4f %12.4f %12.4f\n", n, conf,
                worst$wilson$coverage, worst$clopper_pearson$coverage, worst$jeffreys$coverage))
    rows[[length(rows) + 1]] <- list(
      n = n, conf = conf,
      wilson = worst$wilson, clopper_pearson = worst$clopper_pearson, jeffreys = worst$jeffreys
    )
  }
}

cat("\n  Reading: Clopper-Pearson never drops below nominal, by construction.\n")
cat("  Wilson and Jeffreys both can, and this table says by how much, where.\n\n")

fixture <- list(
  what = "Exact coverage of Wilson, Clopper-Pearson and Jeffreys in the rare-event regime",
  produced_by = "r/coverage_fixtures.R",
  why = paste(
    "C-30(c) asserted a region three times and was wrong three times. Coverage",
    "has a definition, so it is asserted instead. This fixture answers whether",
    "the blog's claim (Jeffreys over-covers for rare events) and S-1.1's claim",
    "(Jeffreys has excellent average coverage) are in conflict. They measure",
    "different quantities, so they may both be true."
  ),
  instrument_validated_against = "S-1.1 sections 3.2 and 4.1.1, published limits",
  validation = checks,
  exact_call = paste(
    "wilson: closed form, kappa = qnorm(1 - (1-conf)/2);",
    "clopper_pearson: binom.test(k, n, conf.level = conf)$conf.int;",
    "jeffreys: qbeta({alpha/2, 1-alpha/2}, k+0.5, n-k+0.5), with LJ(0)=0 and UJ(n)=1",
    "per S-1.1 section 3.1.3; coverage: sum(dbinom(k, n, p)) over k whose interval contains p"
  ),
  environment = list(
    image_digest = "sha256:c3f39b365d1077fe24f8e9ab2742e352b6d3950897f51af1624a5bb5550c21c0",
    r_version = R.version.string,
    cran_snapshot = getOption("repos")[["CRAN"]]
  ),
  standards = list(anchor = "S-1.1 Brown, Cai & DasGupta (2001), DOI 10.1214/ss/1009213286"),
  axes = list(
    varied = c("n", "conf", "p = gamma/n for gamma in [0.5, 15]"),
    grid_step = 0.25,
    held_fixed = c("none"),
    note = paste(
      "An agreement or coverage figure states its axes, and a WORST-over-a-grid",
      "figure states its grid too. A finer grid can only find a lower minimum, so",
      "every number here is an UPPER BOUND on the worst case rather than the worst",
      "case itself. At step 0.05 the director measured 0.9537 for clopper_pearson",
      "at n=1000 conf=0.95, where step 0.25 reports 0.9540. Both are correct for",
      "their grid, and neither is 'the' worst case."
    )
  ),
  rare_event_worst_coverage = rows
)

out_dir <- "/fixtures"
if (dir.exists(out_dir)) {
  writeLines(toJSON(fixture, auto_unbox = TRUE, pretty = TRUE, digits = 15),
             file.path(out_dir, "coverage.json"))
  cat(sprintf("  fixture written to %s/coverage.json\n\n", out_dir))
} else {
  cat("  no /fixtures mount, fixture not written\n\n")
}
