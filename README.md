# prevalence-kit

**Pre-release. Phase 3 of 4 in progress. Nothing here is ready to rely on yet.**

Audit-grade prevalence measurement for Trust & Safety.

You give it a sampling plan and human labels. It gives back a prevalence estimate, an honest
confidence interval, a sealed copy of the content, a tamper-evident record of every step, and a
stamped report.

**No AI ever touches the evidence or the estimate.**

## What this is, and what it is not

**It is the governance, label-quality and audit layer.** Pre-registration, sealed content, a chain
that can say no, and a report an auditor can check.

**It is not a survey-statistics library.** [`svy`](https://github.com/samplics-org/svy) is, and it is
good — stratified sampling, Neyman allocation, Wilson and Clopper-Pearson intervals, Taylor
linearization, post-stratification. R [`survey`](https://cran.r-project.org/package=survey) has
covered this since 2003. **Our estimators are validated against both.** We do not claim to fill an
estimator gap, because there isn't one.

What neither of them does is seal content, keep a tamper-evident record, or refuse to print a number
it cannot defend. That is the gap.

## Honest limits

- It measures prevalence of labeled samples from a defined population. It **cannot fix a bad
  sampling frame, biased labels, or a dishonest plan.** It can only make them visible and permanent
  in the record.
- **Interval guarantees are sampling-only.** They do not account for rater quality — the same caveat
  YouTube publishes for its Violative View Rate.
- **No EU regulation requires the number this tool produces.** The word "prevalence" appears zero
  times in the Digital Services Act and zero times in Implementing Regulation (EU) 2024/2835. What
  those do mandate is classifier accuracy, precision and recall — and, in the guidance, sensitivity
  and specificity. This tool shows what those mandated quantities do to a prevalence estimate.
- Validation is on synthetic data and one public dataset. **No claim of production deployment.**
- Built by directing an AI under a governed process. The director wrote none of the code and all of
  the decisions.

## The record

Every claim above is checked against a primary source and pinned by version, date or DOI.

| | |
|---|---|
| [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) | What is being built, and the cap on it |
| [`docs/PHASE-0-VERIFICATION.md`](docs/PHASE-0-VERIFICATION.md) | 24 claims checked; 6 defects found and recorded |
| [`docs/STANDARDS.md`](docs/STANDARDS.md) | Every source, pinned |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Why each choice was made, and what was rejected |
| [`docs/CORRECTIONS.md`](docs/CORRECTIONS.md) | What we got wrong, and where it came from |
| [`SECURITY.md`](SECURITY.md) | What it protects, from whom, and what it does not |

## Licence

MIT.
