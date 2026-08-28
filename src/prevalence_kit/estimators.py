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

from collections.abc import Callable
from dataclasses import dataclass
from math import exp, fsum, lgamma, log, log1p, sqrt
from statistics import NormalDist

from .canonical import JSONObject
from .errors import Reason, Refusal

DIGITS = 12
"""Decimal places carried in the record. Enough to reproduce, few enough that
platform float noise in the last bits cannot change a digest."""


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

    z = NormalDist().inv_cdf(1 - (1 - confidence) / 2)
    p = positives / n
    zsq_n = z * z / n
    denom = 1 + zsq_n
    centre = (p + zsq_n / 2) / denom
    half = (z / denom) * sqrt(p * (1 - p) / n + zsq_n / (4 * n))

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
