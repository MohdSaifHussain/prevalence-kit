# Prevalence report

**0.800%**  (95% interval 0.406% to 1.571%)

8 of 1000 sampled items were positive.

## What was measured

- **Estimand:** Comments scored toxic by at least ninety percent of annotators
- **Positive when:** `toxicity` at_least `0.9`
- **Population:** frame.txt
- **Design:** srs, seed `coverage-demo-full-chain-2026-08-31`
- **Frame:** 1999514 rows read, 1999514 unique items sampled from
- **Interval method:** wilson

## What that 95% actually delivers

Measured, not asserted. Worst coverage for `wilson` at a nominal 95%: **90.98%**, at n = 1000, p = gamma/n, gamma in [0.5, 15] step 0.25.

That is the worst value found on a *grid* of true rates, so the real worst is **at most** this and may be lower. It is rounded down rather than to nearest, because rounding a bound toward the middle claims a floor the measurement already breaks.

**Where this run sits, on both axes.** True rate: gamma = p x n = 8.000, inside the swept range 0.5 to 15. Sample size: n = 1000, one of the sizes measured.

The figure above is what the method does at the sizes and rates that were measured. **It is not a coverage computed for this run, and none was computed.** Coverage oscillates with sample size, so a worst case at one n does not bound another.

## The record

Pre-registration hash: `3f5db3b38def7700f0b7c23fe151969864a409566d1759ac4615f4917266e141`

| # | Step | Recorded at | Entry digest |
|---|---|---|---|
| 0 | plan | 2026-08-31T01:46:53Z | `3749371bb7941d08` |
| 1 | sample | 2026-08-31T01:47:14Z | `b64014e79618d75a` |
| 2 | ingest-labels | 2026-08-31T01:47:16Z | `ecade5ae86b22f05` |
| 3 | estimate | 2026-08-31T01:47:16Z | `ac8cc9d25244556e` |

**This is the chain as at emission: 4 entries.** Emitting this report appends one further entry, so `prevalence-kit verify` on this run will report **5 entries**. A report cannot list its own emission; the difference is that entry, not a discrepancy.

Anyone can re-check this with `prevalence-kit verify`. It redraws the sample and recomputes the estimate from the sealed record, rather than re-reading the numbers above.

## Honest limits

Read these before quoting the number.

- It measures prevalence of labeled samples from a defined population. It cannot fix a bad sampling frame, biased labels, or a dishonest plan. It can only make them visible and permanent in the record.
- The interval is a SAMPLING interval. It does not account for rater quality. This is the same caveat YouTube publishes for its Violative View Rate: "The confidence intervals do not take into account rater quality, which may impact our measurements."
- This version relies on the sensitivity and specificity you provide, if you provide them. It does not estimate rater quality itself.
- No EU regulation requires this number. The word "prevalence" appears zero times in Regulation (EU) 2022/2065 and zero times in Implementing Regulation (EU) 2024/2835.
- Validation is on synthetic data and one public dataset. No claim of production deployment.
- Built by directing an AI under a governed process. The director wrote none of the code and all of the decisions.

_Emitted 2026-08-31T01:47:49Z by prevalence-kit._
