# Prevalence report

**6.800%**  (95% interval 5.319% to 8.541%)

68 of 1000 sampled items were positive.

## What was measured

- **Estimand:** Civil Comments validation split, comments at least half of annotators called toxic
- **Positive when:** `toxicity` at_least `0.5`
- **Population:** frame.txt
- **Design:** srs, seed `real-data-example-2026-08-31`
- **Frame:** 97320 rows read, 97320 unique items sampled from
- **Interval method:** clopper-pearson

## What that 95% actually delivers

Measured, not asserted. Worst coverage for `clopper_pearson` at a nominal 95%: **95.20%**, at n = 500, p = gamma/n, gamma in [0.5, 15] step 0.25.

That is the worst value found on a *grid* of true rates, so the real worst is **at most** this and may be lower. It is rounded down rather than to nearest, because rounding a bound toward the middle claims a floor the measurement already breaks.

**Where this run sits, on both axes.** True rate: gamma = p x n = 68.000, outside the swept range 0.5 to 15. Sample size: n = 1000, one of the sizes measured.

The figure above is what the method does at the sizes and rates that were measured. **It is not a coverage computed for this run, and none was computed.** Coverage oscillates with sample size, so a worst case at one n does not bound another.

## The record

Pre-registration hash: `1e3202a0b63093716993068cf1bb244b3249dd96a28cdba473bcfc81471fce9c`

| # | Step | Recorded at | Entry digest |
|---|---|---|---|
| 0 | plan | 2026-08-31T05:16:44Z | `617c441aa1c5dbaf` |
| 1 | sample | 2026-08-31T05:16:44Z | `5014490883c63713` |
| 2 | ingest-labels | 2026-08-31T05:16:45Z | `df504d7b5a9424df` |
| 3 | estimate | 2026-08-31T05:16:46Z | `ce397faa3b162e25` |

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

_Emitted 2026-08-31T05:16:59Z by prevalence-kit._
