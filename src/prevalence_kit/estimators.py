"""Prevalence estimation.

Phase 1 ships one interval: Wilson. Phase 2 adds Clopper-Pearson.

Method anchor: Brown, L.D., Cai, T.T., DasGupta, A. (2001), "Interval Estimation
for a Binomial Proportion", Statistical Science 16(2), DOI 10.1214/ss/1009213286.
docs/STANDARDS.md S-1.1, docs/DECISIONS.md D-8.

Wald is not implemented, deliberately. At the prevalence rates this tool exists
to measure -- a fraction of a percent -- Wald's interval is wrong in the
direction that flatters the platform, and an estimator you must remember not to
use is a defect waiting for a deadline.

The normal quantile comes from `statistics.NormalDist.inv_cdf`, standard library
and documented since 3.8. That keeps SciPy out of the runtime dependency tree,
which Hard Rule 1 cares about.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from math import exp, fsum, isfinite, lgamma, log, log1p, sqrt
from statistics import NormalDist

from .canonical import JSONObject
from .errors import Reason, Refusal

DIGITS = 12
"""Decimal places carried in the record. Enough to reproduce, few enough that
platform float noise in the last bits cannot change a digest."""


def _well_formed(low: float, point: float, high: float, where: str) -> None:
    """Refuse to RETURN an interval that is not one. Checked at construction.

    **What this catches, and it is one thing.** A pair of numbers that cannot be
    an interval: not finite, out of [0, 1], the ends in the wrong order, or a
    point estimate outside its own bounds.

    **Two separate defects had this exact shape and neither was caught by the
    other's fix**, which is why it is a postcondition rather than a third
    special case:

      F-8   `wilson(5, 100, confidence=-0.5)` returned [0.066846, 0.037230]
      D2.5  `epi.prev` at Se + Sp < 1 returns lower 6.712724 above upper 6.459273

    Different causes, different modules, one failure mode: a function that
    returns an interval without checking that it is one.

    **What this does NOT catch, stated because the boundary matters.** It says
    nothing about *coverage*. Wilson covering 90.98% when it claims 95% is a
    property of the method, not a malformed value -- the interval it returns
    there is perfectly well formed and simply does not cover as often as its
    label says. No postcondition can see that; it takes a coverage computation
    over a grid of true values, which is what `r/coverage_fixtures.R` does.
    Confusing the two would make this guard look like it defends something it
    cannot.

    **It checks the values as RECORDED, at `DIGITS` places, not the raw floats.**
    That is deliberate and it was found by the guard firing on a non-defect: at
    k = 0, Wilson's lower bound computes to 4.3e-19 rather than exactly 0, so the
    point estimate 0.0 sits below its own lower bound by four parts in 10^19. In
    exact arithmetic `centre` and `half` are equal there and the bound is 0; the
    residue is float error, eighteen places below anything this project records
    or prints. Refusing on it would report a defect that no artifact can show.

    The rounded values are also the right thing to check on their own merits:
    they are what reaches the ledger and the report, and a guard on the artifact
    should read the artifact.
    """
    low, point, high = (round(v, DIGITS) for v in (low, point, high))
    for name, value in (("low", low), ("point", point), ("high", high)):
        if not isfinite(value):
            raise Refusal(
                Reason.ESTIMATE_MISMATCH,
                f"{where} produced a {name} of {value}, which is not a number.",
                "This is a defect in prevalence-kit, not in your data. Please "
                "report it with the plan and the sample size.",
            )
    if not 0.0 <= low <= high <= 1.0:
        raise Refusal(
            Reason.ESTIMATE_MISMATCH,
            f"{where} produced the bounds [{low}, {high}], which are not an "
            "interval on a proportion: a prevalence lies in [0, 1] and a lower "
            "bound cannot exceed an upper one.",
            "This is a defect in prevalence-kit, not in your data. Please "
            "report it with the plan and the sample size.",
        )
    if not low <= point <= high:
        raise Refusal(
            Reason.ESTIMATE_MISMATCH,
            f"{where} produced a point estimate of {point} outside its own "
            f"interval [{low}, {high}].",
            "This is a defect in prevalence-kit, not in your data. Please "
            "report it with the plan and the sample size.",
        )


@dataclass(frozen=True, slots=True)
class Interval:
    """A point estimate and its interval. Stored as strings; see canonical.py."""

    method: str
    point: str
    low: str
    high: str
    confidence: str
    n: int
    positives: int

    def as_record(self) -> JSONObject:
        return {
            "method": self.method,
            "point": self.point,
            "low": self.low,
            "high": self.high,
            "confidence": self.confidence,
            "n": self.n,
            "positives": self.positives,
        }


def _check_confidence(confidence: float) -> None:
    """Refuse a confidence level outside (0, 1), by name.

    F-8, found by D2.7's boundary hunt. Nothing checked this, and all three
    interval estimators took it straight into their arithmetic.

    What that produced, measured 2026-08-29:

        wilson(5, 100, confidence=1.0)    StatisticsError traceback
        wilson(5, 100, confidence=1.5)    StatisticsError traceback
        wilson(5, 100, confidence=-0.5)   [0.066846, 0.037230]  -- inverted
        clopper_pearson(5, 100, -0.5)     [0.062031, 0.042361]  -- inverted

    **The inverted pair is the serious half.** No error, no warning, an interval
    whose lower bound is above its upper and whose point estimate sits outside
    both. That is a silently wrong number, which is the one thing the charter
    says this tool must never print.

    The endpoints are excluded, not just the outside. At 1.0 the normal quantile
    is undefined and Wilson raises; at 0.0 the interval collapses to a point and
    claims nothing. Neither is a confidence level anyone can act on.

    **`PLAN_INVALID` rather than a new code, and D-22 decides it.** Count the
    artifacts an operator opens. `rogan_gladen` already refuses an out-of-range
    sensitivity or specificity with `PLAN_INVALID`, in this same module, and this
    sends the reader to the same place for the same kind of fix: one number, in
    the plan, in the wrong range.

    **Not reachable from the CLI today** -- `run.py` calls `wilson(positives, n)`
    and takes the default. It becomes reachable when D2.8 puts interval settings
    in the plan, which is why it is fixed before then rather than after.
    """
    if not 0.0 < confidence < 1.0:
        raise Refusal(
            Reason.PLAN_INVALID,
            f"Confidence is {confidence}, which is not between 0 and 1. "
            "A confidence level of exactly 0 or 1 is not a level either: at 1 the "
            "interval is undefined, and at 0 it collapses to a point and claims "
            "nothing.",
            "Set confidence to a value above 0 and below 1. The usual choice is "
            "0.95, and this project's anchors publish at that level.",
        )


def wilson(positives: int, n: int, *, confidence: float = 0.95) -> Interval:
    """Wilson score interval for a binomial proportion.

        centre = (p + z^2/2n) / (1 + z^2/n)
        half   = z/(1 + z^2/n) * sqrt( p(1-p)/n + z^2/(4n^2) )

    Correct at p = 0 and p = 1, which is why it is the default here: a
    measurement that finds no violations still has to report an upper bound.
    """
    if n <= 0:
        raise Refusal(
            Reason.EMPTY_SAMPLE,
            "No sampled items, so there is no interval to compute.",
            "Draw a sample before estimating.",
        )
    if not 0 <= positives <= n:
        raise Refusal(
            Reason.LABELS_UNMATCHED,
            f"{positives} positives out of {n} items is not possible.",
            "The labels do not line up with the sample. Re-run ingest-labels.",
        )

    _check_confidence(confidence)

    z = NormalDist().inv_cdf(1 - (1 - confidence) / 2)
    p = positives / n
    zsq_n = z * z / n
    denom = 1 + zsq_n
    centre = (p + zsq_n / 2) / denom
    half = (z / denom) * sqrt(p * (1 - p) / n + zsq_n / (4 * n))

    _well_formed(max(0.0, centre - half), positives / n, min(1.0, centre + half), "wilson")
    return Interval(
        method="wilson",
        point=_fixed(p),
        low=_fixed(max(0.0, centre - half)),
        high=_fixed(min(1.0, centre + half)),
        confidence=_fixed(confidence),
        n=n,
        positives=positives,
    )


def _fixed(x: float) -> str:
    return f"{x:.{DIGITS}f}"


def _log_pmf(n: int, i: int, p: float) -> float:
    """log P(X = i) for X ~ Binomial(n, p), via log factorials.

    `lgamma` is the log of the COMPLETE gamma function -- a factorial. It is not
    an incomplete beta, and nothing here inverts one. That distinction is the
    whole point of this module's independence from the R witness.
    """
    return lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * log(p) + (n - i) * log1p(-p)


def _sum_from(k: int, n: int, p: float, *, upward: bool) -> float:
    """Sum binomial terms outward from k until they stop mattering.

    Only terms within a few standard deviations of the mode carry any weight, so
    this is O(sqrt(n)) work rather than O(n). At Civil Comments scale --
    n = 1,999,514 -- that is a few thousand terms against two million.

    And the naive sum does not merely run slowly. `comb(4000, 2000) * p**2000`
    raises OverflowError, because the integer cannot be converted to a float.
    Working in logs removes both problems, and this docstring records that the
    first version of this function hit exactly that at n = 4000.
    """
    terms: list[float] = []
    total = 0.0
    indices = range(k, n + 1) if upward else range(k, -1, -1)
    for i in indices:
        term = exp(_log_pmf(n, i, p))
        terms.append(term)
        total += term
        # Stop once the tail is spent: a term negligible against what we already
        # have. Never on the first step, or we would stop before starting.
        if i != k and (term == 0.0 or term < 1e-22 * total):
            break
    return fsum(terms)


def _binomial_tail_at_least(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p). The definition, no special functions.

    Computed from whichever side is the SHORT tail, complemented when needed.
    Summing through the mode would cost O(n) terms and buy nothing.
    """
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    if k > (n + 1) * p:
        return _sum_from(k, n, p, upward=True)
    return 1.0 - _sum_from(k - 1, n, p, upward=False)


def _binomial_tail_at_most(k: int, n: int, p: float) -> float:
    """P(X <= k) for X ~ Binomial(n, p)."""
    if k >= n:
        return 1.0
    if k < 0:
        return 0.0
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    if k < (n + 1) * p:
        return _sum_from(k, n, p, upward=False)
    return 1.0 - _sum_from(k + 1, n, p, upward=True)


def _solve(target: float, tail: Callable[[float], float], rising: bool) -> float:
    """Bisect for the p where `tail(p) == target`. Both tails are monotone in p.

    Bisection rather than Newton on purpose. It cannot diverge, it needs no
    derivative, and an outsider can reimplement it in five lines -- which is the
    bar D-16's keyed sort was chosen to meet, applied to an interval.

    100 halvings takes the bracket below 1e-30, far under double precision, so
    this converges to the representable limit rather than to a tolerance.
    """
    low, high = 0.0, 1.0
    for _ in range(100):
        mid = (low + high) / 2
        if (tail(mid) < target) == rising:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def clopper_pearson(positives: int, n: int, *, confidence: float = 0.95) -> Interval:
    """The Clopper-Pearson exact interval, from its definition.

    The interval is DEFINED by its coverage, not by a formula:

        lower p_L solves   P(X >= k | n, p_L) = alpha/2
        upper p_U solves   P(X <= k | n, p_U) = alpha/2

    Most implementations reach the same numbers through beta quantiles, because
    the binomial tail and the incomplete beta are the same function. This one
    solves the definition directly: binomial terms in log space via `lgamma`,
    summed, and bisected. `lgamma` is the COMPLETE gamma -- a log factorial.
    There is no incomplete beta function anywhere in this package.

    That is deliberate, and it is what makes the check independent. R's
    `stats::binom.test` inverts an incomplete beta via `qbeta`; we root-find on
    the tail. Agreement between them is evidence, where two routes through the
    same beta function would only ever be evidence about the beta function.
    `r/fixtures/clopper_pearson.json`, generated before this code existed.

    Anchor: S-1.1 Brown, Cai & DasGupta (2001), DOI 10.1214/ss/1009213286, which
    is also why this ships beside Wilson rather than instead of it. Clopper-
    Pearson never under-covers and is usually wider than it needs to be; Wilson
    is the primary and this is the conservative second. D-8.

    Exact at the ends by definition rather than by special-casing: at k = 0 the
    lower bound is 0 because P(X >= 0) = 1 for every p, and at k = n the upper
    bound is 1 for the mirror reason.
    """
    if n <= 0:
        raise Refusal(
            Reason.EMPTY_SAMPLE,
            "No sampled items, so there is no interval to compute.",
            "Draw a sample before estimating.",
        )
    if not 0 <= positives <= n:
        raise Refusal(
            Reason.LABELS_UNMATCHED,
            f"{positives} positives out of {n} items is not possible.",
            "The labels do not line up with the sample. Re-run ingest-labels.",
        )
    _check_confidence(confidence)

    alpha_half = (1 - confidence) / 2

    # P(X >= k | p) rises with p, so the lower bound is where it reaches alpha/2.
    low = (
        0.0
        if positives == 0
        else _solve(alpha_half, lambda p: _binomial_tail_at_least(positives, n, p), rising=True)
    )
    # P(X <= k | p) falls with p, so the upper bound is where it drops to alpha/2.
    high = (
        1.0
        if positives == n
        else _solve(alpha_half, lambda p: _binomial_tail_at_most(positives, n, p), rising=False)
    )

    _well_formed(low, positives / n, high, "clopper_pearson")
    return Interval(
        method="clopper-pearson",
        point=_fixed(positives / n),
        low=_fixed(low),
        high=_fixed(high),
        confidence=_fixed(confidence),
        n=n,
        positives=positives,
    )


@dataclass(frozen=True, slots=True)
class Corrected:
    """A Rogan-Gladen corrected prevalence, and the apparent one it came from."""

    apparent: str
    corrected: str
    sensitivity: str
    specificity: str

    def as_record(self) -> JSONObject:
        return {
            "method": "rogan-gladen",
            "apparent": self.apparent,
            "corrected": self.corrected,
            "sensitivity": self.sensitivity,
            "specificity": self.specificity,
        }


def rogan_gladen(apparent: float, sensitivity: float, specificity: float) -> Corrected:
    """Correct an apparent prevalence for a test's known sensitivity and specificity.

        pi = (AP + Sp - 1) / (Se + Sp - 1)

    Anchor: S-1.4 Rogan & Gladen (1978), DOI 10.1093/oxfordjournals.aje.a112510.
    Interval companion: S-1.6 Reiczigel et al. (2010), which assumes Se and Sp
    are KNOWN -- our assumption, D-31. S-1.5 Lang & Reiczigel (2014) propagates
    uncertainty in *estimated* Se and Sp and is deliberately not implemented;
    adopting it would be a plan-schema change, not an estimator swap.

    Written against `r/fixtures/rogan_gladen.json`, eleven cases generated by
    `epiR::epi.prev()` 2.0.92 before this function existed. R2.2.

    **THE LIMIT THAT MATTERS MOST, and it is not a rounding detail.** The
    correction treats the Se and Sp you supply as exact. It accounts for
    sampling uncertainty and for nothing else, including any uncertainty in
    those two numbers.

    **Two refusals, and both are arithmetic rather than policy.**

    `CORRECTION_UNDEFINED` when `Se + Sp <= 1`. The denominator vanishes or
    inverts. The witness itself demonstrates why this cannot be printed: at
    Se = 0.60, Sp = 0.30, `epi.prev` returns a point estimate of 6.6 with a
    lower bound of 6.712724 ABOVE an upper bound of 6.459273. An interval whose
    lower bound exceeds its upper bound is not an interval. We are not declining
    to print a working alternative's answer -- there is nothing there to print.

    `CORRECTION_OUT_OF_RANGE` when the corrected estimate falls outside [0, 1].
    The Se/Sp pair and the sample are each individually fine and jointly
    impossible, which is D-22's fourth case and why it is a separate code from
    the one above: one sends you to two numbers in the plan, the other to the
    relationship between the plan and the data.
    """
    if not 0.0 <= apparent <= 1.0:
        raise Refusal(
            Reason.LABELS_UNMATCHED,
            f"Apparent prevalence is {apparent}, which is not a proportion.",
            "Check the labels and the sample size.",
        )
    for name, value in (("sensitivity", sensitivity), ("specificity", specificity)):
        if not 0.0 <= value <= 1.0:
            raise Refusal(
                Reason.PLAN_INVALID,
                f"The plan's {name} is {value}, which is not a proportion.",
                f"Set {name} to a value between 0 and 1.",
            )

    denominator = sensitivity + specificity - 1.0
    if denominator <= 0.0:
        raise Refusal(
            Reason.CORRECTION_UNDEFINED,
            f"Sensitivity {sensitivity} plus specificity {specificity} is "
            f"{sensitivity + specificity:.4f}, which is not above 1, so the "
            "Rogan-Gladen denominator is zero or negative. There is no corrected "
            "prevalence to report -- not one we are declining to print, but none "
            "that exists. A test in this range carries no information about which "
            "way it is wrong.",
            "Check the two numbers. A test whose sensitivity and specificity sum "
            "to 1 or less does no better than chance. If they came from a "
            "validation study, re-read it: they are often reported the other way "
            "round, and swapping them may be all that is wrong.",
        )

    corrected = (apparent + specificity - 1.0) / denominator
    if not 0.0 <= corrected <= 1.0:
        raise Refusal(
            Reason.CORRECTION_OUT_OF_RANGE,
            _out_of_range_detail(apparent, sensitivity, specificity, corrected),
            _out_of_range_fix(apparent, sensitivity, specificity),
        )

    return Corrected(
        apparent=_fixed(apparent),
        corrected=_fixed(corrected),
        sensitivity=_fixed(sensitivity),
        specificity=_fixed(specificity),
    )


def _out_of_range_detail(
    apparent: float, sensitivity: float, specificity: float, corrected: float
) -> str:
    """Say which way the plan and the sample disagree, in the operator's numbers."""
    if corrected < 0.0:
        false_positive_rate = 1.0 - specificity
        return (
            f"The corrected prevalence would be {corrected:.6f}, below zero. "
            f"You observed an apparent prevalence of {apparent:.4%}, but a "
            f"specificity of {specificity:.4%} means the test alone produces "
            f"about {false_positive_rate:.4%} positives from content that is not "
            "violating. The test would have produced more positives than you "
            "saw, so the specificity you supplied and this sample cannot both be "
            "right."
        )
    return (
        f"The corrected prevalence would be {corrected:.6f}, above one. You "
        f"observed an apparent prevalence of {apparent:.4%}, which is higher "
        f"than the sensitivity you supplied, {sensitivity:.4%}. A test cannot "
        "find a larger share of items than it is able to detect, so the "
        "sensitivity you supplied and this sample cannot both be right."
    )


def _out_of_range_fix(apparent: float, sensitivity: float, specificity: float) -> str:
    """R8 at full strength: not what broke, but which number has to change, and to what.

    The correction is defined only when `Sp >= 1 - AP` and `Se >= AP`. Both are
    stated as the threshold the operator's own figure has to clear.

    This is the message the whole `fpr_exceeds_prevalence` finding exists for. At
    rare-event prevalence an ordinary-sounding specificity makes the correction
    undefined rather than merely imprecise, and nobody who has not done the
    arithmetic expects it: 99% specificity sounds excellent and is useless at
    0.2% prevalence.
    """
    if 1.0 - specificity > apparent:
        return (
            f"An apparent prevalence of {apparent:.4%} needs a specificity above "
            f"{1.0 - apparent:.4%} for this correction to be defined. You supplied "
            f"{specificity:.4%}. At rare-event rates an ordinary-sounding "
            "specificity is not enough -- the rarer the thing you are measuring, "
            "the closer to perfect the specificity has to be. Either supply a "
            "better-characterised specificity, or report the apparent prevalence "
            "uncorrected and say so."
        )
    return (
        f"An apparent prevalence of {apparent:.4%} needs a sensitivity of at "
        f"least {apparent:.4%} for this correction to be defined. You supplied "
        f"{sensitivity:.4%}. Either the sensitivity is understated or the sample "
        "is not from the population it was meant to describe."
    )


CORRECTABLE_INTERVALS = frozenset({"clopper_pearson"})
"""Interval methods the Rogan-Gladen correction may be built on.

**One entry, and the reason it is a set rather than a constant is Q7.** The
fixture witnesses `epi.prev(..., method = "c-p")` and nothing else, so a
Wilson-transformed corrected interval has no pre-existing expected value --
which R2.2 forbids shipping, inside the phase whose whole shape is R2.2.

`wilson` is a real interval this package computes and is deliberately absent
here. That is why `KNOWN_INTERVALS` exists separately: an operator who asks for
Wilson has not made a typo, and the refusal must not tell them they have.
"""

KNOWN_INTERVALS = frozenset({"wilson", "clopper_pearson"})
"""Every interval this package computes, correctable or not. See above."""


@dataclass(frozen=True, slots=True)
class CorrectedInterval:
    """A Rogan-Gladen corrected prevalence with its interval, and what we did to it.

    **`low` / `high` are what an operator reads. `low_raw` / `high_raw` are what
    the arithmetic produced.** They differ only when a bound was clamped, and
    `clamped` names which ends. All four reach the record, so `verify` re-derives
    both and an auditor can see the interval before policy touched it. D-32.
    """

    method: str
    point: str
    low: str
    high: str
    low_raw: str
    high_raw: str
    clamped: tuple[str, ...]
    apparent: Interval
    sensitivity: str
    specificity: str
    confidence: str
    n: int
    positives: int

    @property
    def note(self) -> str:
        """The disclosure, in the operator's numbers. Empty when nothing was clamped.

        **It is produced here, not by the renderer.** A bound that was changed has
        to explain itself in the same place the change happened, or the sentence
        drifts from the arithmetic the first time someone edits the report.
        """
        if not self.clamped:
            return ""
        parts = []
        if "low" in self.clamped:
            parts.append(f"lower bound clamped to 0 from {self.low_raw}")
        if "high" in self.clamped:
            parts.append(f"upper bound clamped to 1 from {self.high_raw}")
        return (
            f"Interval {'; '.join(parts)}. A prevalence cannot lie outside [0, 1], so the "
            "clamped interval covers everything the raw one covered and is very slightly "
            "conservative. The raw bounds are in the record. That end of the interval is a "
            "construction, not a measurement."
        )

    def as_record(self) -> JSONObject:
        return {
            "method": self.method,
            "point": self.point,
            "low": self.low,
            "high": self.high,
            "low_raw": self.low_raw,
            "high_raw": self.high_raw,
            "clamped": list(self.clamped),
            "apparent": self.apparent.as_record(),
            "sensitivity": self.sensitivity,
            "specificity": self.specificity,
            "confidence": self.confidence,
            "n": self.n,
            "positives": self.positives,
        }


def rogan_gladen_interval(
    positives: int,
    n: int,
    sensitivity: float,
    specificity: float,
    *,
    interval_method: str,
    confidence: float = 0.95,
) -> CorrectedInterval:
    """A confidence interval for the Rogan-Gladen corrected prevalence.

    **The construction, and it is the witness's construction rather than ours.**
    Build the interval for the *apparent* prevalence, then push both endpoints
    through the same correction the point estimate uses:

        low  = RG(apparent_low)      high = RG(apparent_high)

    Anchor: **S-1.6 Reiczigel, Foldi & Ozsvari (2010)**, which assumes Se and Sp
    are **known** -- our assumption, D-31. **Not S-1.5 Lang & Reiczigel (2014)**,
    which propagates uncertainty in *estimated* Se and Sp; adopting it would be a
    plan-schema change, not an estimator swap.

    **Why the endpoints may simply be transformed.** With `Se + Sp > 1` the
    denominator is positive, so `RG` is strictly increasing in the apparent
    prevalence. A monotone increasing map carries an interval to an interval and
    keeps the order of its ends, so no sorting is needed and none is done. The
    case where it would not hold -- `Se + Sp <= 1` -- never reaches here, because
    `rogan_gladen()` refuses it first. Asserted, not assumed:
    `test_the_transform_is_monotone_so_the_ends_keep_their_order`.

    **This composes two things already witnessed separately** and introduces no
    third unwitnessed one: `clopper_pearson()`, agreeing with base R's
    `stats::binom.test` to 8.4e-11 across 69 cases -- n from 1 to 1,999,514 and
    confidence in {0.90, 0.95, 0.99} (S-2.4) -- and `rogan_gladen()`,
    checked against all eleven `epiR` cases. Measured across the nine
    positive-denominator fixture rows, `RG(ap_lower) == tp_lower` and
    `RG(ap_upper) == tp_upper` to every digit `epiR` printed.

    **Stated at its own width:** endpoint transformation is what the witness
    does. That is an observation about `epi.prev`, not a theorem about corrected
    intervals in general.

    **Bounds outside [0, 1] are clamped, and the clamp is disclosed.** Q6 / D-32.
    A corrected *point* estimate outside [0, 1] is a refusal and always was; a
    corrected *bound* outside it is not, because the point estimate can be
    perfectly good while an end runs past the edge -- which is exactly the
    rare-event case this tool exists for. At `pos = 8, n = 4000, Se = 0.90,
    Sp = 0.999` the witness returns a lower bound of `-0.000151` beside a point
    estimate of `0.001112`. Refusing there would refuse the tool's own use case;
    printing a negative prevalence costs an auditor's trust in every number
    beside it. So it is clamped, `note` says so, and `low_raw` keeps the
    arithmetic.

    **`interval_method` is required and has no default.** Q7 / D-33: a plan that
    pre-registers Wilson and supplies Se/Sp is a plan this version cannot honour,
    and the one thing it must never do is quietly hand back a different method
    than the operator committed to. Defaulting the argument here would put that
    substitution back in as a constant in the source. **D-30 condition 1's shape,
    applied to a second commitment.**
    """
    if interval_method not in KNOWN_INTERVALS:
        raise Refusal(
            Reason.PLAN_INVALID,
            f"{interval_method!r} is not an interval this tool computes.",
            f"Use one of: {', '.join(sorted(KNOWN_INTERVALS))}.",
        )
    if interval_method not in CORRECTABLE_INTERVALS:
        raise Refusal(
            Reason.CORRECTION_INTERVAL_UNSUPPORTED,
            f"This plan pre-registers the {interval_method} interval and also supplies "
            "a sensitivity and specificity. This version can only build the "
            "Rogan-Gladen correction on a Clopper-Pearson interval, because that is "
            "the only one an outside witness gave us expected values for -- epiR "
            "2.0.92 builds its corrected interval from Clopper-Pearson, and we have "
            f"no witnessed expected value for a {interval_method}-based one. "
            "Quietly giving you a Clopper-Pearson interval instead would hand you a "
            "number your plan did not commit to, which is the one thing "
            "pre-registration exists to stop.\n"
            "\n"
            "  Since you are here, the choice is worth making on its merits rather "
            "than on habit. Wilson is the familiar one and it is a good interval, "
            "but it does not guarantee its stated level. At rare-event rates -- a "
            "true rate a few times 1/n, which is what this tool is usually pointed "
            "at -- a 95% Wilson interval covers AS LITTLE AS 90.98% of the time, and a "
            "90% one as little as 85.32%. Those are the worst values found on a "
            "grid, so the real worst is at most that and may be lower. "
            "Clopper-Pearson never covers less than the "
            "level you asked for. It pays for that by being wider.\n"
            "\n"
            "  So this is not a formality. If you are measuring something rare and "
            "you need the number to mean what it says, Clopper-Pearson is the one "
            "that does. If you would rather have a tighter interval and can live "
            "with the level being approximate, Wilson is a defensible choice -- "
            "just not one this version can correct for test error. Measured, not "
            "asserted: r/fixtures/coverage.json, checked against the published "
            "limits in Brown, Cai & DasGupta (2001).",
            "Pick one and put it in the plan. Either set "
            "`interval: clopper_pearson` and keep the correction, or remove "
            "`sensitivity` and `specificity` and report an uncorrected "
            f"{interval_method} interval. Both are honest. The plan has to say "
            "which, because it is hashed before any data is touched and that is "
            "what makes it a commitment.",
        )

    apparent = clopper_pearson(positives, n, confidence=confidence)

    # The point estimate first: it owns both correction refusals, so an undefined
    # or out-of-range correction fails here exactly as it does without an
    # interval. One authority for the refusals, not two that can disagree.
    point = rogan_gladen(positives / n, sensitivity, specificity)

    denominator = sensitivity + specificity - 1.0
    low_raw = (float(apparent.low) + specificity - 1.0) / denominator
    high_raw = (float(apparent.high) + specificity - 1.0) / denominator

    clamped: list[str] = []
    low, high = low_raw, high_raw
    if low < 0.0:
        low = 0.0
        clamped.append("low")
    if high > 1.0:
        high = 1.0
        clamped.append("high")

    # The clamped pair is what an operator reads, so that is what is checked.
    # The raw pair is deliberately NOT checked: it is allowed outside [0, 1] --
    # that is the whole of Q6, and the raw bound is kept precisely so an auditor
    # can see what the arithmetic produced before policy touched it.
    _well_formed(low, float(point.corrected), high, "rogan_gladen_interval")
    return CorrectedInterval(
        method="rogan-gladen/clopper-pearson",
        point=point.corrected,
        low=_fixed(low),
        high=_fixed(high),
        low_raw=_fixed(low_raw),
        high_raw=_fixed(high_raw),
        clamped=tuple(clamped),
        apparent=apparent,
        sensitivity=_fixed(sensitivity),
        specificity=_fixed(specificity),
        confidence=_fixed(confidence),
        n=n,
        positives=positives,
    )


# ===================================================================== design
#
# **Design-based intervals. A separate family, and the separation is the point.**
#
# A binomial interval inverts a distribution over `(k, n)` -- the count observed
# out of the units drawn. A design-based interval replaces `n` with `n_eff`, the
# sample size a simple random sample would have needed to reach this design's
# precision. Under stratification the pooled `k/n` is not even the design
# estimate -- 0.020000 against 0.011333 on the `rare` fixture -- so these are
# intervals for **different quantities** and Q15 gave them different names.
#
# **THE INCOMPLETE BETA LIVES HERE AND NOWHERE ELSE.**
#
# `docs/STANDARDS.md` S-2.4 used to say there was no incomplete beta anywhere in
# this package, which made D2.4's independence from base R's `qbeta` structural
# rather than careful. That sentence was true and is now narrower: the beta is
# below, the **binomial** Clopper-Pearson still root-finds on the tail and cannot
# reach it, and `test_the_binomial_path_cannot_reach_the_incomplete_beta`
# asserts that statically. Structure replaced, not removed -- the director's
# condition on the narrowing.
#
# It is written rather than imported, so the comparison against `svy` on this
# path is also two independent implementations. Agreement: 2.6e-14.


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta. Lentz's algorithm."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        step = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + step * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + step / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        step = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + step * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + step / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return h


def regularised_beta(a: float, b: float, x: float) -> float:
    """`I_x(a, b)`. The only incomplete beta in this package -- S-2.4."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * log(x) + b * log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def _beta_quantile(q: float, a: float, b: float) -> float:
    """Inverse of `regularised_beta`, by bisection. Monotone, so bisection is safe."""
    if q <= 0.0:
        return 0.0
    if q >= 1.0:
        return 1.0
    low, high = 0.0, 1.0
    for _ in range(80):
        mid = (low + high) / 2.0
        if regularised_beta(a, b, mid) < q:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def _t_quantile(q: float, degrees_of_freedom: float) -> float:
    """Student's t quantile, from the same incomplete beta.

    One primitive serves both intervals: the t distribution's CDF is an
    incomplete beta, so adding the beta added this rather than a second special
    function.
    """
    if q == 0.5:
        return 0.0
    tail = 2.0 * min(q, 1.0 - q)
    x = _beta_quantile(tail, degrees_of_freedom / 2.0, 0.5)
    value = sqrt(degrees_of_freedom * (1.0 - x) / x)
    return value if q > 0.5 else -value


def effective_n(
    point: float, standard_error: float, degrees_of_freedom: int, n: int, confidence: float
) -> float:
    """`n_eff`, with Korn-Graubard's degrees-of-freedom adjustment.

        n_eff = p(1 - p) / se^2,  scaled by (t_{n-1} / t_df)^2

    **The adjustment is the part that is easy to miss**, and missing it is what
    the first implementation did: it agreed with `svy` only to 5e-04, which is
    inside "looks right" and outside R2.3. Korn & Graubard (1998) eq 2.1 and 2.2.

    `n` is the **nominal** sample size, not `n_eff`. The fixture records it for
    that reason -- a fixture that omits what the estimator needs is a fixture the
    estimator fills in from a guess.
    """
    if standard_error <= 0.0:
        raise Refusal(
            Reason.INTERVAL_UNDEFINED,
            "Every sampled unit in every stratum carries the same label, so the "
            "design standard error is zero and there is no spread to build an "
            "interval from.",
            "The point estimate stands and the sample sizes stand; the interval "
            "does not exist for this sample. At rare rates this is the most "
            "likely single outcome rather than an edge case -- `plan` reports the "
            "chance of it before any labelling is paid for. Report the point "
            "estimate and say the interval was undefined.",
        )
    n_eff = point * (1.0 - point) / (standard_error * standard_error)
    if degrees_of_freedom > 0 and n > 1:
        q = 1.0 - (1.0 - confidence) / 2.0
        n_eff *= (_t_quantile(q, float(n - 1)) / _t_quantile(q, float(degrees_of_freedom))) ** 2
    return n_eff


def design_wilson(
    point: float,
    standard_error: float,
    degrees_of_freedom: int,
    n: int,
    *,
    confidence: float = 0.95,
) -> Interval:
    """Wilson's score interval on the effective sample size, with a t quantile.

    **Witnessed by `svy` 0.25.0 `ci_method="wilson"`**, generated before this
    function existed -- `svy/fixtures/design_intervals.json`, commit `e04a7aa`.
    Worst endpoint disagreement **4.2e-14**.

    **Its coverage is poor at rare rates and that is disclosed, not hidden.**
    Worst conditional coverage measured **0.00000** against a nominal 0.90 at
    `wide`, p = 0.001. Charter section 8 carries the figures.
    """
    _check_confidence(confidence)
    n_eff = effective_n(point, standard_error, degrees_of_freedom, n, confidence)
    t = _t_quantile(1.0 - (1.0 - confidence) / 2.0, float(degrees_of_freedom))
    t2 = t * t
    denominator = 1.0 + t2 / n_eff
    centre = (point + t2 / (2.0 * n_eff)) / denominator
    half = (t / denominator) * sqrt(point * (1.0 - point) / n_eff + t2 / (4.0 * n_eff * n_eff))
    return Interval(
        method="design-wilson",
        point=_fixed(point),
        low=_fixed(max(0.0, centre - half)),
        high=_fixed(min(1.0, centre + half)),
        confidence=_fixed(confidence),
        n=n,
        positives=round(point * n),
    )


def design_korn_graubard(
    point: float,
    standard_error: float,
    degrees_of_freedom: int,
    n: int,
    *,
    confidence: float = 0.95,
) -> Interval:
    """Korn-Graubard: the Clopper-Pearson construction on an effective sample size.

    **Named for the method and not for Clopper-Pearson, deliberately.** The draft
    of A-5 called it `design_clopper_pearson`, and the name would have promised
    the one property Clopper-Pearson is chosen for: coverage at or above nominal.
    **It does not hold it.** Measured worst conditional coverage **0.74720**
    against a nominal 0.90 at `rare`, p = 0.01 -- and **0.90033** against 0.95 at
    `rare`, p = 0.02, where the interval is defined 99.8% of the time, so it is
    not a boundary artifact. Clopper-Pearson's guarantee is a property of the
    **exact binomial** construction, and an approximation on `n_eff` inherits
    nothing from it.

    **It is still the better of the two**, which is why it ships: closer to
    nominal at every level and at 32 of 32 points at nominal 0.95.

    **Witnessed by `svy` 0.25.0 `ci_method="beta"`**, generated first. Worst
    endpoint disagreement **2.6e-14**.
    """
    _check_confidence(confidence)
    n_eff = effective_n(point, standard_error, degrees_of_freedom, n, confidence)
    successes = n_eff * point
    alpha = 1.0 - confidence
    low = (
        0.0 if successes <= 0.0 else _beta_quantile(alpha / 2.0, successes, n_eff - successes + 1.0)
    )
    high = (
        1.0
        if point >= 1.0
        else _beta_quantile(1.0 - alpha / 2.0, successes + 1.0, n_eff - successes)
    )
    return Interval(
        method="design-korn-graubard",
        point=_fixed(point),
        low=_fixed(max(0.0, low)),
        high=_fixed(min(1.0, high)),
        confidence=_fixed(confidence),
        n=n,
        positives=round(point * n),
    )


def probability_no_interval(rates: Sequence[float], allocation: Sequence[int]) -> float:
    """The chance this design produces **no interval at all**, in closed form.

        P = product over strata of (1 - p_h) ** n_h

    Every sampled unit comes back negative, the design standard error is zero,
    and there is nothing to build an interval from. At rare rates this is not an
    edge case: **87.8%** at the `two_stratum` fixture with p = 0.001, **74.1%**
    at `rare`.

    **The plan already carries everything this needs** -- `expected_rate` per
    stratum and the allocation -- so it is computable **before any data is
    touched**, which is Q2's reason: tell the operator before the label budget is
    spent.

    **A field justified for one purpose earning a second.** `expected_rate` was
    added for Neyman allocation and documented as a prior that costs efficiency
    and never validity. It turns out to also predict whether the run will produce
    an interval at all. Recorded because that is worth noticing.
    """
    probability = 1.0
    for rate, drawn in zip(rates, allocation, strict=True):
        probability *= (1.0 - rate) ** drawn
    return probability
